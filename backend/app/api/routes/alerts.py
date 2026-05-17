from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.job import JobQueuedResponse
from app.schemas.alert import AlertDetectRequest, AlertDetectResponse, AlertDetail, AlertList, AlertStatusRequest, AlertSummary
from app.services.alert_detection_service import detect_events
from app.services.alert_storage_service import get_event, list_events, summary_events, update_status
from app.services.job_service import create_job
from app.services.task_dispatcher import enqueue_task


router = APIRouter(prefix='/alerts', tags=['alerts'])


@router.get('/summary', response_model=AlertSummary)
def get_alert_summary(session: Session = Depends(get_session)) -> AlertSummary:
    """Get alert summary.
    Args:
        session (Session): Database session."""
    summary = summary_events(session)
    return summary


@router.post('/detect', response_model=JobQueuedResponse)
def detect_alerts(request: AlertDetectRequest, session: Session = Depends(get_session)) -> JobQueuedResponse:
    """Detect alerts.
    Args:
        request (AlertDetectRequest): Detection request.
        session (Session): Database session."""
    payload = request.model_dump(mode='json')
    job_id = create_job(session, 'alerts_detection', payload, None, None, 'alert_detection', None)
    enqueue_task(session, job_id, 'alerts_detection_task', [job_id, payload])
    response = JobQueuedResponse(
        job_id=job_id,
        status='queued',
        message='Alert detection job queued',
        related_entity_type='alert_detection',
        related_entity_id=None,
    )
    return response


@router.get('', response_model=AlertList)
def get_alerts(
    country_id: int | None = None,
    domain_id: int | None = None,
    channel_id: int | None = None,
    event_type: str | None = None,
    event_category: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
) -> AlertList:
    """Get alerts.
    Args:
        country_id (int | None): Country filter.
        domain_id (int | None): Domain filter.
        channel_id (int | None): Channel filter.
        event_type (str | None): Event type filter.
        event_category (str | None): Event category filter.
        severity (str | None): Severity filter.
        status (str | None): Status filter.
        date_from (date | None): Start date filter.
        date_to (date | None): End date filter.
        limit (int): Result limit.
        offset (int): Result offset.
        session (Session): Database session."""
    filters = {
        'country_id': country_id,
        'domain_id': domain_id,
        'channel_id': channel_id,
        'event_type': event_type,
        'event_category': event_category,
        'severity': severity,
        'status': status,
        'date_from': date_from,
        'date_to': date_to,
    }
    response = list_events(session, filters, limit, offset)
    return response


@router.get('/{anomaly_id}', response_model=AlertDetail)
def get_alert(anomaly_id: int, session: Session = Depends(get_session)) -> AlertDetail:
    """Get alert detail.
    Args:
        anomaly_id (int): Alert identifier.
        session (Session): Database session."""
    detail = get_event(session, anomaly_id)
    return detail


@router.patch('/{anomaly_id}/status', response_model=AlertDetail)
def patch_alert_status(
    anomaly_id: int,
    request: AlertStatusRequest,
    session: Session = Depends(get_session),
) -> AlertDetail:
    """Update alert status.
    Args:
        anomaly_id (int): Alert identifier.
        request (AlertStatusRequest): Status request.
        session (Session): Database session."""
    detail = update_status(session, anomaly_id, request.status)
    return detail
