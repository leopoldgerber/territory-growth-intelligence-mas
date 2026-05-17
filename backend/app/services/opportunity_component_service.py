from app.schemas.channel import ChannelSummaryResponse
from app.schemas.country import CountryMetricValues


def clamp_score(value: float | None) -> float | None:
    """Clamp score.
    Args:
        value (float | None): Source value."""
    if value is None:
        return None
    return max(0.0, min(1.0, value))


def traffic_score(metrics: CountryMetricValues, traffic_percentile: float | None = None) -> float:
    """Calculate traffic score.
    Args:
        metrics (CountryMetricValues): Country metrics.
        traffic_percentile (float | None): Traffic percentile among countries."""
    no_bounce = metrics.no_bounce_share or 0
    traffic_component = traffic_percentile if traffic_percentile is not None else 0.5
    score = 0.7 * traffic_component + 0.3 * no_bounce
    return clamp_score(score) or 0


def competition_score(metrics: CountryMetricValues) -> float:
    """Calculate competition score.
    Args:
        metrics (CountryMetricValues): Country metrics."""
    active_competitors = metrics.active_competitors_count or 0
    active_score = min(active_competitors / 10, 1)
    leader_score = 1 - (metrics.leader_share or 0)
    hhi_score = 1 - (metrics.market_concentration_hhi or 0)
    score = 0.35 * active_score + 0.35 * leader_score + 0.30 * hhi_score
    return clamp_score(score) or 0


def quality_score(metrics: CountryMetricValues) -> float:
    """Calculate quality score.
    Args:
        metrics (CountryMetricValues): Country metrics."""
    engagement = metrics.engagement_score if metrics.engagement_score is not None else 0.5
    no_bounce = metrics.no_bounce_share if metrics.no_bounce_share is not None else 0.5
    bounce_quality = 1 - metrics.bounce_share if metrics.bounce_share is not None else 0.5
    score = 0.60 * engagement + 0.25 * no_bounce + 0.15 * bounce_quality
    return clamp_score(score) or 0


def channel_score(channel_summary: ChannelSummaryResponse | None, traffic_value: float | None = None) -> float | None:
    """Calculate channel gap score.
    Args:
        channel_summary (ChannelSummaryResponse | None): Channel summary.
        traffic_value (float | None): Traffic component score."""
    if channel_summary is None:
        return None
    dependency = channel_summary.summary.channel_dependency_score
    if dependency is None:
        return None
    share_map = {channel.channel_code: channel.traffic_share or 0 for channel in channel_summary.channels}
    paid_gap = 1 - share_map.get('paid', 0)
    referral_gap = 1 - share_map.get('referral', 0)
    social_gap = 1 - share_map.get('social', 0)
    if traffic_value is not None and traffic_value < 0.4:
        paid_gap *= 0.5
    score = 0.40 * dependency + 0.30 * paid_gap + 0.20 * referral_gap + 0.10 * social_gap
    return clamp_score(score)


def volatility_score(metrics: CountryMetricValues) -> float:
    """Calculate volatility opportunity score.
    Args:
        metrics (CountryMetricValues): Country metrics."""
    raw_value = metrics.market_volatility_score
    if raw_value is None:
        return 0.5
    score = 1 - raw_value
    return clamp_score(score) or 0


def localization_score(metrics: CountryMetricValues, traffic_percentile: float | None = None) -> float:
    """Calculate localization score.
    Args:
        metrics (CountryMetricValues): Country metrics.
        traffic_percentile (float | None): Traffic percentile among countries."""
    demand_score = traffic_percentile if traffic_percentile is not None else 0.5
    bounce_opportunity = metrics.bounce_share or 0
    mobile_opportunity = metrics.mobile_share if metrics.mobile_share is not None and metrics.mobile_share > 0.5 else 0.3
    score = 0.50 * demand_score + 0.30 * bounce_opportunity + 0.20 * mobile_opportunity
    return clamp_score(score) or 0


def difficulty_score(metrics: CountryMetricValues, channel_summary: ChannelSummaryResponse | None) -> float:
    """Calculate difficulty score.
    Args:
        metrics (CountryMetricValues): Country metrics.
        channel_summary (ChannelSummaryResponse | None): Channel summary."""
    direct_share = None
    if channel_summary is not None:
        direct_metric = next((channel for channel in channel_summary.channels if channel.channel_code == 'direct'), None)
        direct_share = direct_metric.traffic_share if direct_metric else None
    if direct_share is None:
        values = [
            metrics.leader_share or 0,
            metrics.top_3_share or 0,
            metrics.market_concentration_hhi or 0,
        ]
        score = sum(values) / len(values)
        return clamp_score(score) or 0
    score = (
        0.35 * (metrics.leader_share or 0)
        + 0.25 * (metrics.top_3_share or 0)
        + 0.20 * (metrics.market_concentration_hhi or 0)
        + 0.20 * direct_share
    )
    return clamp_score(score) or 0


def weighted_score(
    traffic: float,
    competition: float,
    quality: float,
    channel_gap: float | None,
    volatility: float,
    localization: float,
    entry_difficulty: float,
) -> float:
    """Calculate weighted score.
    Args:
        traffic (float): Traffic score.
        competition (float): Competition score.
        quality (float): Quality score.
        channel_gap (float | None): Channel gap score.
        volatility (float): Volatility score.
        localization (float): Localization score.
        entry_difficulty (float): Entry difficulty score."""
    weighted_parts = [
        (traffic, 0.25),
        (competition, 0.20),
        (quality, 0.20),
        (volatility, 0.10),
        (localization, 0.10),
    ]
    if channel_gap is not None:
        weighted_parts.append((channel_gap, 0.15))
    total_weight = sum(weight for _, weight in weighted_parts)
    raw_score = sum(value * weight for value, weight in weighted_parts) / total_weight
    entry_ease = 1 - entry_difficulty
    score = raw_score * (0.7 + 0.3 * entry_ease)
    return clamp_score(score) or 0
