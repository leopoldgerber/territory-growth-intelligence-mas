from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.update import (
    UpdateLatestStatus,
    UpdateRunItem,
    UpdateRunList,
    UpdateRunNowRequest,
    UpdateRunQueued,
    UpdateRunStepList,
    UpdateScheduleCreate,
    UpdateScheduleItem,
    UpdateScheduleList,
    UpdateScheduleUpdate,
)
from app.services.job_service import create_job
from app.services.task_dispatcher import enqueue_task
from app.services.update_run_service import create_run, get_run, link_job, list_runs, list_steps, latest_status
from app.services.update_schedule_service import create_schedule, get_schedule, list_schedules, update_schedule


router = APIRouter(tags=['updates'])


@router.get('/update-schedules', response_model=UpdateScheduleList)
def get_update_schedules(
    project_id: int | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
) -> UpdateScheduleList:
    """Get update schedules.
    Args:
        project_id (int | None): Project identifier.
        limit (int): Result limit.
        offset (int): Result offset.
        session (Session): Database session."""
    response = list_schedules(session, project_id, limit, offset)
    return response


@router.post('/update-schedules', response_model=UpdateScheduleItem)
def post_update_schedule(
    request: UpdateScheduleCreate,
    session: Session = Depends(get_session),
) -> UpdateScheduleItem:
    """Create update schedule.
    Args:
        request (UpdateScheduleCreate): Schedule request.
        session (Session): Database session."""
    response = create_schedule(session, request, None)
    return response


@router.patch('/update-schedules/{schedule_id}', response_model=UpdateScheduleItem)
def patch_update_schedule(
    schedule_id: int,
    request: UpdateScheduleUpdate,
    session: Session = Depends(get_session),
) -> UpdateScheduleItem:
    """Update update schedule.
    Args:
        schedule_id (int): Schedule identifier.
        request (UpdateScheduleUpdate): Schedule update.
        session (Session): Database session."""
    response = update_schedule(session, schedule_id, request)
    return response


@router.post('/update-schedules/{schedule_id}/run-now', response_model=UpdateRunQueued)
def post_run_now(
    schedule_id: int,
    request: UpdateRunNowRequest,
    session: Session = Depends(get_session),
) -> UpdateRunQueued:
    """Run schedule now.
    Args:
        schedule_id (int): Schedule identifier.
        request (UpdateRunNowRequest): Run request.
        session (Session): Database session."""
    schedule = get_schedule(session, schedule_id)
    update_run_id = create_run(session, schedule_id, schedule.project_id, request.run_type, request.period_start, request.period_end)
    payload = {
        'schedule_id': schedule_id,
        'update_run_id': update_run_id,
        'period_start': request.period_start,
        'period_end': request.period_end,
    }
    job_id = create_job(session, 'scheduled_update', payload, schedule.project_id, None, 'update_run', update_run_id)
    link_job(session, update_run_id, job_id)
    enqueue_task(
        session,
        job_id,
        'scheduled_update_task',
        [
            job_id,
            update_run_id,
            schedule_id,
            str(request.period_start) if request.period_start else None,
            str(request.period_end) if request.period_end else None,
        ],
    )
    response = UpdateRunQueued(update_run_id=update_run_id, job_id=job_id, status='queued')
    return response


@router.get('/update-runs', response_model=UpdateRunList)
def get_update_runs(
    project_id: int | None = None,
    schedule_id: int | None = None,
    status: str | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
) -> UpdateRunList:
    """Get update runs.
    Args:
        project_id (int | None): Project identifier.
        schedule_id (int | None): Schedule identifier.
        status (str | None): Status filter.
        limit (int): Result limit.
        offset (int): Result offset.
        session (Session): Database session."""
    response = list_runs(session, project_id, schedule_id, status, limit, offset)
    return response


@router.get('/update-runs/{update_run_id}', response_model=UpdateRunItem)
def get_update_run(update_run_id: int, session: Session = Depends(get_session)) -> UpdateRunItem:
    """Get update run.
    Args:
        update_run_id (int): Update run identifier.
        session (Session): Database session."""
    response = get_run(session, update_run_id)
    return response


@router.get('/update-runs/{update_run_id}/steps', response_model=UpdateRunStepList)
def get_update_run_steps(update_run_id: int, session: Session = Depends(get_session)) -> UpdateRunStepList:
    """Get update run steps.
    Args:
        update_run_id (int): Update run identifier.
        session (Session): Database session."""
    response = list_steps(session, update_run_id)
    return response


@router.get('/update-status/latest', response_model=UpdateLatestStatus)
def get_latest_update_status(project_id: int | None = None, session: Session = Depends(get_session)) -> UpdateLatestStatus:
    """Get latest update status.
    Args:
        project_id (int | None): Project identifier.
        session (Session): Database session."""
    response = latest_status(session, project_id)
    return response
