from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.channel import (
    ChannelRecalculateRequest,
    ChannelRecalculateResponse,
    ChannelSummaryResponse,
    ChannelTrendResponse,
    JourneySourcesResponse,
)
from app.services.channel_analysis_service import build_summary, build_trend
from app.services.channel_scope_service import resolve_scope, validate_dates
from app.services.journey_source_service import build_journey


router = APIRouter(prefix='/channels', tags=['channels'])


@router.get('/summary', response_model=ChannelSummaryResponse)
def get_summary(
    date_from: date,
    date_to: date,
    country_id: int | None = None,
    domain_id: int | None = None,
    calculation_version: str = 'v1',
    recalculate_if_missing: bool = True,
    session: Session = Depends(get_session),
) -> ChannelSummaryResponse:
    """Get channel summary.
    Args:
        date_from (date): Period start date.
        date_to (date): Period end date.
        country_id (int | None): Country identifier.
        domain_id (int | None): Domain identifier.
        calculation_version (str): Calculation version.
        recalculate_if_missing (bool): Recalculate flag.
        session (Session): Database session."""
    period_error = validate_dates(date_from, date_to)
    if period_error:
        raise HTTPException(status_code=400, detail=period_error)
    result = build_summary(session, country_id, domain_id, date_from, date_to, calculation_version)
    return result


@router.get('/trend', response_model=ChannelTrendResponse)
def get_trend(
    date_from: date,
    date_to: date,
    country_id: int | None = None,
    domain_id: int | None = None,
    channel_id: int | None = None,
    session: Session = Depends(get_session),
) -> ChannelTrendResponse:
    """Get channel trend.
    Args:
        date_from (date): Period start date.
        date_to (date): Period end date.
        country_id (int | None): Country identifier.
        domain_id (int | None): Domain identifier.
        channel_id (int | None): Channel identifier.
        session (Session): Database session."""
    period_error = validate_dates(date_from, date_to)
    if period_error:
        raise HTTPException(status_code=400, detail=period_error)
    items = build_trend(session, country_id, domain_id, channel_id, date_from, date_to)
    return {'items': items}


@router.get('/journey-sources', response_model=JourneySourcesResponse)
def get_journey_sources(
    date_from: date,
    date_to: date,
    country_id: int | None = None,
    domain_id: int | None = None,
    channel_id: int | None = None,
    limit: int = Query(30, ge=1, le=200),
    calculation_version: str = 'v1',
    session: Session = Depends(get_session),
) -> JourneySourcesResponse:
    """Get journey sources.
    Args:
        date_from (date): Period start date.
        date_to (date): Period end date.
        country_id (int | None): Country identifier.
        domain_id (int | None): Domain identifier.
        channel_id (int | None): Channel identifier.
        limit (int): Result limit.
        calculation_version (str): Calculation version.
        session (Session): Database session."""
    period_error = validate_dates(date_from, date_to)
    if period_error:
        raise HTTPException(status_code=400, detail=period_error)
    items, warnings = build_journey(
        session,
        country_id,
        domain_id,
        channel_id,
        date_from,
        date_to,
        limit,
        calculation_version,
    )
    return {'items': items, 'warnings': warnings}


@router.post('/recalculate', response_model=ChannelRecalculateResponse)
def post_recalculate(
    request: ChannelRecalculateRequest,
    session: Session = Depends(get_session),
) -> ChannelRecalculateResponse:
    """Recalculate channel metrics.
    Args:
        request (ChannelRecalculateRequest): Recalculation request.
        session (Session): Database session."""
    period_error = validate_dates(request.date_from, request.date_to)
    if period_error:
        raise HTTPException(status_code=400, detail=period_error)
    summary = build_summary(
        session,
        request.country_id,
        request.domain_id,
        request.date_from,
        request.date_to,
        request.calculation_version,
    )
    scope = resolve_scope(session, request.country_id, request.domain_id)
    journey_items, _ = build_journey(
        session,
        request.country_id,
        request.domain_id,
        None,
        request.date_from,
        request.date_to,
        200,
        request.calculation_version,
    )
    response = ChannelRecalculateResponse(
        status='success',
        scope_type=scope.scope_type,
        metrics_created=len(summary.channels),
        journey_source_metrics_created=len(journey_items),
    )
    return response
