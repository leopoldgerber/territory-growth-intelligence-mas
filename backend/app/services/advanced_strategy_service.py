from datetime import date
import json

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.advanced_strategy import (
    AdvancedAllocationItem,
    AdvancedAssumptions,
    AdvancedStrategyRequest,
    AdvancedStrategyResponse,
    GrowthScenarioDetail,
    GrowthScenarioItem,
    GrowthScenarioList,
    SensitivityItem,
)
from app.schemas.history import SavedSummaryCreate
from app.services.advanced_budget_allocation_service import allocate_advanced
from app.services.advanced_score_service import calculate_scores, strategy_type
from app.services.country_metrics_service import get_metrics
from app.services.country_query_service import get_country
from app.services.lead_client_forecast_service import client_forecast, lead_forecast, revenue_forecast
from app.services.roi_forecast_service import cac_value, gross_profit, payback_days, roi_value
from app.services.summary_storage_service import create_summary
from app.services.traffic_capture_forecast_service import confidence_score, forecast_days, traffic_capture


def json_text(value: object) -> str:
    """Convert JSON text.
    Args:
        value (object): Source value."""
    text_value = json.dumps(value, default=str)
    return text_value


def latest_assumptions(session: Session, project_id: int, country_id: int) -> tuple[AdvancedAssumptions, bool]:
    """Get latest assumptions.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        country_id (int): Country identifier."""
    result = session.execute(
        text(
            """
            SELECT *
            FROM business_assumptions
            WHERE project_id = :project_id
              AND (country_id = :country_id OR country_id IS NULL)
            ORDER BY country_id NULLS LAST, created_at DESC
            LIMIT 1
            """,
        ),
        {'project_id': project_id, 'country_id': country_id},
    )
    row = result.first()
    if row is None:
        return AdvancedAssumptions(), False
    data = dict(row._mapping)
    assumptions = AdvancedAssumptions(
        visit_to_lead_rate=float(data.get('visit_to_lead_rate') or 0.03),
        lead_to_client_rate=float(data.get('lead_to_client_rate') or 0.15),
        average_order_value=float(data.get('average_order_value') or 500),
        lifetime_value=float(data.get('ltv') or data.get('average_order_value') or 2500),
        gross_margin=float(data.get('gross_margin') or 0.65),
        target_cac=float(data.get('target_cac') or 400),
        traffic_capture_rate=0.02,
    )
    return assumptions, True


def has_campaigns(session: Session, project_id: int, country_id: int) -> bool:
    """Check campaign data.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        country_id (int): Country identifier."""
    result = session.execute(
        text(
            """
            SELECT COUNT(*)
            FROM campaign_performance_daily AS performance
            JOIN campaigns ON campaigns.campaign_id = performance.campaign_id
            WHERE performance.project_id = :project_id
              AND (campaigns.country_id = :country_id OR campaigns.country_id IS NULL)
            """,
        ),
        {'project_id': project_id, 'country_id': country_id},
    )
    exists = int(result.scalar_one() or 0) > 0
    return exists


def scenario_names(mode: str) -> list[str]:
    """Build scenario names.
    Args:
        mode (str): Scenario mode."""
    if mode in ['conservative', 'base', 'aggressive']:
        return [mode]
    return ['conservative', 'base', 'aggressive']


def build_scenario(
    market_traffic: float,
    request: AdvancedStrategyRequest,
    assumptions: AdvancedAssumptions,
    scenario_name: str,
    scores: object,
    has_assumptions: bool,
    campaign_available: bool,
) -> GrowthScenarioItem:
    """Build scenario.
    Args:
        market_traffic (float): Market traffic.
        request (AdvancedStrategyRequest): Strategy request.
        assumptions (AdvancedAssumptions): Forecast assumptions.
        scenario_name (str): Scenario name.
        scores (object): Advanced scores.
        has_assumptions (bool): Assumptions flag.
        campaign_available (bool): Campaign data flag."""
    expected_traffic = traffic_capture(market_traffic, scores, assumptions, scenario_name, request.forecast_start, request.forecast_end)
    expected_leads = lead_forecast(expected_traffic, assumptions)
    expected_clients = client_forecast(expected_leads, assumptions)
    expected_revenue = revenue_forecast(expected_clients, assumptions)
    expected_profit = gross_profit(expected_revenue, assumptions)
    scenario = GrowthScenarioItem(
        scenario_name=scenario_name,
        budget_amount=request.budget_amount,
        currency_code=request.currency_code[:3].upper(),
        expected_traffic_capture=expected_traffic,
        expected_leads=expected_leads,
        expected_clients=expected_clients,
        expected_revenue=expected_revenue,
        expected_gross_profit=expected_profit,
        estimated_cac=cac_value(request.budget_amount, expected_clients),
        estimated_roi=roi_value(request.budget_amount, expected_profit),
        payback_period_days=payback_days(request.budget_amount, expected_profit, forecast_days(request.forecast_start, request.forecast_end)),
        confidence_score=confidence_score(scores, scenario_name, has_assumptions, campaign_available),
    )
    return scenario


def save_scenario(
    session: Session,
    project_id: int,
    country_id: int,
    request: AdvancedStrategyRequest,
    advanced_score_id: int | None,
    scenario: GrowthScenarioItem,
    assumptions: AdvancedAssumptions,
    details: dict[str, object],
) -> int:
    """Save scenario.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        country_id (int): Country identifier.
        request (AdvancedStrategyRequest): Strategy request.
        advanced_score_id (int | None): Advanced score identifier.
        scenario (GrowthScenarioItem): Scenario item.
        assumptions (AdvancedAssumptions): Forecast assumptions.
        details (dict[str, object]): Scenario details."""
    result = session.execute(
        text(
            """
            INSERT INTO growth_scenarios (
                project_id, country_id, advanced_score_id, period_start, period_end, forecast_start,
                forecast_end, scenario_name, budget_amount, currency_code, expected_traffic_capture,
                expected_leads, expected_clients, expected_revenue, expected_gross_profit, estimated_cac,
                estimated_roi, payback_period_days, confidence_score, assumptions, scenario_details,
                calculation_version
            )
            VALUES (
                :project_id, :country_id, :advanced_score_id, :period_start, :period_end, :forecast_start,
                :forecast_end, :scenario_name, :budget_amount, :currency_code, :expected_traffic_capture,
                :expected_leads, :expected_clients, :expected_revenue, :expected_gross_profit, :estimated_cac,
                :estimated_roi, :payback_period_days, :confidence_score, CAST(:assumptions AS jsonb),
                CAST(:scenario_details AS jsonb), :calculation_version
            )
            RETURNING growth_scenario_id
            """,
        ),
        {
            'project_id': project_id,
            'country_id': country_id,
            'advanced_score_id': advanced_score_id,
            'period_start': request.date_from,
            'period_end': request.date_to,
            'forecast_start': request.forecast_start,
            'forecast_end': request.forecast_end,
            **scenario.model_dump(exclude={'growth_scenario_id'}),
            'assumptions': json_text(assumptions.model_dump()),
            'scenario_details': json_text(details),
            'calculation_version': request.calculation_version,
        },
    )
    scenario_id = int(result.scalar_one())
    return scenario_id


def save_allocations(
    session: Session,
    project_id: int,
    country_id: int,
    scenario_id: int,
    allocations: list[AdvancedAllocationItem],
) -> list[AdvancedAllocationItem]:
    """Save allocations.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        country_id (int): Country identifier.
        scenario_id (int): Scenario identifier.
        allocations (list[AdvancedAllocationItem]): Allocation items."""
    saved_items = []
    for item in allocations:
        result = session.execute(
            text(
                """
                INSERT INTO advanced_budget_allocations (
                    growth_scenario_id, project_id, country_id, allocation_category, budget_share, budget_amount,
                    expected_traffic, expected_leads, expected_clients, expected_revenue, estimated_cac,
                    rationale, risk_level, success_metric
                )
                VALUES (
                    :growth_scenario_id, :project_id, :country_id, :allocation_category, :budget_share, :budget_amount,
                    :expected_traffic, :expected_leads, :expected_clients, :expected_revenue, :estimated_cac,
                    :rationale, :risk_level, :success_metric
                )
                RETURNING advanced_allocation_id
                """,
            ),
            {
                'growth_scenario_id': scenario_id,
                'project_id': project_id,
                'country_id': country_id,
                **item.model_dump(exclude={'advanced_allocation_id', 'growth_scenario_id'}),
            },
        )
        item.advanced_allocation_id = int(result.scalar_one())
        item.growth_scenario_id = scenario_id
        saved_items.append(item)
    return saved_items


def recommendation_list(strategy_name: str, best_scenario: GrowthScenarioItem) -> list[str]:
    """Build recommendations.
    Args:
        strategy_name (str): Strategy name.
        best_scenario (GrowthScenarioItem): Best scenario."""
    recommendations = [
        f'Use {strategy_name} as the primary growth strategy.',
        f'Use {best_scenario.scenario_name} scenario as the planning baseline.',
    ]
    if best_scenario.estimated_cac is not None:
        recommendations.append(f'Track CAC against forecasted {round(best_scenario.estimated_cac, 2)}.')
    return recommendations


def risk_list(best_scenario: GrowthScenarioItem, has_assumptions: bool, campaign_available: bool) -> list[str]:
    """Build risk list.
    Args:
        best_scenario (GrowthScenarioItem): Best scenario.
        has_assumptions (bool): Assumptions flag.
        campaign_available (bool): Campaign data flag."""
    risks = []
    if not has_assumptions:
        risks.append('ROI forecast uses default conversion assumptions.')
    if not campaign_available:
        risks.append('No campaign performance exists for feedback calibration.')
    if best_scenario.estimated_cac is None:
        risks.append('Expected clients are zero, so CAC cannot be calculated.')
    if best_scenario.estimated_roi is not None and best_scenario.estimated_roi > 1 and best_scenario.confidence_score < 0.55:
        risks.append('Scenario looks financially attractive, but confidence is low.')
    return risks


def sensitivity_items(best_scenario: GrowthScenarioItem, assumptions: AdvancedAssumptions) -> list[SensitivityItem]:
    """Build sensitivity items.
    Args:
        best_scenario (GrowthScenarioItem): Best scenario.
        assumptions (AdvancedAssumptions): Forecast assumptions."""
    items = []
    factors = [
        ('visit_to_lead_rate', assumptions.visit_to_lead_rate),
        ('lead_to_client_rate', assumptions.lead_to_client_rate),
        ('lifetime_value', assumptions.lifetime_value),
        ('gross_margin', assumptions.gross_margin),
    ]
    for factor_name, base_value in factors:
        low_value = base_value * 0.8
        high_value = base_value * 1.2
        low_clients = best_scenario.expected_clients * 0.8
        high_clients = best_scenario.expected_clients * 1.2
        items.append(
            SensitivityItem(
                factor_name=factor_name,
                base_value=round(base_value, 4),
                low_value=round(low_value, 4),
                high_value=round(high_value, 4),
                low_clients=round(low_clients, 2),
                high_clients=round(high_clients, 2),
                low_roi=None if best_scenario.estimated_roi is None else round(best_scenario.estimated_roi * 0.8, 4),
                high_roi=None if best_scenario.estimated_roi is None else round(best_scenario.estimated_roi * 1.2, 4),
            ),
        )
    return items


def save_strategy_summary(
    session: Session,
    country: dict[str, object],
    request: AdvancedStrategyRequest,
    best_scenario: GrowthScenarioItem,
    strategy_name: str,
    response_payload: dict[str, object],
) -> int:
    """Save strategy summary.
    Args:
        session (Session): Database session.
        country (dict[str, object]): Country row.
        request (AdvancedStrategyRequest): Strategy request.
        best_scenario (GrowthScenarioItem): Best scenario.
        strategy_name (str): Strategy name.
        response_payload (dict[str, object]): Response payload."""
    summary = SavedSummaryCreate(
        summary_type='advanced_strategy',
        title=f"Advanced strategy for {country.get('country_name_en')}",
        summary_text=(
            f"Advanced strategy recommends {strategy_name}. "
            f"Base planning scenario is {best_scenario.scenario_name} with "
            f"{round(best_scenario.expected_clients, 2)} expected clients and ROI {best_scenario.estimated_roi}."
        ),
        summary_json=response_payload,
        country_id=request.country_id,
        period_start=request.date_from,
        period_end=request.date_to,
        source_type='growth_scenario',
        source_id=int(best_scenario.growth_scenario_id or 0),
        tags=['advanced_strategy', 'forecast', 'roi'],
        importance_score=0.85,
        confidence_score=best_scenario.confidence_score,
        data_quality_status='forecast',
        rag_ready=True,
    )
    summary_id = create_summary(session, summary)
    return summary_id


def build_strategy(session: Session, project_id: int, request: AdvancedStrategyRequest) -> AdvancedStrategyResponse:
    """Build advanced strategy.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        request (AdvancedStrategyRequest): Strategy request."""
    country = get_country(session, request.country_id)
    if country is None:
        raise HTTPException(status_code=404, detail='Country not found.')
    assumptions, stored_assumptions = latest_assumptions(session, project_id, request.country_id)
    if request.assumptions is not None:
        assumptions = request.assumptions
        stored_assumptions = True
    campaign_available = has_campaigns(session, project_id, request.country_id)
    score_response = calculate_scores(session, project_id, request.country_id, request.date_from, request.date_to, request.calculation_version)
    scores = score_response.scores
    metrics = get_metrics(session, request.country_id, request.date_from, request.date_to, 'v1', True).metrics
    market_traffic = float(metrics.total_competitor_traffic or 0)
    strategy_name = strategy_type(scores)
    scenarios = [
        build_scenario(market_traffic, request, assumptions, name, scores, stored_assumptions, campaign_available)
        for name in scenario_names(request.scenario_mode)
    ]
    best_scenario = next((scenario for scenario in scenarios if scenario.scenario_name == 'base'), scenarios[0])
    details = {'market_traffic': market_traffic, 'strategy_name': strategy_name}
    saved_allocations = []
    for scenario in scenarios:
        scenario_id = save_scenario(session, project_id, request.country_id, request, scores.advanced_score_id, scenario, assumptions, details)
        scenario.growth_scenario_id = scenario_id
        if scenario.scenario_name == best_scenario.scenario_name:
            allocation = allocate_advanced(
                strategy_name,
                scenario.budget_amount,
                scenario.expected_traffic_capture,
                scenario.expected_leads,
                scenario.expected_clients,
                scenario.expected_revenue,
                scores,
            )
            saved_allocations = save_allocations(session, project_id, request.country_id, scenario_id, allocation)
            best_scenario = scenario
    session.commit()
    warnings = []
    if not stored_assumptions:
        warnings.append('ROI forecast uses default conversion assumptions because no business assumptions were found.')
    if not campaign_available:
        warnings.append('No real campaign performance exists for feedback calibration.')
    explanation = f'{country.get("country_name_en")} is best approached with {strategy_name} based on advanced scores and scenario ROI.'
    response = AdvancedStrategyResponse(
        country=country,
        period={'date_from': request.date_from, 'date_to': request.date_to, 'days_count': (request.date_to - request.date_from).days + 1},
        forecast_period={'forecast_start': request.forecast_start, 'forecast_end': request.forecast_end},
        advanced_scores=scores,
        recommended_strategy_type=strategy_name,
        scenarios=scenarios,
        recommended_allocation=saved_allocations,
        sensitivity=sensitivity_items(best_scenario, assumptions),
        recommendations=recommendation_list(strategy_name, best_scenario),
        risks=risk_list(best_scenario, stored_assumptions, campaign_available),
        explanation=explanation,
        assumptions=assumptions,
        warnings=warnings,
    )
    save_strategy_summary(session, country, request, best_scenario, strategy_name, response.model_dump(mode='json'))
    return response


def list_scenarios(session: Session, project_id: int, limit: int, offset: int) -> GrowthScenarioList:
    """List scenarios.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        limit (int): Result limit.
        offset (int): Result offset."""
    result = session.execute(
        text(
            """
            SELECT *, COUNT(*) OVER() AS total
            FROM growth_scenarios
            WHERE project_id = :project_id
            ORDER BY created_at DESC, growth_scenario_id DESC
            LIMIT :limit OFFSET :offset
            """,
        ),
        {'project_id': project_id, 'limit': limit, 'offset': offset},
    )
    rows = [dict(row._mapping) for row in result]
    total = int(rows[0]['total']) if rows else 0
    items = [GrowthScenarioItem(**{key: value for key, value in row.items() if key != 'total'}) for row in rows]
    return GrowthScenarioList(items=items, total=total)


def get_scenario(session: Session, project_id: int, growth_scenario_id: int) -> GrowthScenarioDetail:
    """Get scenario.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        growth_scenario_id (int): Scenario identifier."""
    row = session.execute(
        text('SELECT * FROM growth_scenarios WHERE project_id = :project_id AND growth_scenario_id = :growth_scenario_id'),
        {'project_id': project_id, 'growth_scenario_id': growth_scenario_id},
    ).first()
    if row is None:
        raise HTTPException(status_code=404, detail='Growth scenario not found.')
    allocations = session.execute(
        text(
            """
            SELECT *
            FROM advanced_budget_allocations
            WHERE growth_scenario_id = :growth_scenario_id
            ORDER BY budget_share DESC NULLS LAST
            """,
        ),
        {'growth_scenario_id': growth_scenario_id},
    )
    scenario_data = dict(row._mapping)
    detail = GrowthScenarioDetail(
        scenario=GrowthScenarioItem(**scenario_data),
        allocation=[AdvancedAllocationItem(**dict(item._mapping)) for item in allocations],
        assumptions=scenario_data.get('assumptions'),
        scenario_details=scenario_data.get('scenario_details'),
    )
    return detail
