from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.history import (
    HistoryAgentRunList,
    HistoryInsightList,
    HistoryRecommendationList,
    HistoryReportList,
    SavedSummaryCreate,
    SavedSummaryItem,
    SavedSummaryList,
    SavedSummaryUpdate,
)
from app.services.history_service import agent_history, insight_history, recommendation_history, report_history
from app.services.summary_storage_service import create_summary, get_summary, list_summaries, update_summary


router = APIRouter(prefix='/history', tags=['history'])


@router.get('/reports', response_model=HistoryReportList)
def get_history_reports(
    report_type: str | None = None,
    country_id: int | None = None,
    domain_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    search: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
) -> HistoryReportList:
    """Get history reports.
    Args:
        report_type (str | None): Report type.
        country_id (int | None): Country identifier.
        domain_id (int | None): Domain identifier.
        date_from (date | None): Period start filter.
        date_to (date | None): Period end filter.
        search (str | None): Search text.
        limit (int): Result limit.
        offset (int): Result offset.
        session (Session): Database session."""
    result = report_history(session, report_type, country_id, domain_id, date_from, date_to, search, limit, offset)
    response = HistoryReportList(**result)
    return response


@router.get('/agent-runs', response_model=HistoryAgentRunList)
def get_agent_runs(
    country_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    search: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
) -> HistoryAgentRunList:
    """Get agent runs.
    Args:
        country_id (int | None): Country identifier.
        date_from (date | None): Period start filter.
        date_to (date | None): Period end filter.
        search (str | None): Search text.
        limit (int): Result limit.
        offset (int): Result offset.
        session (Session): Database session."""
    result = agent_history(session, country_id, date_from, date_to, search, limit, offset)
    response = HistoryAgentRunList(**result)
    return response


@router.get('/insights', response_model=HistoryInsightList)
def get_insights(
    country_id: int | None = None,
    insight_type: str | None = None,
    severity: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
) -> HistoryInsightList:
    """Get insights.
    Args:
        country_id (int | None): Country identifier.
        insight_type (str | None): Insight type.
        severity (str | None): Severity filter.
        limit (int): Result limit.
        offset (int): Result offset.
        session (Session): Database session."""
    result = insight_history(session, country_id, insight_type, severity, limit, offset)
    response = HistoryInsightList(**result)
    return response


@router.get('/recommendations', response_model=HistoryRecommendationList)
def get_recommendations(
    country_id: int | None = None,
    recommendation_type: str | None = None,
    priority: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
) -> HistoryRecommendationList:
    """Get recommendations.
    Args:
        country_id (int | None): Country identifier.
        recommendation_type (str | None): Recommendation type.
        priority (str | None): Priority filter.
        limit (int): Result limit.
        offset (int): Result offset.
        session (Session): Database session."""
    result = recommendation_history(session, country_id, recommendation_type, priority, limit, offset)
    response = HistoryRecommendationList(**result)
    return response


@router.get('/summaries', response_model=SavedSummaryList)
def get_summaries(
    summary_type: str | None = None,
    country_id: int | None = None,
    domain_id: int | None = None,
    channel_id: int | None = None,
    tag: str | None = None,
    rag_ready: bool | None = None,
    search: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
) -> SavedSummaryList:
    """Get summaries.
    Args:
        summary_type (str | None): Summary type.
        country_id (int | None): Country identifier.
        domain_id (int | None): Domain identifier.
        channel_id (int | None): Channel identifier.
        tag (str | None): Tag filter.
        rag_ready (bool | None): RAG-ready filter.
        search (str | None): Search text.
        limit (int): Result limit.
        offset (int): Result offset.
        session (Session): Database session."""
    result = list_summaries(
        session,
        summary_type,
        country_id,
        domain_id,
        channel_id,
        tag,
        rag_ready,
        search,
        limit,
        offset,
    )
    response = SavedSummaryList(**result)
    return response


@router.post('/summaries', response_model=SavedSummaryItem)
def post_summary(summary: SavedSummaryCreate, session: Session = Depends(get_session)) -> SavedSummaryItem:
    """Create summary.
    Args:
        summary (SavedSummaryCreate): Summary payload.
        session (Session): Database session."""
    summary_id = create_summary(session, summary)
    item = get_summary(session, summary_id)
    if item is None:
        raise HTTPException(status_code=500, detail='Summary was not saved.')
    return item


@router.patch('/summaries/{summary_id}', response_model=SavedSummaryItem)
def patch_summary(
    summary_id: int,
    payload: SavedSummaryUpdate,
    session: Session = Depends(get_session),
) -> SavedSummaryItem:
    """Update summary.
    Args:
        summary_id (int): Summary identifier.
        payload (SavedSummaryUpdate): Update payload.
        session (Session): Database session."""
    item = update_summary(session, summary_id, payload)
    if item is None:
        raise HTTPException(status_code=404, detail='Summary not found.')
    return item
