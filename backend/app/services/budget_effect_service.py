from app.schemas.strategy import BudgetAllocationItem, BudgetAssumptions


CHANNEL_MODIFIERS = {
    'search': 1.10,
    'paid': 1.00,
    'referral': 0.90,
    'social': 0.70,
    'direct': 0.60,
    'brand_localization': 0.60,
}


def effect_values(
    available_traffic: float,
    budget_share: float,
    channel_code: str,
    assumptions: BudgetAssumptions,
) -> tuple[float, float, float]:
    """Calculate expected effect.
    Args:
        available_traffic (float): Available no-bounce traffic.
        budget_share (float): Budget share.
        channel_code (str): Channel code.
        assumptions (BudgetAssumptions): Business assumptions."""
    modifier = CHANNEL_MODIFIERS.get(channel_code, 0.75)
    expected_traffic = available_traffic * budget_share * assumptions.traffic_capture_rate * modifier
    expected_leads = expected_traffic * assumptions.visit_to_lead_rate
    expected_clients = expected_leads * assumptions.lead_to_client_rate
    return expected_traffic, expected_leads, expected_clients


def total_effect(allocation: list[BudgetAllocationItem]) -> dict[str, float]:
    """Calculate total effect.
    Args:
        allocation (list[BudgetAllocationItem]): Allocation rows."""
    effect = {
        'expected_traffic': sum(item.expected_traffic for item in allocation),
        'expected_leads': sum(item.expected_leads for item in allocation),
        'expected_clients': sum(item.expected_clients for item in allocation),
    }
    return effect
