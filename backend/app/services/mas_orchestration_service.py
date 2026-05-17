from datetime import date
import re

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.mas import MASAnalyzeRequest, MASRunResponse
from app.services.country_query_service import get_country, get_period, period_quality
from app.services.mas_store_service import (
    create_run,
    get_run,
    save_evidence,
    save_insight,
    save_recommendation,
    save_step,
    update_run,
)
from app.services.mas_tool_registry_service import (
    budget_strategy,
    channel_summary,
    country_metrics,
    country_report,
    country_summary,
    journey_sources,
    opportunity_score,
    top_competitors,
    tool_names,
)
from app.services.summary_generation_service import create_agent_summary


def find_country(session: Session, user_query: str, country_id: int | None) -> dict[str, object] | None:
    """Find requested country.
    Args:
        session (Session): Database session.
        user_query (str): User query text.
        country_id (int | None): Country identifier."""
    if country_id is not None:
        return get_country(session, country_id)
    result = session.execute(
        text(
            """
            SELECT
                country.country_id,
                country.country_name_en,
                country.country_name_ru,
                region.region_name AS region_name_en,
                region.region_name AS region_name_ru,
                TRUE AS has_data
            FROM dim_country AS country
            LEFT JOIN dim_region AS region ON region.region_id = country.region_id
            WHERE :user_query ILIKE '%' || country.country_name_en || '%'
               OR :user_query ILIKE '%' || COALESCE(country.country_name_ru, '') || '%'
            ORDER BY LENGTH(country.country_name_en) DESC
            LIMIT 1
            """,
        ),
        {'user_query': user_query},
    )
    row = result.first()
    country = dict(row._mapping) if row else None
    return country


def resolve_period(
    session: Session,
    country_id: int,
    date_from: date | None,
    date_to: date | None,
) -> tuple[date | None, date | None]:
    """Resolve requested period.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_from (date | None): Period start date.
        date_to (date | None): Period end date."""
    if date_from is not None and date_to is not None:
        return date_from, date_to
    period = get_period(session, country_id)
    resolved_from = date_from or period.get('date_min')
    resolved_to = date_to or period.get('date_max')
    return resolved_from, resolved_to


def parse_budget(user_query: str, budget_amount: float | None) -> float | None:
    """Parse budget amount.
    Args:
        user_query (str): User query text.
        budget_amount (float | None): Structured budget amount."""
    if budget_amount is not None:
        return budget_amount
    pattern = r'(\d[\d\s,.]*)\s*(eur|euro|usd|rub|руб|долл)'
    match = re.search(pattern, user_query, flags=re.IGNORECASE)
    if match is None:
        return None
    raw_value = match.group(1).replace(' ', '').replace(',', '.')
    try:
        parsed_value = float(raw_value)
    except ValueError:
        parsed_value = None
    return parsed_value


def quality_confidence(status: str | None) -> float:
    """Calculate quality confidence.
    Args:
        status (str | None): Quality status."""
    if status == 'warning':
        return 0.78
    if status == 'failed':
        return 0.2
    if status == 'passed':
        return 0.92
    return 0.72


def number_value(value: object) -> float | None:
    """Convert number value.
    Args:
        value (object): Source value."""
    if value is None:
        return None
    try:
        converted_value = float(value)
    except (TypeError, ValueError):
        converted_value = None
    return converted_value


def save_metric(
    session: Session,
    agent_run_id: int,
    source_name: str,
    metric_name: str,
    metric_value: object,
    payload: dict[str, object],
) -> int:
    """Save metric evidence.
    Args:
        session (Session): Database session.
        agent_run_id (int): Agent run identifier.
        source_name (str): Source name.
        metric_name (str): Metric name.
        metric_value (object): Metric value.
        payload (dict[str, object]): Evidence payload."""
    evidence_id = save_evidence(
        session,
        agent_run_id,
        'metric',
        source_name,
        source_name,
        metric_name,
        number_value(metric_value),
        payload,
    )
    return evidence_id


def build_answer(
    country_name: str,
    date_from: date,
    date_to: date,
    outputs: dict[str, dict[str, object]],
    budget_amount: float | None,
    currency_code: str,
) -> str:
    """Build final answer.
    Args:
        country_name (str): Country name.
        date_from (date): Period start date.
        date_to (date): Period end date.
        outputs (dict[str, dict[str, object]]): Tool outputs.
        budget_amount (float | None): Budget amount.
        currency_code (str): Currency code."""
    summary = outputs.get('country_summary', {}).get('summary', {})
    opportunity = outputs.get('opportunity_score', {}).get('score', {})
    channel = outputs.get('channel_summary', {}).get('summary', {})
    strategy = outputs.get('budget_strategy', {}).get('strategy', {})
    dominant_channel = channel.get('dominant_channel') or {}
    lines = [
        f'## Strategy analysis for {country_name}',
        f'Period: {date_from} - {date_to}.',
        '',
        f"- Market traffic: {round(float(summary.get('total_competitor_traffic') or 0), 2)} visits.",
        f"- Active competitors: {summary.get('active_competitors_count') or 0}.",
        f"- Opportunity score: {round(float(opportunity.get('opportunity_score') or 0), 2)} "
        f"({opportunity.get('recommended_priority') or 'unknown'} priority).",
        f"- Dominant channel: {dominant_channel.get('channel_name') or 'unknown'}.",
    ]
    if budget_amount is not None:
        lines.extend(
            [
                '',
                f'Budget scenario: {budget_amount} {currency_code}.',
                strategy.get('summary') or 'Budget allocation was generated from current opportunity and channel signals.',
            ],
        )
    else:
        lines.extend(
            [
                '',
                'Budget was not provided, so this run focuses on market, competitor, channel, and opportunity signals.',
            ],
        )
    final_answer = '\n'.join(lines)
    return final_answer


def run_analysis(session: Session, request: MASAnalyzeRequest) -> MASRunResponse:
    """Run MAS analysis.
    Args:
        session (Session): Database session.
        request (MASAnalyzeRequest): MAS request."""
    country = find_country(session, request.user_query, request.country_id)
    country_id = int(country['country_id']) if country else None
    date_from, date_to = resolve_period(session, country_id, request.date_from, request.date_to) if country_id else (None, None)
    budget_amount = parse_budget(request.user_query, request.budget_amount)
    agent_run_id = create_run(
        session,
        request.user_query,
        country_id,
        date_from,
        date_to,
        budget_amount,
        request.currency_code,
        request.campaign_goal,
    )
    if country is None or country_id is None or date_from is None or date_to is None:
        final_answer = 'Please select a country and period before running strategy analysis.'
        save_step(session, agent_run_id, 1, 'Planner Agent', 'planning', 'needs_clarification', final_answer, {'tools': tool_names()})
        update_run(session, agent_run_id, 'needs_clarification', final_answer, 0.0, {})
        response = get_run(session, agent_run_id)
        if response is None:
            raise HTTPException(status_code=500, detail='MAS run was not saved.')
        return response
    outputs: dict[str, dict[str, object]] = {}
    quality_status = period_quality(session, country_id, date_from, date_to)
    current_step = 'planning'
    try:
        current_step = 'planning'
        save_step(
            session,
            agent_run_id,
            1,
            'Planner Agent',
            'planning',
            'completed',
            'Built a synchronous rule-based plan for market, competitor, channel, opportunity, and report steps.',
            {'tools': tool_names(), 'quality_status': quality_status},
        )
        current_step = 'country_analysis'
        outputs['country_summary'] = country_summary(session, country_id, date_from, date_to, request.calculation_version)
        outputs['country_metrics'] = country_metrics(session, country_id, date_from, date_to, request.calculation_version)
        summary_values = outputs['country_summary'].get('summary', {})
        save_metric(session, agent_run_id, 'get_country_summary', 'total_competitor_traffic', summary_values.get('total_competitor_traffic'), summary_values)
        save_metric(session, agent_run_id, 'get_country_metrics', 'engagement_score', outputs['country_metrics'].get('metrics', {}).get('engagement_score'), outputs['country_metrics'].get('metrics', {}))
        save_insight(
            session,
            agent_run_id,
            'Country Analyst Agent',
            'market_signal',
            'Country demand baseline is available',
            'Country metrics were calculated and attached as evidence for the final answer.',
            'medium',
            quality_confidence(quality_status),
        )
        save_step(session, agent_run_id, 2, 'Country Analyst Agent', 'analysis', 'completed', 'Calculated country summary and country metric evidence.', outputs['country_summary'])
        current_step = 'competitor_analysis'
        outputs['competitors'] = top_competitors(session, country_id, date_from, date_to, request.calculation_version)
        leader = outputs['competitors'].get('items', [{}])[0] if outputs['competitors'].get('items') else {}
        save_metric(session, agent_run_id, 'get_top_competitors_by_country', 'leader_traffic_share', leader.get('traffic_share'), leader)
        save_insight(
            session,
            agent_run_id,
            'Competitor Analyst Agent',
            'competitive_position',
            'Competitor benchmark is ready',
            f"Top competitor: {leader.get('domain') or 'unknown'}.",
            'medium',
            quality_confidence(quality_status),
        )
        save_step(session, agent_run_id, 3, 'Competitor Analyst Agent', 'analysis', 'completed', 'Ranked top competitors by country traffic.', outputs['competitors'])
        current_step = 'channel_analysis'
        outputs['channel_summary'] = channel_summary(session, country_id, date_from, date_to, request.calculation_version)
        outputs['journey_sources'] = journey_sources(session, country_id, date_from, date_to, request.calculation_version)
        channel_values = outputs['channel_summary'].get('summary', {})
        dominant_channel = channel_values.get('dominant_channel') or {}
        save_metric(session, agent_run_id, 'get_channel_summary', 'dominant_channel_share', dominant_channel.get('traffic_share'), dominant_channel)
        save_insight(
            session,
            agent_run_id,
            'Channel Strategist Agent',
            'channel_mix',
            'Channel mix can guide acquisition focus',
            f"Dominant channel: {dominant_channel.get('channel_name') or 'unknown'}.",
            'medium',
            quality_confidence(quality_status),
        )
        save_step(session, agent_run_id, 4, 'Channel Strategist Agent', 'analysis', 'completed', 'Built channel summary and journey-source evidence.', outputs['channel_summary'])
        current_step = 'opportunity_scoring'
        outputs['opportunity_score'] = opportunity_score(session, country_id, date_from, date_to, request.calculation_version)
        score_values = outputs['opportunity_score'].get('score', {})
        save_metric(session, agent_run_id, 'get_opportunity_score', 'opportunity_score', score_values.get('opportunity_score'), score_values)
        save_recommendation(
            session,
            agent_run_id,
            'market_entry',
            str(score_values.get('recommended_priority') or 'medium'),
            'Use opportunity score as the country priority gate',
            outputs['opportunity_score'].get('explanation') or 'Opportunity score was calculated from market, channel, quality, and competition components.',
            'Keeps country prioritization tied to reusable scoring evidence.',
            str(score_values.get('market_type') or 'market signal'),
            quality_confidence(quality_status),
        )
        save_step(session, agent_run_id, 5, 'Country Analyst Agent', 'scoring', 'completed', 'Calculated opportunity score and priority.', outputs['opportunity_score'])
        if budget_amount is not None:
            current_step = 'budget_strategy'
            outputs['budget_strategy'] = budget_strategy(
                session,
                country_id,
                date_from,
                date_to,
                request.calculation_version,
                budget_amount,
                request.currency_code,
                request.campaign_goal,
                request.risk_appetite,
            )
            for recommendation in outputs['budget_strategy'].get('recommendations', [])[:3]:
                save_recommendation(
                    session,
                    agent_run_id,
                    'budget',
                    'high',
                    str(recommendation),
                    str(recommendation),
                    'Budget recommendation generated from allocation model.',
                    'Expected effect is available in the budget strategy payload.',
                    number_value(outputs['budget_strategy'].get('strategy', {}).get('confidence_score')) or quality_confidence(quality_status),
            )
            save_step(session, agent_run_id, 6, 'Budget Strategist Agent', 'strategy', 'completed', 'Generated budget allocation strategy.', outputs['budget_strategy'])
        current_step = 'country_report'
        outputs['country_report'] = country_report(session, country_id, date_from, date_to, request.calculation_version)
        save_step(session, agent_run_id, 7, 'Report Writer Agent', 'report', 'completed', 'Created reusable country report artifact.', {'report_id': outputs['country_report'].get('report_id')})
        final_answer = build_answer(
            str(country.get('country_name_en') or 'selected country'),
            date_from,
            date_to,
            outputs,
            budget_amount,
            request.currency_code,
        )
        confidence_score = quality_confidence(quality_status)
        update_run(session, agent_run_id, 'completed', final_answer, confidence_score, outputs)
        create_agent_summary(session, agent_run_id)
    except Exception as exc:
        error_text = f'MAS analysis failed: {exc}'
        session.rollback()
        save_step(
            session,
            agent_run_id,
            99,
            'Orchestrator',
            'error',
            'failed',
            error_text,
            {'partial_outputs': outputs, 'failed_step_name': current_step},
        )
        update_run(session, agent_run_id, 'failed', error_text, 0.0, outputs)
        raise
    response = get_run(session, agent_run_id)
    if response is None:
        raise HTTPException(status_code=500, detail='MAS run was not saved.')
    return response
