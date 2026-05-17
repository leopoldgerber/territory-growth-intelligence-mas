from app.schemas.advanced_strategy import AdvancedAssumptions


def lead_forecast(expected_traffic: float, assumptions: AdvancedAssumptions) -> float:
    """Calculate lead forecast.
    Args:
        expected_traffic (float): Expected traffic.
        assumptions (AdvancedAssumptions): Forecast assumptions."""
    leads = expected_traffic * assumptions.visit_to_lead_rate
    return round(leads, 2)


def client_forecast(expected_leads: float, assumptions: AdvancedAssumptions) -> float:
    """Calculate client forecast.
    Args:
        expected_leads (float): Expected leads.
        assumptions (AdvancedAssumptions): Forecast assumptions."""
    clients = expected_leads * assumptions.lead_to_client_rate
    return round(clients, 2)


def revenue_forecast(expected_clients: float, assumptions: AdvancedAssumptions) -> float:
    """Calculate revenue forecast.
    Args:
        expected_clients (float): Expected clients.
        assumptions (AdvancedAssumptions): Forecast assumptions."""
    revenue = expected_clients * assumptions.lifetime_value
    return round(revenue, 2)
