from datetime import date
import json

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.advanced_strategy import AdvancedScoreResponse, AdvancedScoreValues
from app.services.audience_analytics_service import audience_fit
from app.services.backlink_opportunity_service import backlink_opportunity
from app.services.channel_analysis_service import build_summary
from app.services.country_metrics_service import get_metrics
from app.services.opportunity_scoring_service import get_score
from app.services.paid_search_opportunity_service import ppc_opportunity
from app.services.seo_opportunity_service import seo_opportunity


def score_value(value: object) -> float:
    """Normalize score.
    Args:
        value (object): Source value."""
    if value is None:
        return 0.0
    score = float(value)
    if score > 1:
        score = score / 100
    return max(0.0, min(score, 1.0))


def json_text(value: object) -> str:
    """Convert JSON text.
    Args:
        value (object): Source value."""
    text_value = json.dumps(value, default=str)
    return text_value


def safe_channel(session: Session, country_id: int, date_from: date, date_to: date, calculation_version: str) -> object | None:
    """Get safe channel.
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


def safe_score(callable_value: object, fallback: float = 0.0) -> float:
    """Read safe score.
    Args:
        callable_value (object): Score value.
        fallback (float): Fallback value."""
    try:
        value = score_value(callable_value)
    except Exception:
        value = fallback
    return value


def paid_share(channel_summary: object | None) -> float:
    """Get paid share.
    Args:
        channel_summary (object | None): Channel summary."""
    if channel_summary is None:
        return 0.0
    metric = next((channel for channel in channel_summary.channels if channel.channel_code == 'paid'), None)
    value = score_value(metric.traffic_share) if metric else 0.0
    return value


def strategy_type(scores: AdvancedScoreValues) -> str:
    """Choose strategy type.
    Args:
        scores (AdvancedScoreValues): Advanced scores."""
    seo = scores.seo_opportunity_score or 0
    paid = scores.paid_dependency_score or 0
    roi = scores.roi_potential_score or 0
    threat = scores.competitor_threat_score or 0
    audience = scores.audience_fit_score or 0
    if roi < 0.25 or audience < 0.25:
        return 'avoid_or_wait'
    if threat > 0.75 and roi < 0.55:
        return 'defensive_monitoring'
    if seo > 0.65 and paid < 0.55:
        return 'content_led_entry'
    if seo > 0.55 and paid >= 0.35:
        return 'seo_plus_paid_validation'
    if paid >= 0.45 and roi >= 0.45:
        return 'paid_fast_validation'
    if audience >= 0.6 and seo < 0.45:
        return 'localization_first'
    if roi >= 0.7 and threat < 0.65:
        return 'aggressive_growth_push'
    return 'seo_plus_paid_validation'


def score_payload(
    session: Session,
    project_id: int,
    country_id: int,
    date_from: date,
    date_to: date,
    calculation_version: str,
) -> tuple[AdvancedScoreValues, dict[str, object], str]:
    """Calculate score payload.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        calculation_version (str): Calculation version."""
    metrics = get_metrics(session, country_id, date_from, date_to, 'v1', True).metrics
    opportunity = get_score(session, country_id, date_from, date_to, 'v1', True, False)
    channel_summary = safe_channel(session, country_id, date_from, date_to, 'v1')
    seo = seo_opportunity(session, project_id)
    ppc = ppc_opportunity(session, project_id)
    audience = audience_fit(session, project_id, country_id)
    backlinks = backlink_opportunity(session, project_id)
    competitor_threat = (
        score_value(metrics.leader_share) * 0.3
        + score_value(metrics.top_3_share) * 0.25
        + score_value(metrics.market_concentration_hhi) * 0.2
        + score_value(metrics.market_volatility_score) * 0.15
        + paid_share(channel_summary) * 0.1
    )
    diversification = score_value(channel_summary.summary.channel_diversification_score) if channel_summary else 0.0
    market_maturity = (
        min(float(metrics.active_competitors_count or 0) / 10, 1) * 0.25
        + diversification * 0.2
        + score_value(seo.opportunity_score) * 0.2
        + score_value(ppc.opportunity_score) * 0.15
        + score_value(backlinks.opportunity_score) * 0.1
        + (1 - score_value(metrics.market_volatility_score)) * 0.1
    )
    paid_dependency = paid_share(channel_summary) * 0.4 + score_value(ppc.opportunity_score) * 0.4 + min(float(ppc.estimated_cost or 0) / 50000, 1) * 0.2
    seo_score = score_value(seo.opportunity_score)
    audience_score = score_value(audience.audience_fit_score) if audience.audience_fit_score is not None else score_value(opportunity.components.quality_score) * 0.8
    roi_potential = min(((opportunity.score.opportunity_score or 0) / 100) * 0.4 + seo_score * 0.25 + (1 - paid_dependency) * 0.15 + audience_score * 0.2, 1)
    growth_feasibility = (
        score_value(opportunity.score.opportunity_score) * 0.25
        + audience_score * 0.2
        + diversification * 0.2
        + roi_potential * 0.15
        + (1 - score_value(metrics.market_volatility_score)) * 0.1
        + (1 - competitor_threat) * 0.1
    )
    strategic_priority = growth_feasibility * 0.3 + roi_potential * 0.25 + score_value(opportunity.score.opportunity_score) * 0.2 + max(seo_score, score_value(ppc.opportunity_score)) * 0.15 + market_maturity * 0.1
    scores = AdvancedScoreValues(
        competitor_threat_score=round(competitor_threat, 4),
        market_maturity_score=round(market_maturity, 4),
        paid_dependency_score=round(paid_dependency, 4),
        seo_opportunity_score=round(seo_score, 4),
        audience_fit_score=round(audience_score, 4),
        roi_potential_score=round(roi_potential, 4),
        growth_feasibility_score=round(growth_feasibility, 4),
        strategic_priority_score=round(strategic_priority, 4),
    )
    breakdown = {
        'traffic': metrics.total_competitor_traffic,
        'active_competitors': metrics.active_competitors_count,
        'leader_share': metrics.leader_share,
        'top_3_share': metrics.top_3_share,
        'seo_warning': [warning.model_dump() for warning in seo.warnings],
        'ppc_warning': [warning.model_dump() for warning in ppc.warnings],
        'audience_warning': [warning.model_dump() for warning in audience.warnings],
        'calculation_version': calculation_version,
    }
    explanation = 'Advanced scores combine traffic, competitor pressure, channel mix, SEO/PPC data, audience fit, and ROI assumptions.'
    return scores, breakdown, explanation


def save_scores(
    session: Session,
    project_id: int,
    country_id: int,
    date_from: date,
    date_to: date,
    scores: AdvancedScoreValues,
    breakdown: dict[str, object],
    explanation: str,
    calculation_version: str,
) -> AdvancedScoreValues:
    """Save scores.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        scores (AdvancedScoreValues): Score values.
        breakdown (dict[str, object]): Score breakdown.
        explanation (str): Explanation text.
        calculation_version (str): Calculation version."""
    recommended = strategy_type(scores)
    result = session.execute(
        text(
            """
            INSERT INTO advanced_country_scores (
                project_id, country_id, period_start, period_end, competitor_threat_score,
                market_maturity_score, paid_dependency_score, seo_opportunity_score,
                audience_fit_score, roi_potential_score, growth_feasibility_score,
                strategic_priority_score, recommended_strategy_type, score_breakdown,
                explanation, calculation_version
            )
            VALUES (
                :project_id, :country_id, :period_start, :period_end, :competitor_threat_score,
                :market_maturity_score, :paid_dependency_score, :seo_opportunity_score,
                :audience_fit_score, :roi_potential_score, :growth_feasibility_score,
                :strategic_priority_score, :recommended_strategy_type, CAST(:score_breakdown AS jsonb),
                :explanation, :calculation_version
            )
            ON CONFLICT (project_id, country_id, period_start, period_end, calculation_version) DO UPDATE
            SET competitor_threat_score = EXCLUDED.competitor_threat_score,
                market_maturity_score = EXCLUDED.market_maturity_score,
                paid_dependency_score = EXCLUDED.paid_dependency_score,
                seo_opportunity_score = EXCLUDED.seo_opportunity_score,
                audience_fit_score = EXCLUDED.audience_fit_score,
                roi_potential_score = EXCLUDED.roi_potential_score,
                growth_feasibility_score = EXCLUDED.growth_feasibility_score,
                strategic_priority_score = EXCLUDED.strategic_priority_score,
                recommended_strategy_type = EXCLUDED.recommended_strategy_type,
                score_breakdown = EXCLUDED.score_breakdown,
                explanation = EXCLUDED.explanation
            RETURNING advanced_score_id
            """,
        ),
        {
            'project_id': project_id,
            'country_id': country_id,
            'period_start': date_from,
            'period_end': date_to,
            'competitor_threat_score': scores.competitor_threat_score,
            'market_maturity_score': scores.market_maturity_score,
            'paid_dependency_score': scores.paid_dependency_score,
            'seo_opportunity_score': scores.seo_opportunity_score,
            'audience_fit_score': scores.audience_fit_score,
            'roi_potential_score': scores.roi_potential_score,
            'growth_feasibility_score': scores.growth_feasibility_score,
            'strategic_priority_score': scores.strategic_priority_score,
            'recommended_strategy_type': recommended,
            'score_breakdown': json_text(breakdown),
            'explanation': explanation,
            'calculation_version': calculation_version,
        },
    )
    scores.advanced_score_id = int(result.scalar_one())
    session.commit()
    return scores


def calculate_scores(
    session: Session,
    project_id: int,
    country_id: int,
    date_from: date,
    date_to: date,
    calculation_version: str,
) -> AdvancedScoreResponse:
    """Calculate advanced scores.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        calculation_version (str): Calculation version."""
    scores, breakdown, explanation = score_payload(session, project_id, country_id, date_from, date_to, calculation_version)
    scores = save_scores(session, project_id, country_id, date_from, date_to, scores, breakdown, explanation, calculation_version)
    response = AdvancedScoreResponse(
        project_id=project_id,
        country_id=country_id,
        period={'date_from': date_from, 'date_to': date_to, 'days_count': (date_to - date_from).days + 1},
        scores=scores,
        recommended_strategy_type=strategy_type(scores),
        explanation=explanation,
        score_breakdown=breakdown,
    )
    return response


def stored_scores(
    session: Session,
    project_id: int,
    country_id: int,
    calculation_version: str,
) -> AdvancedScoreResponse | None:
    """Get stored scores.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        country_id (int): Country identifier.
        calculation_version (str): Calculation version."""
    result = session.execute(
        text(
            """
            SELECT *
            FROM advanced_country_scores
            WHERE project_id = :project_id
              AND country_id = :country_id
              AND calculation_version = :calculation_version
            ORDER BY created_at DESC
            LIMIT 1
            """,
        ),
        {'project_id': project_id, 'country_id': country_id, 'calculation_version': calculation_version},
    )
    row = result.first()
    if row is None:
        return None
    data = dict(row._mapping)
    scores = AdvancedScoreValues(**{key: data.get(key) for key in AdvancedScoreValues.model_fields})
    response = AdvancedScoreResponse(
        project_id=project_id,
        country_id=country_id,
        period={'date_from': data['period_start'], 'date_to': data['period_end'], 'days_count': (data['period_end'] - data['period_start']).days + 1},
        scores=scores,
        recommended_strategy_type=data.get('recommended_strategy_type') or strategy_type(scores),
        explanation=data.get('explanation') or '',
        score_breakdown=data.get('score_breakdown') or {},
    )
    return response
