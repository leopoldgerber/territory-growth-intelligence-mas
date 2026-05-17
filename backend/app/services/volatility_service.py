import statistics


def volatility_score(traffic_values: list[float], leader_ids: list[int | None]) -> float | None:
    """Calculate volatility score.
    Args:
        traffic_values (list[float]): Daily traffic values.
        leader_ids (list[int | None]): Daily leader identifiers."""
    if len(traffic_values) < 2:
        return None
    average_traffic = statistics.fmean(traffic_values)
    if average_traffic == 0:
        traffic_score = 0
    else:
        traffic_score = min(statistics.pstdev(traffic_values) / average_traffic, 1)
    leader_changes = 0
    previous_leader = leader_ids[0] if leader_ids else None
    for leader_id in leader_ids[1:]:
        if leader_id != previous_leader:
            leader_changes += 1
        previous_leader = leader_id
    leader_score = leader_changes / max(1, len(leader_ids) - 1)
    score = (0.75 * traffic_score) + (0.25 * leader_score)
    return score
