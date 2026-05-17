from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.schemas.report import CountryReportRequest
from app.schemas.advanced_strategy import AdvancedStrategyRequest
from app.schemas.strategy import BudgetStrategyRequest
from app.services.advanced_score_service import calculate_scores
from app.services.advanced_budget_allocation_service import allocate_advanced
from app.services.advanced_strategy_service import build_strategy
from app.services.budget_strategy_service import generate_strategy
from app.services.ads_creative_analysis_service import ads_creatives
from app.services.audience_analytics_service import audience_fit, audience_summary
from app.services.backlink_opportunity_service import backlink_opportunity, referring_domains
from app.services.business_impact_service import list_assumptions, list_performance
from app.services.channel_analysis_service import build_summary as build_channel_summary
from app.services.country_competitor_service import list_competitors
from app.services.country_metrics_service import get_metrics
from app.services.country_query_service import get_country
from app.services.country_report_service import create_country_report
from app.services.country_summary_service import build_country_summary
from app.services.feedback_loop_service import active_weights, learning_summary, list_comparisons, list_feedback, list_snapshots, similar_campaigns
from app.services.journey_source_service import build_journey
from app.services.opportunity_scoring_service import get_score
from app.services.paid_search_opportunity_service import paid_keywords, ppc_opportunity
from app.services.report_storage_service import find_report
from app.services.seo_opportunity_service import organic_keywords, seo_opportunity
from app.services.top_pages_analysis_service import top_pages


def dump_model(value: object) -> dict[str, object]:
    """Dump model value.
    Args:
        value (object): Source value."""
    if hasattr(value, 'model_dump'):
        dumped_value = value.model_dump(mode='json')
        return dumped_value
    if isinstance(value, dict):
        return value
    return {'value': value}


def tool_names() -> list[str]:
    """List tool names.
    Args:
        None (None): No arguments."""
    names = [
        'get_country_summary',
        'get_country_metrics',
        'get_top_competitors_by_country',
        'get_channel_summary',
        'get_journey_sources',
        'get_opportunity_score',
        'generate_budget_strategy',
        'create_country_report',
        'get_audience_summary',
        'get_audience_fit_score',
        'get_organic_keywords',
        'get_seo_opportunity',
        'get_paid_keywords',
        'get_ppc_opportunity',
        'get_top_pages',
        'get_ads_creatives',
        'get_referring_domains',
        'get_backlink_opportunity',
        'get_business_assumptions',
        'get_campaign_performance',
        'calculate_growth_scenarios',
        'calculate_roi_forecast',
        'calculate_advanced_scores',
        'calculate_advanced_budget_allocation',
        'get_recommendation_feedback',
        'get_forecast_accuracy',
        'get_campaign_results',
        'get_learning_summary',
        'get_active_scoring_weights',
        'get_similar_past_campaigns',
    ]
    return names


def recommendation_feedback(session: Session, project_id: int) -> dict[str, object]:
    """Call recommendation feedback tool.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier."""
    feedback = list_feedback(session, project_id)
    return dump_model(feedback)


def forecast_accuracy(session: Session, project_id: int) -> dict[str, object]:
    """Call forecast accuracy tool.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier."""
    comparisons = list_comparisons(session, project_id)
    return dump_model(comparisons)


def campaign_results(session: Session, project_id: int) -> dict[str, object]:
    """Call campaign results tool.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier."""
    snapshots = list_snapshots(session, project_id)
    return dump_model(snapshots)


def feedback_learning(session: Session, project_id: int) -> dict[str, object]:
    """Call learning summary tool.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier."""
    summary = learning_summary(session, project_id)
    return dump_model(summary)


def scoring_weights(session: Session) -> dict[str, object]:
    """Call scoring weights tool.
    Args:
        session (Session): Database session."""
    weights = active_weights(session)
    return dump_model(weights)


def past_campaigns(session: Session, project_id: int, country_id: int | None = None, channel_id: int | None = None) -> dict[str, object]:
    """Call past campaigns tool.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        country_id (int | None): Country identifier.
        channel_id (int | None): Channel identifier."""
    snapshots = similar_campaigns(session, project_id, country_id, channel_id)
    return dump_model(snapshots)


def growth_scenarios(
    session: Session,
    project_id: int,
    request: AdvancedStrategyRequest,
) -> dict[str, object]:
    """Call growth scenarios tool.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        request (AdvancedStrategyRequest): Strategy request."""
    strategy = build_strategy(session, project_id, request)
    return dump_model(strategy)


def roi_forecast(
    session: Session,
    project_id: int,
    request: AdvancedStrategyRequest,
) -> dict[str, object]:
    """Call ROI forecast tool.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        request (AdvancedStrategyRequest): Strategy request."""
    strategy = build_strategy(session, project_id, request)
    payload = {'scenarios': [scenario.model_dump(mode='json') for scenario in strategy.scenarios]}
    return payload


def advanced_scores(
    session: Session,
    project_id: int,
    request: AdvancedStrategyRequest,
) -> dict[str, object]:
    """Call advanced scores tool.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        request (AdvancedStrategyRequest): Strategy request."""
    scores = calculate_scores(session, project_id, request.country_id, request.date_from, request.date_to, request.calculation_version)
    return dump_model(scores)


def advanced_allocation(
    strategy_name: str,
    budget_amount: float,
    expected_traffic: float,
    expected_leads: float,
    expected_clients: float,
    expected_revenue: float,
    scores: object,
) -> dict[str, object]:
    """Call advanced allocation tool.
    Args:
        strategy_name (str): Strategy name.
        budget_amount (float): Budget amount.
        expected_traffic (float): Expected traffic.
        expected_leads (float): Expected leads.
        expected_clients (float): Expected clients.
        expected_revenue (float): Expected revenue.
        scores (object): Advanced scores."""
    allocation = allocate_advanced(
        strategy_name,
        budget_amount,
        expected_traffic,
        expected_leads,
        expected_clients,
        expected_revenue,
        scores,
    )
    payload = {'items': [item.model_dump(mode='json') for item in allocation]}
    return payload


def project_audience_summary(session: Session, project_id: int) -> dict[str, object]:
    """Call audience summary tool.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier."""
    summary = audience_summary(session, project_id)
    return dump_model(summary)


def project_audience_fit(session: Session, project_id: int, country_id: int) -> dict[str, object]:
    """Call audience fit tool.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        country_id (int): Country identifier."""
    summary = audience_fit(session, project_id, country_id)
    return dump_model(summary)


def project_organic_keywords(session: Session, project_id: int) -> dict[str, object]:
    """Call organic keywords tool.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier."""
    keywords = organic_keywords(session, project_id)
    return dump_model(keywords)


def project_seo_opportunity(session: Session, project_id: int) -> dict[str, object]:
    """Call SEO opportunity tool.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier."""
    opportunity = seo_opportunity(session, project_id)
    return dump_model(opportunity)


def project_paid_keywords(session: Session, project_id: int) -> dict[str, object]:
    """Call paid keywords tool.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier."""
    keywords = paid_keywords(session, project_id)
    return dump_model(keywords)


def project_ppc_opportunity(session: Session, project_id: int) -> dict[str, object]:
    """Call PPC opportunity tool.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier."""
    opportunity = ppc_opportunity(session, project_id)
    return dump_model(opportunity)


def project_top_pages(session: Session, project_id: int) -> dict[str, object]:
    """Call top pages tool.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier."""
    pages = top_pages(session, project_id)
    return dump_model(pages)


def project_ads_creatives(session: Session, project_id: int) -> dict[str, object]:
    """Call ad creatives tool.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier."""
    creatives = ads_creatives(session, project_id)
    return dump_model(creatives)


def project_referring_domains(session: Session, project_id: int) -> dict[str, object]:
    """Call referring domains tool.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier."""
    domains = referring_domains(session, project_id)
    return dump_model(domains)


def project_backlink_opportunity(session: Session, project_id: int) -> dict[str, object]:
    """Call backlink opportunity tool.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier."""
    opportunity = backlink_opportunity(session, project_id)
    return dump_model(opportunity)


def project_assumptions(session: Session, project_id: int) -> dict[str, object]:
    """Call assumptions tool.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier."""
    assumptions = list_assumptions(session, project_id)
    return dump_model(assumptions)


def project_campaign_performance(session: Session, project_id: int, campaign_id: int) -> dict[str, object]:
    """Call campaign performance tool.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        campaign_id (int): Campaign identifier."""
    performance = list_performance(session, project_id, campaign_id)
    return dump_model(performance)


def country_summary(
    session: Session,
    country_id: int,
    date_from: date,
    date_to: date,
    calculation_version: str,
) -> dict[str, object]:
    """Call country summary tool.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        calculation_version (str): Calculation version."""
    country = get_country(session, country_id)
    if country is None:
        raise HTTPException(status_code=404, detail='Country not found.')
    summary = build_country_summary(session, country, date_from, date_to, 10)
    return dump_model(summary)


def country_metrics(
    session: Session,
    country_id: int,
    date_from: date,
    date_to: date,
    calculation_version: str,
) -> dict[str, object]:
    """Call country metrics tool.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        calculation_version (str): Calculation version."""
    metrics = get_metrics(session, country_id, date_from, date_to, calculation_version, True)
    return dump_model(metrics)


def top_competitors(
    session: Session,
    country_id: int,
    date_from: date,
    date_to: date,
    calculation_version: str,
) -> dict[str, object]:
    """Call competitors tool.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        calculation_version (str): Calculation version."""
    competitors = list_competitors(session, country_id, date_from, date_to, 10, 'traffic', 'desc')
    return competitors


def channel_summary(
    session: Session,
    country_id: int,
    date_from: date,
    date_to: date,
    calculation_version: str,
) -> dict[str, object]:
    """Call channel summary tool.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        calculation_version (str): Calculation version."""
    summary = build_channel_summary(session, country_id, None, date_from, date_to, calculation_version)
    return dump_model(summary)


def journey_sources(
    session: Session,
    country_id: int,
    date_from: date,
    date_to: date,
    calculation_version: str,
) -> dict[str, object]:
    """Call journey sources tool.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        calculation_version (str): Calculation version."""
    items, warnings = build_journey(session, country_id, None, None, date_from, date_to, 10, calculation_version)
    response = {'items': [dump_model(item) for item in items], 'warnings': warnings}
    return response


def opportunity_score(
    session: Session,
    country_id: int,
    date_from: date,
    date_to: date,
    calculation_version: str,
) -> dict[str, object]:
    """Call opportunity score tool.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        calculation_version (str): Calculation version."""
    score = get_score(session, country_id, date_from, date_to, calculation_version, True, False)
    return dump_model(score)


def budget_strategy(
    session: Session,
    country_id: int,
    date_from: date,
    date_to: date,
    calculation_version: str,
    budget_amount: float,
    currency_code: str,
    campaign_goal: str,
    risk_appetite: str,
) -> dict[str, object]:
    """Call budget strategy tool.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        calculation_version (str): Calculation version.
        budget_amount (float): Budget amount.
        currency_code (str): Currency code.
        campaign_goal (str): Campaign goal.
        risk_appetite (str): Risk appetite."""
    request = BudgetStrategyRequest(
        country_id=country_id,
        date_from=date_from,
        date_to=date_to,
        budget_amount=budget_amount,
        currency_code=currency_code,
        campaign_goal=campaign_goal,
        risk_appetite=risk_appetite,
        calculation_version=calculation_version,
    )
    strategy = generate_strategy(session, request)
    return dump_model(strategy)


def country_report(
    session: Session,
    country_id: int,
    date_from: date,
    date_to: date,
    calculation_version: str,
) -> dict[str, object]:
    """Call country report tool.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        calculation_version (str): Calculation version."""
    existing_report = find_report(session, 'country_report', country_id, date_from, date_to, calculation_version)
    if existing_report is not None:
        return existing_report
    request = CountryReportRequest(
        country_id=country_id,
        date_from=date_from,
        date_to=date_to,
        limit_competitors=10,
        include_channels=True,
        include_recommendations=True,
        calculation_version=calculation_version,
    )
    report = create_country_report(session, request)
    return dump_model(report)
