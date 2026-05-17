from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.strategy import BudgetStrategyList, BudgetStrategyRequest, BudgetStrategyResponse
from app.services.budget_strategy_service import archive_strategy, generate_strategy, get_strategy, list_strategies


router = APIRouter(prefix='/strategy', tags=['strategy'])


@router.post('/budget', response_model=BudgetStrategyResponse)
def post_budget_strategy(
    request: BudgetStrategyRequest,
    session: Session = Depends(get_session),
) -> BudgetStrategyResponse:
    """Create budget strategy.
    Args:
        request (BudgetStrategyRequest): Strategy request.
        session (Session): Database session."""
    result = generate_strategy(session, request)
    return result


@router.get('/budget', response_model=BudgetStrategyList)
def get_budget_strategies(
    country_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    campaign_goal: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
) -> BudgetStrategyList:
    """Get budget strategies.
    Args:
        country_id (int | None): Country identifier.
        date_from (date | None): Period start date.
        date_to (date | None): Period end date.
        campaign_goal (str | None): Campaign goal.
        limit (int): Result limit.
        offset (int): Result offset.
        session (Session): Database session."""
    result = list_strategies(session, country_id, date_from, date_to, campaign_goal, limit, offset)
    return result


@router.get('/budget/{strategy_id}', response_model=BudgetStrategyResponse)
def get_budget_strategy(strategy_id: int, session: Session = Depends(get_session)) -> BudgetStrategyResponse:
    """Get budget strategy.
    Args:
        strategy_id (int): Strategy identifier.
        session (Session): Database session."""
    result = get_strategy(session, strategy_id)
    return result


@router.post('/budget/{strategy_id}/archive', response_model=BudgetStrategyResponse)
def post_archive_strategy(strategy_id: int, session: Session = Depends(get_session)) -> BudgetStrategyResponse:
    """Archive budget strategy.
    Args:
        strategy_id (int): Strategy identifier.
        session (Session): Database session."""
    result = archive_strategy(session, strategy_id)
    return result
