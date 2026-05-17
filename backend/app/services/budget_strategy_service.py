from datetime import date
import json

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.strategy import (
    BudgetAssumptions,
    BudgetInfo,
    BudgetStrategyListItem,
    BudgetStrategyRequest,
    BudgetStrategyResponse,
    ExpectedEffect,
    StrategyInfo,
)
from app.services.budget_allocation_service import allocate_budget
from app.services.budget_effect_service import total_effect
from app.services.channel_analysis_service import build_summary
from app.services.country_metrics_service import get_metrics
from app.services.country_query_service import get_country, validate_period
from app.services.opportunity_scoring_service import get_score
from app.services.strategy_narrative_service import confidence_score, recommendation_list, risk_list, strategy_type, summary_text
from app.services.summary_generation_service import create_budget_summary


def json_text(value: object) -> str:
    """Convert value to JSON text.
    Args:
        value (object): Source value."""
    return json.dumps(value)


def opportunity_id(
    session: Session,
    country_id: int,
    date_from: date,
    date_to: date,
    calculation_version: str,
) -> int | None:
    """Get opportunity identifier.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        calculation_version (str): Calculation version."""
    result = session.execute(
        text(
            """
            SELECT opportunity_score_id
            FROM country_opportunity_scores
            WHERE country_id = :country_id
              AND period_start = :date_from
              AND period_end = :date_to
              AND calculation_version = :calculation_version
            """,
        ),
        {
            'country_id': country_id,
            'date_from': date_from,
            'date_to': date_to,
            'calculation_version': calculation_version,
        },
    )
    value = result.scalar_one_or_none()
    return None if value is None else int(value)


def safe_channel(
    session: Session,
    country_id: int,
    date_from: date,
    date_to: date,
    calculation_version: str,
) -> object | None:
    """Build safe channel summary.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        calculation_version (str): Calculation version."""
    try:
        summary = build_summary(session, country_id, None, date_from, date_to, calculation_version)
    except HTTPException:
        summary = None
    return summary


def available_traffic(metrics: object) -> float:
    """Calculate available traffic.
    Args:
        metrics (object): Country metrics."""
    total_traffic = metrics.total_competitor_traffic or 0
    no_bounce_share = metrics.no_bounce_share if metrics.no_bounce_share is not None else 0.5
    traffic = total_traffic * no_bounce_share
    return traffic


def save_strategy(
    session: Session,
    request: BudgetStrategyRequest,
    country: dict[str, object],
    strategy_name: str,
    confidence: float,
    summary: str,
    recommendations: list[str],
    risks: list[str],
    expected: dict[str, float],
    opportunity_score_id: int | None,
    data_quality_status: str,
) -> int:
    """Save strategy run.
    Args:
        session (Session): Database session.
        request (BudgetStrategyRequest): Strategy request.
        country (dict[str, object]): Country data.
        strategy_name (str): Strategy type.
        confidence (float): Confidence score.
        summary (str): Strategy summary.
        recommendations (list[str]): Recommendations.
        risks (list[str]): Risks.
        expected (dict[str, float]): Expected effect.
        opportunity_score_id (int | None): Opportunity score identifier.
        data_quality_status (str): Data quality status."""
    result = session.execute(
        text(
            """
            INSERT INTO budget_strategy_runs (
                country_id, region_id, period_start, period_end, budget_amount, currency_code,
                campaign_goal, risk_appetite, opportunity_score_id, strategy_status, recommended_strategy_type,
                total_expected_traffic, total_expected_leads, total_expected_clients, confidence_score, summary,
                recommendations, risks, assumptions, input_params, calculation_version, data_quality_status
            )
            VALUES (
                :country_id, :region_id, :period_start, :period_end, :budget_amount, :currency_code,
                :campaign_goal, :risk_appetite, :opportunity_score_id, 'generated', :recommended_strategy_type,
                :total_expected_traffic, :total_expected_leads, :total_expected_clients, :confidence_score, :summary,
                CAST(:recommendations AS jsonb), CAST(:risks AS jsonb), CAST(:assumptions AS jsonb),
                CAST(:input_params AS jsonb), :calculation_version, :data_quality_status
            )
            RETURNING strategy_id
            """,
        ),
        {
            'country_id': request.country_id,
            'region_id': country.get('region_id'),
            'period_start': request.date_from,
            'period_end': request.date_to,
            'budget_amount': request.budget_amount,
            'currency_code': request.currency_code[:3].upper(),
            'campaign_goal': request.campaign_goal,
            'risk_appetite': request.risk_appetite,
            'opportunity_score_id': opportunity_score_id,
            'recommended_strategy_type': strategy_name,
            'total_expected_traffic': expected['expected_traffic'],
            'total_expected_leads': expected['expected_leads'],
            'total_expected_clients': expected['expected_clients'],
            'confidence_score': confidence,
            'summary': summary,
            'recommendations': json_text(recommendations),
            'risks': json_text(risks),
            'assumptions': json_text((request.assumptions or BudgetAssumptions()).model_dump()),
            'input_params': json_text(request.model_dump(mode='json')),
            'calculation_version': request.calculation_version,
            'data_quality_status': data_quality_status,
        },
    )
    strategy_id = int(result.scalar_one())
    return strategy_id


def save_allocations(session: Session, strategy_id: int, allocation: list[object]) -> int:
    """Save allocation rows.
    Args:
        session (Session): Database session.
        strategy_id (int): Strategy identifier.
        allocation (list[object]): Allocation items."""
    count = 0
    for item in allocation:
        session.execute(
            text(
                """
                INSERT INTO budget_strategy_allocations (
                    strategy_id, channel_id, channel_code, channel_name, budget_amount, budget_share,
                    rationale, expected_traffic, expected_leads, expected_clients, priority, risk_level,
                    test_hypothesis, success_metric
                )
                VALUES (
                    :strategy_id, :channel_id, :channel_code, :channel_name, :budget_amount, :budget_share,
                    :rationale, :expected_traffic, :expected_leads, :expected_clients, :priority, :risk_level,
                    :test_hypothesis, :success_metric
                )
                """,
            ),
            {'strategy_id': strategy_id, **item.model_dump()},
        )
        count += 1
    session.commit()
    return count


def generate_strategy(session: Session, request: BudgetStrategyRequest) -> BudgetStrategyResponse:
    """Generate budget strategy.
    Args:
        session (Session): Database session.
        request (BudgetStrategyRequest): Strategy request."""
    country = get_country(session, request.country_id)
    if country is None:
        raise HTTPException(status_code=404, detail='Country not found.')
    period_error = validate_period(session, request.country_id, request.date_from, request.date_to)
    if period_error:
        raise HTTPException(status_code=400, detail=period_error)
    assumptions = request.assumptions or BudgetAssumptions()
    opportunity = get_score(
        session,
        request.country_id,
        request.date_from,
        request.date_to,
        request.calculation_version,
        True,
        False,
    )
    metrics = get_metrics(
        session,
        request.country_id,
        request.date_from,
        request.date_to,
        request.calculation_version,
        True,
    )
    channel_summary = safe_channel(session, request.country_id, request.date_from, request.date_to, request.calculation_version)
    allocation = allocate_budget(
        request.budget_amount,
        request.campaign_goal,
        request.risk_appetite,
        assumptions,
        opportunity,
        channel_summary,
        available_traffic(metrics.metrics),
    )
    expected = total_effect(allocation)
    strategy_name = strategy_type(request.campaign_goal, opportunity)
    confidence = confidence_score(opportunity, channel_summary is not None, request.assumptions is None)
    summary = summary_text(country['country_name_en'], strategy_name, allocation)
    recommendations = recommendation_list(opportunity, allocation)
    risks = risk_list(opportunity, request.budget_amount, channel_summary is not None and channel_summary.scope.is_estimated)
    strategy_id = save_strategy(
        session,
        request,
        country,
        strategy_name,
        confidence,
        summary,
        recommendations,
        risks,
        expected,
        opportunity_id(session, request.country_id, request.date_from, request.date_to, request.calculation_version),
        opportunity.data_quality_status,
    )
    save_allocations(session, strategy_id, allocation)
    create_budget_summary(session, strategy_id)
    response = BudgetStrategyResponse(
        strategy_id=strategy_id,
        country=country,
        period={'date_from': request.date_from, 'date_to': request.date_to, 'days_count': (request.date_to - request.date_from).days + 1},
        budget=BudgetInfo(amount=request.budget_amount, currency_code=request.currency_code[:3].upper()),
        strategy=StrategyInfo(recommended_strategy_type=strategy_name, confidence_score=confidence, summary=summary),
        allocation=allocation,
        expected_effect=ExpectedEffect(**expected),
        risks=risks,
        recommendations=recommendations,
        assumptions=assumptions,
        data_quality_status=opportunity.data_quality_status,
    )
    return response


def get_strategy(session: Session, strategy_id: int) -> BudgetStrategyResponse:
    """Get strategy.
    Args:
        session (Session): Database session.
        strategy_id (int): Strategy identifier."""
    result = session.execute(
        text(
            """
            SELECT
                runs.*,
                country.country_name_en,
                country.country_name_ru,
                region.region_name AS region_name_en,
                region.region_name AS region_name_ru
            FROM budget_strategy_runs AS runs
            JOIN dim_country AS country ON country.country_id = runs.country_id
            LEFT JOIN dim_region AS region ON region.region_id = country.region_id
            WHERE runs.strategy_id = :strategy_id
            """,
        ),
        {'strategy_id': strategy_id},
    )
    row = result.first()
    if row is None:
        raise HTTPException(status_code=404, detail='Strategy not found.')
    row_data = dict(row._mapping)
    allocation = strategy_allocations(session, strategy_id)
    response = BudgetStrategyResponse(
        strategy_id=strategy_id,
        country={
            'country_id': row_data['country_id'],
            'country_name_en': row_data['country_name_en'],
            'country_name_ru': row_data.get('country_name_ru'),
            'region_name_en': row_data.get('region_name_en'),
            'region_name_ru': row_data.get('region_name_ru'),
            'has_data': True,
        },
        period={'date_from': row_data['period_start'], 'date_to': row_data['period_end'], 'days_count': (row_data['period_end'] - row_data['period_start']).days + 1},
        budget=BudgetInfo(amount=float(row_data['budget_amount']), currency_code=row_data['currency_code']),
        strategy=StrategyInfo(
            recommended_strategy_type=row_data.get('recommended_strategy_type') or 'unknown',
            confidence_score=float(row_data.get('confidence_score') or 0),
            summary=row_data.get('summary') or '',
        ),
        allocation=allocation,
        expected_effect=ExpectedEffect(
            expected_traffic=float(row_data.get('total_expected_traffic') or 0),
            expected_leads=float(row_data.get('total_expected_leads') or 0),
            expected_clients=float(row_data.get('total_expected_clients') or 0),
        ),
        risks=row_data.get('risks') or [],
        recommendations=row_data.get('recommendations') or [],
        assumptions=BudgetAssumptions(**(row_data.get('assumptions') or {})),
        data_quality_status=row_data.get('data_quality_status'),
    )
    return response


def strategy_allocations(session: Session, strategy_id: int) -> list[object]:
    """Get strategy allocations.
    Args:
        session (Session): Database session.
        strategy_id (int): Strategy identifier."""
    from app.schemas.strategy import BudgetAllocationItem

    result = session.execute(
        text(
            """
            SELECT *
            FROM budget_strategy_allocations
            WHERE strategy_id = :strategy_id
            ORDER BY budget_share DESC NULLS LAST
            """,
        ),
        {'strategy_id': strategy_id},
    )
    rows = [BudgetAllocationItem(**dict(row._mapping)) for row in result]
    return rows


def list_strategies(
    session: Session,
    country_id: int | None,
    date_from: date | None,
    date_to: date | None,
    campaign_goal: str | None,
    limit: int,
    offset: int,
) -> dict[str, object]:
    """List strategies.
    Args:
        session (Session): Database session.
        country_id (int | None): Country identifier.
        date_from (date | None): Period start date.
        date_to (date | None): Period end date.
        campaign_goal (str | None): Campaign goal.
        limit (int): Result limit.
        offset (int): Result offset."""
    filters = ["runs.strategy_status != 'archived'"]
    params: dict[str, object] = {'limit': limit, 'offset': offset}
    if country_id is not None:
        filters.append('runs.country_id = :country_id')
        params['country_id'] = country_id
    if date_from is not None:
        filters.append('runs.period_start >= :date_from')
        params['date_from'] = date_from
    if date_to is not None:
        filters.append('runs.period_end <= :date_to')
        params['date_to'] = date_to
    if campaign_goal:
        filters.append('runs.campaign_goal = :campaign_goal')
        params['campaign_goal'] = campaign_goal
    where_clause = ' AND '.join(filters)
    result = session.execute(
        text(
            f"""
            SELECT
                runs.strategy_id,
                runs.country_id,
                country.country_name_en,
                runs.period_start,
                runs.period_end,
                runs.budget_amount,
                runs.currency_code,
                runs.campaign_goal,
                runs.strategy_status,
                runs.recommended_strategy_type,
                runs.total_expected_traffic,
                runs.confidence_score,
                runs.created_at::text AS created_at,
                COUNT(*) OVER() AS total
            FROM budget_strategy_runs AS runs
            JOIN dim_country AS country ON country.country_id = runs.country_id
            WHERE {where_clause}
            ORDER BY runs.created_at DESC
            LIMIT :limit OFFSET :offset
            """,
        ),
        params,
    )
    rows = [dict(row._mapping) for row in result]
    total = int(rows[0]['total']) if rows else 0
    items = [BudgetStrategyListItem(**{key: value for key, value in row.items() if key != 'total'}) for row in rows]
    return {'items': items, 'total': total}


def archive_strategy(session: Session, strategy_id: int) -> BudgetStrategyResponse:
    """Archive strategy.
    Args:
        session (Session): Database session.
        strategy_id (int): Strategy identifier."""
    session.execute(
        text(
            """
            UPDATE budget_strategy_runs
            SET strategy_status = 'archived', updated_at = now()
            WHERE strategy_id = :strategy_id
            """,
        ),
        {'strategy_id': strategy_id},
    )
    session.commit()
    return get_strategy(session, strategy_id)
