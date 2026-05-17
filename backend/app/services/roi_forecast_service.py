from app.schemas.advanced_strategy import AdvancedAssumptions


def gross_profit(expected_revenue: float, assumptions: AdvancedAssumptions) -> float:
    """Calculate gross profit.
    Args:
        expected_revenue (float): Expected revenue.
        assumptions (AdvancedAssumptions): Forecast assumptions."""
    profit = expected_revenue * assumptions.gross_margin
    return round(profit, 2)


def cac_value(budget_amount: float, expected_clients: float) -> float | None:
    """Calculate CAC.
    Args:
        budget_amount (float): Budget amount.
        expected_clients (float): Expected clients."""
    if expected_clients <= 0:
        return None
    cac = budget_amount / expected_clients
    return round(cac, 2)


def roi_value(budget_amount: float, expected_gross_profit: float) -> float | None:
    """Calculate ROI.
    Args:
        budget_amount (float): Budget amount.
        expected_gross_profit (float): Expected gross profit."""
    if budget_amount <= 0:
        return None
    roi = (expected_gross_profit - budget_amount) / budget_amount
    return round(roi, 4)


def payback_days(budget_amount: float, expected_gross_profit: float, forecast_days: int) -> int | None:
    """Calculate payback days.
    Args:
        budget_amount (float): Budget amount.
        expected_gross_profit (float): Expected gross profit.
        forecast_days (int): Forecast day count."""
    if expected_gross_profit <= 0:
        return None
    daily_profit = expected_gross_profit / max(forecast_days, 1)
    if daily_profit <= 0:
        return None
    days = int(round(budget_amount / daily_profit))
    return days
