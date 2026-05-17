from datetime import date
import json

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.opportunity import (
    OpportunityCalculation,
    OpportunityComponents,
    OpportunityCountryItem,
    OpportunityScoreResponse,
    OpportunityScoreValues,
)
from app.services.channel_analysis_service import build_summary
from app.services.country_metrics_service import get_metrics
from app.services.country_query_service import float_value, get_country, period_quality
from app.services.opportunity_component_service import (
    channel_score,
    competition_score,
    difficulty_score,
    localization_score,
    quality_score,
    traffic_score,
    volatility_score,
    weighted_score,
)
from app.services.opportunity_narrative_service import explain_score, market_type, priority_label, risk_list, strength_list


def quality_status(session: Session, country_id: int, date_from: date, date_to: date) -> str:
    """Get quality status.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date."""
    status = period_quality(session, country_id, date_from, date_to)
    if status == 'failed':
        raise HTTPException(
            status_code=409,
            detail='Opportunity score cannot be calculated because the dataset has failed quality checks.',
        )
    return status


def region_id(country: dict[str, object]) -> int | None:
    """Get region identifier.
    Args:
        country (dict[str, object]): Country data."""
    value = country.get('region_id')
    identifier = None if value is None else int(value)
    return identifier


def country_data(session: Session, country_id: int) -> dict[str, object]:
    """Get country data.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier."""
    result = session.execute(
        text(
            """
            SELECT
                country.country_id,
                country.country_name_en,
                country.country_name_ru,
                country.region_id,
                region.region_name AS region_name_en,
                region.region_name AS region_name_ru,
                TRUE AS has_data
            FROM dim_country AS country
            LEFT JOIN dim_region AS region ON region.region_id = country.region_id
            WHERE country.country_id = :country_id
            """,
        ),
        {'country_id': country_id},
    )
    row = result.first()
    if row is None:
        raise HTTPException(status_code=404, detail='Country not found.')
    country = dict(row._mapping)
    return country


def paid_share(channel_summary: object | None) -> float | None:
    """Get paid share.
    Args:
        channel_summary (object | None): Channel summary."""
    if channel_summary is None:
        return None
    metric = next((channel for channel in channel_summary.channels if channel.channel_code == 'paid'), None)
    share = metric.traffic_share if metric else None
    return share


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


def traffic_percentile(
    session: Session,
    country_id: int,
    date_from: date,
    date_to: date,
) -> float:
    """Calculate traffic percentile.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date."""
    result = session.execute(
        text(
            """
            SELECT country_id, SUM(traffic) AS total_traffic
            FROM fact_domain_country_daily
            WHERE date BETWEEN :date_from AND :date_to
            GROUP BY country_id
            ORDER BY SUM(traffic), country_id
            """,
        ),
        {'date_from': date_from, 'date_to': date_to},
    )
    rows = [dict(row._mapping) for row in result]
    if len(rows) <= 1:
        return 1.0
    country_index = next((index for index, row in enumerate(rows) if int(row['country_id']) == country_id), 0)
    percentile = country_index / (len(rows) - 1)
    return percentile


def build_components(
    metrics: object,
    channel_summary: object | None,
    traffic_rank: float,
) -> OpportunityComponents:
    """Build score components.
    Args:
        metrics (object): Country metric values.
        channel_summary (object | None): Channel summary.
        traffic_rank (float): Country traffic percentile."""
    traffic_component = traffic_score(metrics, traffic_rank)
    components = OpportunityComponents(
        traffic_score=traffic_component,
        competition_score=competition_score(metrics),
        quality_score=quality_score(metrics),
        channel_gap_score=channel_score(channel_summary, traffic_component),
        volatility_score=volatility_score(metrics),
        localization_potential_score=localization_score(metrics, traffic_rank),
        entry_difficulty_score=difficulty_score(metrics, channel_summary),
    )
    return components


def final_score(components: OpportunityComponents) -> float:
    """Calculate final score.
    Args:
        components (OpportunityComponents): Score components."""
    score = weighted_score(
        components.traffic_score or 0,
        components.competition_score or 0,
        components.quality_score or 0,
        components.channel_gap_score,
        components.volatility_score or 0,
        components.localization_potential_score or 0,
        components.entry_difficulty_score or 0,
    )
    return score


def save_score(
    session: Session,
    country: dict[str, object],
    date_from: date,
    date_to: date,
    score: float,
    priority: str,
    market: str,
    components: OpportunityComponents,
    strengths: list[str],
    risks: list[str],
    explanation: str,
    data_quality_status: str,
    calculation_version: str,
) -> str | None:
    """Save opportunity score.
    Args:
        session (Session): Database session.
        country (dict[str, object]): Country data.
        date_from (date): Period start date.
        date_to (date): Period end date.
        score (float): Opportunity score.
        priority (str): Recommended priority.
        market (str): Market type.
        components (OpportunityComponents): Score components.
        strengths (list[str]): Strength list.
        risks (list[str]): Risk list.
        explanation (str): Explanation text.
        data_quality_status (str): Data quality status.
        calculation_version (str): Calculation version."""
    breakdown = components.model_dump()
    result = session.execute(
        text(
            """
            INSERT INTO country_opportunity_scores (
                country_id, region_id, period_start, period_end, opportunity_score,
                traffic_score, competition_score, quality_score, channel_gap_score, volatility_score,
                localization_potential_score, entry_difficulty_score, recommended_priority, market_type,
                strengths, risks, explanation, score_breakdown, data_quality_status, calculation_version
            )
            VALUES (
                :country_id, :region_id, :period_start, :period_end, :opportunity_score,
                :traffic_score, :competition_score, :quality_score, :channel_gap_score, :volatility_score,
                :localization_potential_score, :entry_difficulty_score, :recommended_priority, :market_type,
                CAST(:strengths AS jsonb), CAST(:risks AS jsonb), :explanation, CAST(:score_breakdown AS jsonb),
                :data_quality_status, :calculation_version
            )
            ON CONFLICT (country_id, period_start, period_end, calculation_version) DO UPDATE
            SET opportunity_score = EXCLUDED.opportunity_score,
                traffic_score = EXCLUDED.traffic_score,
                competition_score = EXCLUDED.competition_score,
                quality_score = EXCLUDED.quality_score,
                channel_gap_score = EXCLUDED.channel_gap_score,
                volatility_score = EXCLUDED.volatility_score,
                localization_potential_score = EXCLUDED.localization_potential_score,
                entry_difficulty_score = EXCLUDED.entry_difficulty_score,
                recommended_priority = EXCLUDED.recommended_priority,
                market_type = EXCLUDED.market_type,
                strengths = EXCLUDED.strengths,
                risks = EXCLUDED.risks,
                explanation = EXCLUDED.explanation,
                score_breakdown = EXCLUDED.score_breakdown,
                data_quality_status = EXCLUDED.data_quality_status,
                calculated_at = now()
            RETURNING calculated_at::text
            """,
        ),
        {
            'country_id': country['country_id'],
            'region_id': country.get('region_id'),
            'period_start': date_from,
            'period_end': date_to,
            'opportunity_score': score,
            'traffic_score': components.traffic_score,
            'competition_score': components.competition_score,
            'quality_score': components.quality_score,
            'channel_gap_score': components.channel_gap_score,
            'volatility_score': components.volatility_score,
            'localization_potential_score': components.localization_potential_score,
            'entry_difficulty_score': components.entry_difficulty_score,
            'recommended_priority': priority,
            'market_type': market,
            'strengths': json_text(strengths),
            'risks': json_text(risks),
            'explanation': explanation,
            'score_breakdown': json_text(breakdown),
            'data_quality_status': data_quality_status,
            'calculation_version': calculation_version,
        },
    )
    calculated_at = result.scalar_one_or_none()
    session.commit()
    return calculated_at


def json_text(value: object) -> str:
    """Convert value to JSON text.
    Args:
        value (object): Source value."""
    text_value = json.dumps(value)
    return text_value


def calculate_score(
    session: Session,
    country_id: int,
    date_from: date,
    date_to: date,
    calculation_version: str,
) -> OpportunityScoreResponse:
    """Calculate opportunity score.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        calculation_version (str): Calculation version."""
    status = quality_status(session, country_id, date_from, date_to)
    country = country_data(session, country_id)
    metric_response = get_metrics(session, country_id, date_from, date_to, calculation_version, True)
    channel_summary = safe_channel(session, country_id, date_from, date_to, calculation_version)
    traffic_rank = traffic_percentile(session, country_id, date_from, date_to)
    components = build_components(metric_response.metrics, channel_summary, traffic_rank)
    score = final_score(components)
    priority = priority_label(score)
    market = market_type(score, components, metric_response.metrics.active_competitors_count or 0, paid_share(channel_summary))
    strengths = strength_list(components)
    risks = risk_list(components, metric_response.metrics.leader_share, metric_response.metrics.top_3_share, status)
    explanation = explain_score(country['country_name_en'], priority, components, risks)
    calculated_at = save_score(
        session,
        country,
        date_from,
        date_to,
        score,
        priority,
        market,
        components,
        strengths,
        risks,
        explanation,
        status,
        calculation_version,
    )
    response = OpportunityScoreResponse(
        country=country,
        period={'date_from': date_from, 'date_to': date_to, 'days_count': (date_to - date_from).days + 1},
        score=OpportunityScoreValues(opportunity_score=score, recommended_priority=priority, market_type=market),
        components=components,
        strengths=strengths,
        risks=risks,
        explanation=explanation,
        data_quality_status=status,
        calculation=OpportunityCalculation(calculation_version=calculation_version, calculated_at=calculated_at),
    )
    return response


def stored_score(
    session: Session,
    country_id: int,
    date_from: date,
    date_to: date,
    calculation_version: str,
) -> OpportunityScoreResponse | None:
    """Get stored score.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        calculation_version (str): Calculation version."""
    result = session.execute(
        text(
            """
            SELECT scores.*, scores.calculated_at::text AS calculated_at
            FROM country_opportunity_scores AS scores
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
    row = result.first()
    if row is None:
        return None
    row_data = dict(row._mapping)
    country = country_data(session, country_id)
    components = OpportunityComponents(
        traffic_score=optional_score(row_data.get('traffic_score')),
        competition_score=optional_score(row_data.get('competition_score')),
        quality_score=optional_score(row_data.get('quality_score')),
        channel_gap_score=optional_score(row_data.get('channel_gap_score')),
        volatility_score=optional_score(row_data.get('volatility_score')),
        localization_potential_score=optional_score(row_data.get('localization_potential_score')),
        entry_difficulty_score=optional_score(row_data.get('entry_difficulty_score')),
    )
    response = OpportunityScoreResponse(
        country=country,
        period={'date_from': date_from, 'date_to': date_to, 'days_count': (date_to - date_from).days + 1},
        score=OpportunityScoreValues(
            opportunity_score=float_value(row_data.get('opportunity_score')),
            recommended_priority=row_data.get('recommended_priority') or 'avoid',
            market_type=row_data.get('market_type') or 'unclear',
        ),
        components=components,
        strengths=row_data.get('strengths') or [],
        risks=row_data.get('risks') or [],
        explanation=row_data.get('explanation') or '',
        data_quality_status=row_data.get('data_quality_status') or 'unknown',
        calculation=OpportunityCalculation(
            calculation_version=calculation_version,
            calculated_at=row_data.get('calculated_at'),
        ),
    )
    return response


def optional_score(value: object) -> float | None:
    """Convert optional score.
    Args:
        value (object): Source value."""
    if value is None:
        return None
    return float(value)


def get_score(
    session: Session,
    country_id: int,
    date_from: date,
    date_to: date,
    calculation_version: str,
    calculate_if_missing: bool,
    force_recalculate: bool = False,
) -> OpportunityScoreResponse:
    """Get opportunity score.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        calculation_version (str): Calculation version.
        calculate_if_missing (bool): Calculate missing score flag.
        force_recalculate (bool): Force recalculation flag."""
    response = stored_score(session, country_id, date_from, date_to, calculation_version)
    if response is not None and not force_recalculate:
        return response
    if response is None and not calculate_if_missing and not force_recalculate:
        raise HTTPException(status_code=404, detail='OPPORTUNITY_SCORE_NOT_FOUND')
    return calculate_score(session, country_id, date_from, date_to, calculation_version)


def list_scores(
    session: Session,
    date_from: date,
    date_to: date,
    region_id: int | None,
    priority: str | None,
    limit: int,
    offset: int,
    calculate_if_missing: bool,
    force_recalculate: bool = False,
) -> dict[str, object]:
    """List opportunity scores.
    Args:
        session (Session): Database session.
        date_from (date): Period start date.
        date_to (date): Period end date.
        region_id (int | None): Region identifier.
        priority (str | None): Priority filter.
        limit (int): Result limit.
        offset (int): Result offset.
        calculate_if_missing (bool): Calculate missing scores flag.
        force_recalculate (bool): Force recalculation flag."""
    if calculate_if_missing or force_recalculate:
        populate_scores(session, date_from, date_to, region_id, force_recalculate)
    filters = ['scores.period_start = :date_from', 'scores.period_end = :date_to']
    params: dict[str, object] = {'date_from': date_from, 'date_to': date_to, 'limit': limit, 'offset': offset}
    if region_id is not None:
        filters.append('scores.region_id = :region_id')
        params['region_id'] = region_id
    if priority:
        filters.append('scores.recommended_priority = :priority')
        params['priority'] = priority
    where_clause = ' AND '.join(filters)
    result = session.execute(
        text(
            f"""
            SELECT
                scores.country_id,
                country.country_name_en,
                country.country_name_ru,
                region.region_name AS region_name_en,
                scores.period_start,
                scores.period_end,
                scores.opportunity_score,
                scores.recommended_priority,
                scores.market_type,
                scores.traffic_score,
                scores.competition_score,
                scores.quality_score,
                scores.channel_gap_score,
                scores.entry_difficulty_score,
                COUNT(*) OVER() AS total
            FROM country_opportunity_scores AS scores
            JOIN dim_country AS country ON country.country_id = scores.country_id
            LEFT JOIN dim_region AS region ON region.region_id = country.region_id
            WHERE {where_clause}
            ORDER BY scores.opportunity_score DESC NULLS LAST
            LIMIT :limit OFFSET :offset
            """,
        ),
        params,
    )
    rows = [dict(row._mapping) for row in result]
    total = int(rows[0]['total']) if rows else 0
    items = [OpportunityCountryItem(**{key: value for key, value in row.items() if key != 'total'}) for row in rows]
    return {'items': items, 'total': total}


def populate_scores(
    session: Session,
    date_from: date,
    date_to: date,
    region_id: int | None,
    force_recalculate: bool = False,
) -> int:
    """Populate missing scores.
    Args:
        session (Session): Database session.
        date_from (date): Period start date.
        date_to (date): Period end date.
        region_id (int | None): Region identifier.
        force_recalculate (bool): Force recalculation flag."""
    filters = ['facts.date BETWEEN :date_from AND :date_to']
    params: dict[str, object] = {'date_from': date_from, 'date_to': date_to}
    if region_id is not None:
        filters.append('country.region_id = :region_id')
        params['region_id'] = region_id
    where_clause = ' AND '.join(filters)
    result = session.execute(
        text(
            f"""
            SELECT DISTINCT facts.country_id
            FROM fact_domain_country_daily AS facts
            JOIN dim_country AS country ON country.country_id = facts.country_id
            WHERE {where_clause}
            ORDER BY facts.country_id
            """,
        ),
        params,
    )
    country_ids = [int(value) for value in result.scalars().all()]
    count = 0
    for country_id in country_ids:
        try:
            stored = stored_score(session, country_id, date_from, date_to, 'v1')
            if stored is None or force_recalculate:
                calculate_score(session, country_id, date_from, date_to, 'v1')
                count += 1
        except HTTPException:
            continue
    return count
