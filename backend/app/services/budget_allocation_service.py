from app.schemas.channel import ChannelMetric, ChannelSummaryResponse
from app.schemas.opportunity import OpportunityScoreResponse
from app.schemas.strategy import BudgetAllocationItem, BudgetAssumptions
from app.services.budget_effect_service import effect_values


GOAL_WEIGHTS = {
    'market_test': {'paid': 0.35, 'search': 0.25, 'referral': 0.20, 'social': 0.10, 'brand_localization': 0.10},
    'growth': {'search': 0.35, 'paid': 0.25, 'referral': 0.20, 'social': 0.10, 'brand_localization': 0.10},
    'aggressive_entry': {'paid': 0.40, 'search': 0.25, 'referral': 0.15, 'social': 0.10, 'brand_localization': 0.10},
    'brand_awareness': {'social': 0.25, 'referral': 0.25, 'brand_localization': 0.25, 'search': 0.15, 'paid': 0.10},
    'performance': {'paid': 0.40, 'search': 0.35, 'referral': 0.15, 'social': 0.05, 'brand_localization': 0.05},
}


def goal_weights(goal: str) -> dict[str, float]:
    """Get goal weights.
    Args:
        goal (str): Campaign goal."""
    weights = GOAL_WEIGHTS.get(goal, GOAL_WEIGHTS['market_test'])
    return weights


def metric_lookup(channels: list[ChannelMetric]) -> dict[str, ChannelMetric]:
    """Build metric lookup.
    Args:
        channels (list[ChannelMetric]): Channel metrics."""
    lookup = {channel.channel_code: channel for channel in channels}
    return lookup


def category_metric(lookup: dict[str, ChannelMetric], channel_code: str) -> ChannelMetric | None:
    """Get category metric.
    Args:
        lookup (dict[str, ChannelMetric]): Channel lookup.
        channel_code (str): Allocation category code."""
    source_code = 'direct' if channel_code == 'brand_localization' else channel_code
    metric = lookup.get(source_code)
    return metric


def category_name(channel_code: str, metric: ChannelMetric | None) -> str:
    """Build category name.
    Args:
        channel_code (str): Allocation category code.
        metric (ChannelMetric | None): Source channel metric."""
    if channel_code == 'brand_localization':
        return 'Brand localization'
    name = metric.channel_name if metric is not None else channel_code.replace('_', ' ').title()
    return name


def category_id(channel_code: str, metric: ChannelMetric | None) -> int | None:
    """Build category identifier.
    Args:
        channel_code (str): Allocation category code.
        metric (ChannelMetric | None): Source channel metric."""
    if channel_code == 'brand_localization' or metric is None:
        return None
    return metric.channel_id


def base_score(
    channel_code: str,
    base_weight: float,
    metric: ChannelMetric | None,
    risk_appetite: str,
) -> float:
    """Calculate category base score.
    Args:
        channel_code (str): Allocation category code.
        base_weight (float): Goal base weight.
        metric (ChannelMetric | None): Source channel metric.
        risk_appetite (str): Risk appetite."""
    traffic_share = metric.traffic_share if metric is not None and metric.traffic_share is not None else base_weight
    stability_score = metric.stability_score if metric is not None and metric.stability_score is not None else 0.5
    data_weight = 0.70 * traffic_share + 0.30 * stability_score
    score = 0.70 * base_weight + 0.30 * data_weight
    if risk_appetite == 'low' and channel_code in ['paid', 'social']:
        score *= 0.85
    if risk_appetite == 'high' and channel_code in ['paid', 'social']:
        score *= 1.15
    return max(score, 0.05)


def priority_value(share: float) -> str:
    """Build priority value.
    Args:
        share (float): Budget share."""
    if share >= 0.25:
        return 'high'
    if share >= 0.12:
        return 'medium'
    if share >= 0.05:
        return 'low'
    return 'avoid'


def risk_value(channel_code: str, opportunity: OpportunityScoreResponse) -> str:
    """Build risk value.
    Args:
        channel_code (str): Channel code.
        opportunity (OpportunityScoreResponse): Opportunity score."""
    if opportunity.score.recommended_priority in ['low', 'avoid']:
        return 'high'
    if channel_code in ['paid', 'social']:
        return 'medium'
    return 'low'


def rationale_text(channel_code: str) -> str:
    """Build rationale text.
    Args:
        channel_code (str): Allocation category code."""
    if channel_code == 'search':
        return 'Search receives budget because it can validate existing demand through localized search intent.'
    if channel_code == 'paid':
        return 'Paid receives budget because it can test demand quickly before scaling.'
    if channel_code == 'referral':
        return 'Referral receives budget because partner and media sources can reveal local acquisition paths.'
    if channel_code == 'social':
        return 'Social receives budget as a controlled awareness and message testing channel.'
    return 'Brand localization supports trust, landing quality, and local market readiness.'


def hypothesis_text(channel_code: str) -> str:
    """Build hypothesis text.
    Args:
        channel_code (str): Channel code."""
    values = {
        'search': 'Localized search pages can capture existing demand.',
        'paid': 'Controlled paid campaigns can validate demand and traffic quality.',
        'referral': 'Local partners and media can create qualified referral traffic.',
        'social': 'Localized social messaging can identify resonant positioning.',
        'brand_localization': 'Localized brand assets can improve trust and no-bounce traffic.',
    }
    return values.get(channel_code, 'The channel can support the country entry test.')


def success_text(channel_code: str) -> str:
    """Build success metric text.
    Args:
        channel_code (str): Channel code."""
    values = {
        'search': 'No-bounce traffic and lead conversion from search.',
        'paid': 'Cost per qualified lead and no-bounce paid traffic.',
        'referral': 'Qualified referral visits and partner-sourced leads.',
        'social': 'Message engagement and assisted lead conversion.',
        'brand_localization': 'Landing engagement, trust signals, and brand conversion lift.',
    }
    return values.get(channel_code, 'Qualified traffic and lead conversion.')


def fallback_channels(channel_summary: ChannelSummaryResponse | None) -> list[ChannelMetric]:
    """Build fallback channels.
    Args:
        channel_summary (ChannelSummaryResponse | None): Channel summary."""
    if channel_summary is not None and channel_summary.channels:
        return channel_summary.channels
    channels = [
        ChannelMetric(
            channel_id=index,
            channel_code=code,
            channel_name=name,
            traffic=0,
            traffic_share=share,
            stability_score=0.5,
            is_dominant_channel=index == 1,
            dependency_score=share,
            role='secondary',
            interpretation='Fallback allocation channel.',
        )
        for index, (code, name, share) in enumerate(
            [
                ('search', 'Search', 0.35),
                ('paid', 'Paid', 0.30),
                ('referral', 'Referral', 0.20),
                ('social', 'Social', 0.10),
                ('direct', 'Direct', 0.05),
            ],
            start=1,
        )
    ]
    return channels


def scored_categories(
    channels: list[ChannelMetric],
    goal: str,
    risk_appetite: str,
) -> list[tuple[str, ChannelMetric | None, float]]:
    """Score allocation categories.
    Args:
        channels (list[ChannelMetric]): Channel metrics.
        goal (str): Campaign goal.
        risk_appetite (str): Risk appetite."""
    lookup = metric_lookup(channels)
    weights = goal_weights(goal)
    scored = []
    for channel_code, base_weight in weights.items():
        metric = category_metric(lookup, channel_code)
        score = base_score(channel_code, base_weight, metric, risk_appetite)
        scored.append((channel_code, metric, score))
    return scored


def allocate_budget(
    budget_amount: float,
    goal: str,
    risk_appetite: str,
    assumptions: BudgetAssumptions,
    opportunity: OpportunityScoreResponse,
    channel_summary: ChannelSummaryResponse | None,
    available_traffic: float,
) -> list[BudgetAllocationItem]:
    """Allocate budget.
    Args:
        budget_amount (float): Budget amount.
        goal (str): Campaign goal.
        risk_appetite (str): Risk appetite.
        assumptions (BudgetAssumptions): Business assumptions.
        opportunity (OpportunityScoreResponse): Opportunity score.
        channel_summary (ChannelSummaryResponse | None): Channel summary.
        available_traffic (float): Available no-bounce traffic."""
    channels = fallback_channels(channel_summary)
    scored_channels = scored_categories(channels, goal, risk_appetite)
    score_total = sum(score for _, _, score in scored_channels) or 1
    allocation = []
    for channel_code, metric, score in scored_channels:
        budget_share = score / score_total
        expected_traffic, expected_leads, expected_clients = effect_values(
            available_traffic,
            budget_share,
            channel_code,
            assumptions,
        )
        allocation.append(
            BudgetAllocationItem(
                channel_id=category_id(channel_code, metric),
                channel_code=channel_code,
                channel_name=category_name(channel_code, metric),
                budget_share=budget_share,
                budget_amount=budget_amount * budget_share,
                priority=priority_value(budget_share),
                risk_level=risk_value(channel_code, opportunity),
                rationale=rationale_text(channel_code),
                expected_traffic=expected_traffic,
                expected_leads=expected_leads,
                expected_clients=expected_clients,
                test_hypothesis=hypothesis_text(channel_code),
                success_metric=success_text(channel_code),
            ),
        )
    return allocation
