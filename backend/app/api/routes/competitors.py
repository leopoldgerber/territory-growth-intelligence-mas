from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.competitor import (
    CompetitorCountriesResponse,
    CompetitorList,
    CompetitorPeriod,
    CompetitorSignalSet,
    CompetitorSummary,
)
from app.services.competitor_country_service import build_countries, country_rows
from app.services.competitor_query_service import get_competitor, get_period, list_competitors, validate_period
from app.services.competitor_signal_service import build_signals
from app.services.competitor_summary_service import build_competitor_summary


router = APIRouter(prefix='/competitors', tags=['competitors'])


@router.get('', response_model=CompetitorList)
def get_competitors(
    search: str | None = None,
    has_data: bool = True,
    limit: int = Query(100, ge=1, le=300),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
) -> CompetitorList:
    """Get competitors.
    Args:
        search (str | None): Search text.
        has_data (bool): Has data flag.
        limit (int): Result limit.
        offset (int): Result offset.
        session (Session): Database session."""
    result = list_competitors(session, search, has_data, limit, offset)
    return result


@router.get('/{domain_id}/available-period', response_model=CompetitorPeriod)
def get_available_period(domain_id: int, session: Session = Depends(get_session)) -> CompetitorPeriod:
    """Get competitor period.
    Args:
        domain_id (int): Domain identifier.
        session (Session): Database session."""
    competitor = get_competitor(session, domain_id)
    if competitor is None:
        raise HTTPException(status_code=404, detail='Competitor not found.')
    period = get_period(session, domain_id)
    return period


@router.get('/{domain_id}/summary', response_model=CompetitorSummary)
def get_summary(
    domain_id: int,
    date_from: date,
    date_to: date,
    limit_countries: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session),
) -> CompetitorSummary:
    """Get competitor summary.
    Args:
        domain_id (int): Domain identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        limit_countries (int): Country limit.
        session (Session): Database session."""
    period_error = validate_period(session, domain_id, date_from, date_to)
    if period_error:
        raise HTTPException(status_code=400, detail=period_error)
    summary = build_competitor_summary(session, domain_id, date_from, date_to, limit_countries)
    return summary


@router.get('/{domain_id}/countries', response_model=CompetitorCountriesResponse)
def get_countries(
    domain_id: int,
    date_from: date,
    date_to: date,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    sort_by: str = 'traffic',
    sort_order: str = 'desc',
    session: Session = Depends(get_session),
) -> CompetitorCountriesResponse:
    """Get competitor countries.
    Args:
        domain_id (int): Domain identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        limit (int): Result limit.
        offset (int): Result offset.
        sort_by (str): Sort column.
        sort_order (str): Sort order.
        session (Session): Database session."""
    rows = country_rows(session, domain_id, date_from, date_to)
    items = build_countries(rows, date_from, date_to)
    reverse_order = sort_order != 'asc'
    sorted_items = sorted(items, key=lambda item: item.get(sort_by) or 0, reverse=reverse_order)
    return {'items': sorted_items[offset : offset + limit], 'total': len(sorted_items)}


@router.get('/{domain_id}/signals', response_model=CompetitorSignalSet)
def get_signals(
    domain_id: int,
    date_from: date,
    date_to: date,
    session: Session = Depends(get_session),
) -> CompetitorSignalSet:
    """Get competitor signals.
    Args:
        domain_id (int): Domain identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        session (Session): Database session."""
    rows = country_rows(session, domain_id, date_from, date_to)
    items = build_countries(rows, date_from, date_to)
    signals = build_signals(items)
    return signals
