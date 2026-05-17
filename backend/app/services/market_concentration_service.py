from app.services.country_query_service import ratio_value


def hhi_score(traffic_values: list[float]) -> float | None:
    """Calculate HHI score.
    Args:
        traffic_values (list[float]): Competitor traffic values."""
    total_traffic = sum(traffic_values)
    if total_traffic == 0:
        return None
    score = sum((traffic / total_traffic) ** 2 for traffic in traffic_values)
    return score


def top_share(traffic_values: list[float], top_count: int) -> float | None:
    """Calculate top share.
    Args:
        traffic_values (list[float]): Competitor traffic values.
        top_count (int): Top competitor count."""
    total_traffic = sum(traffic_values)
    top_traffic = sum(sorted(traffic_values, reverse=True)[:top_count])
    share = ratio_value(top_traffic, total_traffic)
    return share
