from datetime import date

from app.schemas.advanced_strategy import AdvancedAssumptions, AdvancedScoreValues


SCENARIO_FACTORS = {
    'conservative': 0.55,
    'base': 1.0,
    'aggressive': 1.65,
}

CONFIDENCE_FACTORS = {
    'conservative': 0.78,
    'base': 0.66,
    'aggressive': 0.48,
}


def forecast_days(forecast_start: date | None, forecast_end: date | None) -> int:
    """Calculate forecast days.
    Args:
        forecast_start (date | None): Forecast start date.
        forecast_end (date | None): Forecast end date."""
    if forecast_start is None or forecast_end is None:
        return 90
    days_count = max((forecast_end - forecast_start).days + 1, 1)
    return days_count


def capture_rate(scores: AdvancedScoreValues, assumptions: AdvancedAssumptions, scenario_name: str) -> float:
    """Calculate capture rate.
    Args:
        scores (AdvancedScoreValues): Advanced scores.
        assumptions (AdvancedAssumptions): Assumptions.
        scenario_name (str): Scenario name."""
    feasibility = scores.growth_feasibility_score or 0.35
    priority = scores.strategic_priority_score or 0.35
    threat = scores.competitor_threat_score or 0.4
    factor = SCENARIO_FACTORS.get(scenario_name, 1.0)
    rate = assumptions.traffic_capture_rate * factor * (0.5 + feasibility) * (0.7 + priority) * (1.1 - min(threat, 0.9))
    return max(rate, 0.001)


def traffic_capture(
    market_traffic: float,
    scores: AdvancedScoreValues,
    assumptions: AdvancedAssumptions,
    scenario_name: str,
    forecast_start: date | None,
    forecast_end: date | None,
) -> float:
    """Calculate traffic capture.
    Args:
        market_traffic (float): Market traffic value.
        scores (AdvancedScoreValues): Advanced scores.
        assumptions (AdvancedAssumptions): Assumptions.
        scenario_name (str): Scenario name.
        forecast_start (date | None): Forecast start date.
        forecast_end (date | None): Forecast end date."""
    days_count = forecast_days(forecast_start, forecast_end)
    monthly_factor = days_count / 30
    traffic = market_traffic * capture_rate(scores, assumptions, scenario_name) * monthly_factor
    return round(traffic, 2)


def confidence_score(scores: AdvancedScoreValues, scenario_name: str, has_assumptions: bool, has_campaigns: bool) -> float:
    """Calculate confidence score.
    Args:
        scores (AdvancedScoreValues): Advanced scores.
        scenario_name (str): Scenario name.
        has_assumptions (bool): Assumptions availability flag.
        has_campaigns (bool): Campaign results availability flag."""
    base_confidence = CONFIDENCE_FACTORS.get(scenario_name, 0.6)
    score_bonus = ((scores.strategic_priority_score or 0.4) - 0.4) * 0.2
    assumption_penalty = 0 if has_assumptions else 0.12
    campaign_bonus = 0.08 if has_campaigns else 0
    confidence = max(0.1, min(base_confidence + score_bonus + campaign_bonus - assumption_penalty, 0.95))
    return round(confidence, 4)
