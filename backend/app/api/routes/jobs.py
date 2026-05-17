import asyncio
import json

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, get_session
from app.schemas.job import JobEventList, JobItem, JobList
from app.services.job_service import cancel_job, get_job, list_events, list_jobs


router = APIRouter(prefix='/jobs', tags=['jobs'])


@router.get('', response_model=JobList)
def get_jobs(
    project_id: int | None = None,
    user_id: int | None = None,
    job_type: str | None = None,
    status: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
) -> JobList:
    """Get jobs.
    Args:
        project_id (int | None): Project identifier.
        user_id (int | None): User identifier.
        job_type (str | None): Job type.
        status (str | None): Job status.
        limit (int): Result limit.
        offset (int): Result offset.
        session (Session): Database session."""
    response = list_jobs(session, project_id, user_id, job_type, status, limit, offset)
    return response


@router.get('/{job_id}', response_model=JobItem)
def get_job_by_id(job_id: str, session: Session = Depends(get_session)) -> JobItem:
    """Get job by id.
    Args:
        job_id (str): Job identifier.
        session (Session): Database session."""
    response = get_job(session, job_id)
    return response


@router.get('/{job_id}/events', response_model=JobEventList)
def get_job_events(job_id: str, session: Session = Depends(get_session)) -> JobEventList:
    """Get job events.
    Args:
        job_id (str): Job identifier.
        session (Session): Database session."""
    response = list_events(session, job_id)
    return response


@router.post('/{job_id}/cancel', response_model=JobItem)
def post_job_cancel(job_id: str, session: Session = Depends(get_session)) -> JobItem:
    """Cancel job.
    Args:
        job_id (str): Job identifier.
        session (Session): Database session."""
    response = cancel_job(session, job_id)
    return response


async def event_stream(job_id: str) -> object:
    """Stream job events.
    Args:
        job_id (str): Job identifier."""
    last_event_id = 0
    while True:
        session = SessionLocal()
        try:
            events = list_events(session, job_id, last_event_id)
            job = get_job(session, job_id)
            for event in events.items:
                last_event_id = event.event_id
                payload = event.model_dump(mode='json')
                yield f"event: {event.event_type}\ndata: {json.dumps(payload)}\n\n"
            if job.status in ['success', 'failed', 'cancelled', 'partial']:
                payload = job.model_dump(mode='json')
                yield f"event: job_status\ndata: {json.dumps(payload)}\n\n"
                break
        finally:
            session.close()
        await asyncio.sleep(1)


@router.get('/{job_id}/stream')
def stream_job(job_id: str) -> StreamingResponse:
    """Stream job.
    Args:
        job_id (str): Job identifier."""
    response = StreamingResponse(event_stream(job_id), media_type='text/event-stream')
    return response
