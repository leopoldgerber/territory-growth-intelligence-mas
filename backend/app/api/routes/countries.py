from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.country import (
    CompetitorList,
    CountryList,
    CountryMetricRequest,
    CountryMetricsResponse,
    CountryPeriod,
    CountrySummary,
    DailyMetricsResponse,
    MetricRecalculateResponse,
)
from app.schemas.opportunity import (
    OpportunityRecalculateRequest,
    OpportunityRecalculateResponse,
    OpportunityScoreResponse,
)
from app.services.country_competitor_service import list_competitors
from app.services.country_metrics_service import daily_metrics, get_metrics, recalculate_metrics
from app.services.country_query_service import get_country, get_period, list_countries, validate_period
from app.services.country_summary_service import build_country_summary
from app.services.opportunity_scoring_service import calculate_score, get_score


router = APIRouter(prefix='/countries', tags=['countries'])


@router.get('', response_model=CountryList)
def get_countries(
    search: str | None = None,
    has_data: bool = True,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
) -> CountryList:
    """Get countries.
    Args:
        search (str | None): Search text.
        has_data (bool): Has data filter.
        limit (int): Result limit.
        offset (int): Result offset.
        session (Session): Database session."""
    result = list_countries(session, search, has_data, limit, offset)
    return result


@router.get('/{country_id}/available-period', response_model=CountryPeriod)
def get_available_period(country_id: int, session: Session = Depends(get_session)) -> CountryPeriod:
    """Get available period.
    Args:
        country_id (int): Country identifier.
        session (Session): Database session."""
    country = get_country(session, country_id)
    if country is None:
        raise HTTPException(status_code=404, detail='Country not found.')
    period = get_period(session, country_id)
    return period


@router.get('/{country_id}/summary', response_model=CountrySummary)
def get_country_summary(
    country_id: int,
    date_from: date,
    date_to: date,
    limit_competitors: int = Query(10, ge=1, le=100),
    session: Session = Depends(get_session),
) -> CountrySummary:
    """Get country summary.
    Args:
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        limit_competitors (int): Top competitors limit.
        session (Session): Database session."""
    country = get_country(session, country_id)
    if country is None:
        raise HTTPException(status_code=404, detail='Country not found.')
    period_error = validate_period(session, country_id, date_from, date_to)
    if period_error == 'NO_DATA_FOR_COUNTRY':
        raise HTTPException(status_code=404, detail='No data found for selected country and period.')
    if period_error == 'INVALID_PERIOD':
        raise HTTPException(status_code=400, detail='Selected period is invalid.')
    if period_error == 'PERIOD_OUT_OF_RANGE':
        raise HTTPException(status_code=400, detail='Selected period is outside available data range.')
    result = build_country_summary(session, country, date_from, date_to, limit_competitors)
    return result


@router.get('/{country_id}/competitors', response_model=CompetitorList)
def get_competitors(
    country_id: int,
    date_from: date,
    date_to: date,
    limit: int = Query(50, ge=1, le=200),
    sort_by: str = 'traffic',
    sort_order: str = 'desc',
    session: Session = Depends(get_session),
) -> CompetitorList:
    """Get country competitors.
    Args:
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        limit (int): Result limit.
        sort_by (str): Sort column.
        sort_order (str): Sort order.
        session (Session): Database session."""
    country = get_country(session, country_id)
    if country is None:
        raise HTTPException(status_code=404, detail='Country not found.')
    period_error = validate_period(session, country_id, date_from, date_to)
    if period_error:
        raise HTTPException(status_code=400, detail=period_error)
    result = list_competitors(session, country_id, date_from, date_to, limit, sort_by, sort_order)
    return result


@router.post('/{country_id}/metrics/recalculate', response_model=MetricRecalculateResponse)
def recalculate_country_metrics(
    country_id: int,
    request: CountryMetricRequest,
    session: Session = Depends(get_session),
) -> MetricRecalculateResponse:
    """Recalculate country metrics.
    Args:
        country_id (int): Country identifier.
        request (CountryMetricRequest): Metric calculation request.
        session (Session): Database session."""
    country = get_country(session, country_id)
    if country is None:
        raise HTTPException(status_code=404, detail='Country not found.')
    period_error = validate_period(session, country_id, request.date_from, request.date_to)
    if period_error:
        raise HTTPException(status_code=400, detail=period_error)
    result = recalculate_metrics(
        session,
        country_id,
        request.date_from,
        request.date_to,
        request.calculation_version,
    )
    warning = 'Metrics were calculated from data with quality warnings.' if result.get('quality_status') == 'warning' else None
    response = MetricRecalculateResponse(
        country_id=country_id,
        period_start=request.date_from,
        period_end=request.date_to,
        status='success',
        metrics=get_metrics(
            session,
            country_id,
            request.date_from,
            request.date_to,
            request.calculation_version,
            False,
        ).metrics,
        warning=warning,
    )
    return response


@router.get('/{country_id}/metrics', response_model=CountryMetricsResponse)
def get_country_metrics(
    country_id: int,
    date_from: date,
    date_to: date,
    calculation_version: str = 'v1',
    recalculate_if_missing: bool = True,
    session: Session = Depends(get_session),
) -> CountryMetricsResponse:
    """Get country metrics.
    Args:
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        calculation_version (str): Calculation version.
        recalculate_if_missing (bool): Recalculate missing metrics flag.
        session (Session): Database session."""
    country = get_country(session, country_id)
    if country is None:
        raise HTTPException(status_code=404, detail='Country not found.')
    period_error = validate_period(session, country_id, date_from, date_to)
    if period_error:
        raise HTTPException(status_code=400, detail=period_error)
    result = get_metrics(session, country_id, date_from, date_to, calculation_version, recalculate_if_missing)
    return result


@router.get('/{country_id}/metrics/daily', response_model=DailyMetricsResponse)
def get_daily_metrics(
    country_id: int,
    date_from: date,
    date_to: date,
    session: Session = Depends(get_session),
) -> DailyMetricsResponse:
    """Get daily metrics.
    Args:
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        session (Session): Database session."""
    country = get_country(session, country_id)
    if country is None:
        raise HTTPException(status_code=404, detail='Country not found.')
    rows = daily_metrics(session, country_id, date_from, date_to)
    return {'country_id': country_id, 'items': rows}


@router.get('/{country_id}/opportunity-score', response_model=OpportunityScoreResponse)
def get_opportunity_score(
    country_id: int,
    date_from: date,
    date_to: date,
    calculation_version: str = 'v1',
    calculate_if_missing: bool = True,
    force_recalculate: bool = False,
    recalculate_if_missing: bool | None = None,
    session: Session = Depends(get_session),
) -> OpportunityScoreResponse:
    """Get opportunity score.
    Args:
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        calculation_version (str): Calculation version.
        calculate_if_missing (bool): Calculate missing score flag.
        force_recalculate (bool): Force recalculation flag.
        recalculate_if_missing (bool | None): Legacy calculate missing score flag.
        session (Session): Database session."""
    country = get_country(session, country_id)
    if country is None:
        raise HTTPException(status_code=404, detail='Country not found.')
    period_error = validate_period(session, country_id, date_from, date_to)
    if period_error:
        raise HTTPException(status_code=400, detail=period_error)
    resolved_calculate = calculate_if_missing if recalculate_if_missing is None else recalculate_if_missing
    result = get_score(
        session,
        country_id,
        date_from,
        date_to,
        calculation_version,
        resolved_calculate,
        force_recalculate,
    )
    return result


@router.post('/{country_id}/opportunity-score/recalculate', response_model=OpportunityRecalculateResponse)
def recalculate_opportunity_score(
    country_id: int,
    request: OpportunityRecalculateRequest,
    session: Session = Depends(get_session),
) -> OpportunityRecalculateResponse:
    """Recalculate opportunity score.
    Args:
        country_id (int): Country identifier.
        request (OpportunityRecalculateRequest): Recalculation request.
        session (Session): Database session."""
    country = get_country(session, country_id)
    if country is None:
        raise HTTPException(status_code=404, detail='Country not found.')
    period_error = validate_period(session, country_id, request.date_from, request.date_to)
    if period_error:
        raise HTTPException(status_code=400, detail=period_error)
    result = calculate_score(session, country_id, request.date_from, request.date_to, request.calculation_version)
    response = OpportunityRecalculateResponse(
        country_id=country_id,
        status='success',
        opportunity_score=result.score.opportunity_score,
        recommended_priority=result.score.recommended_priority,
        market_type=result.score.market_type,
    )
    return response
