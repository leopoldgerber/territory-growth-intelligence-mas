from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.schemas.workflow import WorkflowRequest
from app.services.country_query_service import get_country, period_quality, validate_period


CAMPAIGN_GOALS = ['market_test', 'growth', 'aggressive_entry', 'brand_awareness', 'performance']
RISK_APPETITES = ['low', 'medium', 'high']
CURRENCIES = ['EUR', 'USD']


def validate_workflow(session: Session, request: WorkflowRequest) -> str:
    """Validate workflow request.
    Args:
        session (Session): Database session.
        request (WorkflowRequest): Workflow request."""
    country = get_country(session, request.country_id)
    if country is None:
        raise HTTPException(status_code=404, detail='Country not found.')
    period_error = validate_period(session, request.country_id, request.date_from, request.date_to)
    if period_error:
        raise HTTPException(status_code=400, detail=period_error)
    if request.budget_amount is not None and request.budget_amount <= 0:
        raise HTTPException(status_code=400, detail='Budget amount must be positive.')
    if request.campaign_goal not in CAMPAIGN_GOALS:
        raise HTTPException(status_code=400, detail='Invalid campaign goal.')
    if request.risk_appetite not in RISK_APPETITES:
        raise HTTPException(status_code=400, detail='Invalid risk appetite.')
    if request.currency_code[:3].upper() not in CURRENCIES:
        raise HTTPException(status_code=400, detail='Invalid currency code.')
    quality_status = period_quality(session, request.country_id, request.date_from, request.date_to)
    if quality_status == 'failed':
        raise HTTPException(status_code=409, detail='Workflow cannot run on failed quality data.')
    return quality_status
