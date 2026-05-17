from app.schemas.opportunity import OpportunityScoreResponse
from app.schemas.strategy import BudgetAllocationItem


def strategy_type(goal: str, opportunity: OpportunityScoreResponse) -> str:
    """Build strategy type.
    Args:
        goal (str): Campaign goal.
        opportunity (OpportunityScoreResponse): Opportunity score."""
    if opportunity.score.recommended_priority in ['low', 'avoid']:
        return 'limited_monitoring_test'
    if goal == 'aggressive_entry' and opportunity.score.recommended_priority == 'high':
        return 'accelerated_entry'
    if goal == 'growth':
        return 'balanced_growth'
    if goal == 'brand_awareness':
        return 'awareness_first'
    if goal == 'performance':
        return 'performance_validation'
    return 'balanced_market_test'


def summary_text(country_name: str, strategy: str, allocation: list[BudgetAllocationItem]) -> str:
    """Build summary text.
    Args:
        country_name (str): Country name.
        strategy (str): Strategy type.
        allocation (list[BudgetAllocationItem]): Allocation rows."""
    top_channels = ', '.join([item.channel_name or item.channel_code for item in allocation[:2]])
    summary = f'{country_name} is suitable for a {strategy} strategy with initial emphasis on {top_channels}.'
    return summary


def recommendation_list(opportunity: OpportunityScoreResponse, allocation: list[BudgetAllocationItem]) -> list[str]:
    """Build recommendations.
    Args:
        opportunity (OpportunityScoreResponse): Opportunity score.
        allocation (list[BudgetAllocationItem]): Allocation rows."""
    recommendations = ['Start with a controlled market test before scaling.']
    for item in allocation[:3]:
        recommendations.append(item.test_hypothesis)
    if opportunity.score.recommended_priority in ['low', 'avoid']:
        recommendations.append('Limit spend and monitor the country before full campaign launch.')
    else:
        recommendations.append('Review early no-bounce traffic and lead quality before increasing budget.')
    return recommendations


def risk_list(
    opportunity: OpportunityScoreResponse,
    budget_amount: float,
    channel_estimated: bool,
) -> list[str]:
    """Build strategy risks.
    Args:
        opportunity (OpportunityScoreResponse): Opportunity score.
        budget_amount (float): Budget amount.
        channel_estimated (bool): Estimated channel flag."""
    risks = list(opportunity.risks)
    if channel_estimated:
        risks.append('Channel data is estimated from domain-level channel mix.')
    if budget_amount < 1000:
        risks.append('Budget may be too small to test several channels at once.')
    if opportunity.data_quality_status == 'warning':
        risks.append('Strategy is based on data with quality warnings.')
    return risks


def confidence_score(
    opportunity: OpportunityScoreResponse,
    has_channels: bool,
    uses_default_assumptions: bool,
) -> float:
    """Calculate confidence score.
    Args:
        opportunity (OpportunityScoreResponse): Opportunity score.
        has_channels (bool): Channel data flag.
        uses_default_assumptions (bool): Default assumptions flag."""
    quality_map = {'passed': 1.0, 'warning': 0.7, 'failed': 0.0, 'unknown': 0.5}
    data_quality_score = quality_map.get(opportunity.data_quality_status, 0.5)
    channel_score = 1.0 if has_channels else 0.5
    assumptions_score = 0.5 if uses_default_assumptions else 0.8
    confidence = (
        0.30 * data_quality_score
        + 0.25 * opportunity.score.opportunity_score
        + 0.20 * channel_score
        + 0.15 * 1.0
        + 0.10 * assumptions_score
    )
    return max(0.0, min(1.0, confidence))
