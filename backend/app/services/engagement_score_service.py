from app.services.country_query_service import ratio_value


def clamp_value(value: float | None) -> float | None:
    """Clamp score value.
    Args:
        value (float | None): Source value."""
    if value is None:
        return None
    clamped_value = max(0, min(1, value))
    return clamped_value


def average_score(values: list[tuple[float | None, float]]) -> float | None:
    """Calculate weighted score.
    Args:
        values (list[tuple[float | None, float]]): Score values with weights."""
    available_values = [(value, weight) for value, weight in values if value is not None]
    total_weight = sum(weight for _, weight in available_values)
    if total_weight == 0:
        return None
    score = sum((value or 0) * weight for value, weight in available_values) / total_weight
    return score


def engagement_score(
    no_bounce_share: float | None,
    avg_bounce_rate: float | None,
    avg_pages_per_visit: float | None,
    avg_visit_duration_seconds: float | None,
) -> float | None:
    """Calculate engagement score.
    Args:
        no_bounce_share (float | None): No-bounce share.
        avg_bounce_rate (float | None): Average bounce rate.
        avg_pages_per_visit (float | None): Average pages per visit.
        avg_visit_duration_seconds (float | None): Average visit duration."""
    no_bounce_score = clamp_value(no_bounce_share)
    inverse_bounce_score = None if avg_bounce_rate is None else 1 - (clamp_value(avg_bounce_rate) or 0)
    duration_score = clamp_value(ratio_value(avg_visit_duration_seconds, 300))
    pages_score = clamp_value(ratio_value(avg_pages_per_visit, 5))
    score = average_score(
        [
            (no_bounce_score, 0.40),
            (duration_score, 0.25),
            (pages_score, 0.25),
            (inverse_bounce_score, 0.10),
        ],
    )
    return score
