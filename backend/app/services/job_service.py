import json
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.job import JobEventItem, JobEventList, JobItem, JobList


def json_text(value: object) -> str:
    """Convert value to JSON text.
    Args:
        value (object): Source value."""
    serialized_value = json.dumps(value, default=str)
    return serialized_value


def job_value(row: dict[str, object]) -> JobItem:
    """Build job value.
    Args:
        row (dict[str, object]): Job row."""
    data = dict(row)
    for key in ['created_at', 'started_at', 'finished_at', 'updated_at']:
        if data.get(key) is not None:
            data[key] = str(data[key])
    data['progress_percent'] = float(data.get('progress_percent') or 0)
    item = JobItem(**data)
    return item


def event_value(row: dict[str, object]) -> JobEventItem:
    """Build event value.
    Args:
        row (dict[str, object]): Event row."""
    data = dict(row)
    if data.get('created_at') is not None:
        data['created_at'] = str(data['created_at'])
    if data.get('progress_percent') is not None:
        data['progress_percent'] = float(data['progress_percent'])
    item = JobEventItem(**data)
    return item


def create_job(
    session: Session,
    job_type: str,
    input_payload: dict[str, object],
    project_id: int | None = None,
    user_id: int | None = None,
    related_entity_type: str | None = None,
    related_entity_id: int | None = None,
) -> str:
    """Create background job.
    Args:
        session (Session): Database session.
        job_type (str): Job type.
        input_payload (dict[str, object]): Input payload.
        project_id (int | None): Project identifier.
        user_id (int | None): User identifier.
        related_entity_type (str | None): Related entity type.
        related_entity_id (int | None): Related entity identifier."""
    job_id = str(uuid4())
    session.execute(
        text(
            """
            INSERT INTO background_jobs (
                job_id, job_type, status, project_id, user_id, related_entity_type,
                related_entity_id, progress_percent, current_step, input_payload
            )
            VALUES (
                :job_id, :job_type, 'queued', :project_id, :user_id, :related_entity_type,
                :related_entity_id, 0, 'Queued', CAST(:input_payload AS jsonb)
            )
            """,
        ),
        {
            'job_id': job_id,
            'job_type': job_type,
            'project_id': project_id,
            'user_id': user_id,
            'related_entity_type': related_entity_type,
            'related_entity_id': related_entity_id,
            'input_payload': json_text(input_payload),
        },
    )
    add_event(session, job_id, 'queued', 'Queued', 'Job queued', 0, {})
    session.commit()
    return job_id


def set_task_id(session: Session, job_id: str, celery_task_id: str) -> str:
    """Set celery task id.
    Args:
        session (Session): Database session.
        job_id (str): Job identifier.
        celery_task_id (str): Celery task identifier."""
    session.execute(
        text('UPDATE background_jobs SET celery_task_id = :celery_task_id, updated_at = now() WHERE job_id = :job_id'),
        {'job_id': job_id, 'celery_task_id': celery_task_id},
    )
    session.commit()
    return job_id


def add_event(
    session: Session,
    job_id: str,
    event_type: str,
    step_name: str | None,
    message: str | None,
    progress_percent: float | None,
    event_payload: dict[str, object] | None = None,
) -> int:
    """Add job event.
    Args:
        session (Session): Database session.
        job_id (str): Job identifier.
        event_type (str): Event type.
        step_name (str | None): Step name.
        message (str | None): Event message.
        progress_percent (float | None): Progress percent.
        event_payload (dict[str, object] | None): Event payload."""
    result = session.execute(
        text(
            """
            INSERT INTO background_job_events (
                job_id, event_type, step_name, message, progress_percent, event_payload
            )
            VALUES (
                :job_id, :event_type, :step_name, :message, :progress_percent, CAST(:event_payload AS jsonb)
            )
            RETURNING event_id
            """,
        ),
        {
            'job_id': job_id,
            'event_type': event_type,
            'step_name': step_name,
            'message': message,
            'progress_percent': progress_percent,
            'event_payload': json_text(event_payload or {}),
        },
    )
    event_id = int(result.scalar_one())
    return event_id


def update_job(
    session: Session,
    job_id: str,
    status: str,
    progress_percent: float,
    current_step: str,
    result_payload: dict[str, object] | None = None,
    error_message: str | None = None,
) -> str:
    """Update background job.
    Args:
        session (Session): Database session.
        job_id (str): Job identifier.
        status (str): Job status.
        progress_percent (float): Progress percent.
        current_step (str): Current step.
        result_payload (dict[str, object] | None): Result payload.
        error_message (str | None): Error message."""
    session.execute(
        text(
            """
            UPDATE background_jobs
            SET status = :status,
                progress_percent = :progress_percent,
                current_step = :current_step,
                result_payload = CASE WHEN :result_payload IS NULL THEN result_payload ELSE CAST(:result_payload AS jsonb) END,
                error_message = :error_message,
                started_at = CASE WHEN started_at IS NULL AND :status IN ('running', 'success', 'failed') THEN now() ELSE started_at END,
                finished_at = CASE WHEN :status IN ('success', 'failed', 'cancelled', 'partial') THEN now() ELSE finished_at END,
                updated_at = now()
            WHERE job_id = :job_id
            """,
        ),
        {
            'job_id': job_id,
            'status': status,
            'progress_percent': progress_percent,
            'current_step': current_step,
            'result_payload': None if result_payload is None else json_text(result_payload),
            'error_message': error_message,
        },
    )
    session.commit()
    return job_id


def get_job(session: Session, job_id: str) -> JobItem:
    """Get background job.
    Args:
        session (Session): Database session.
        job_id (str): Job identifier."""
    row = session.execute(
        text(
            """
            SELECT
                job_id::text AS job_id,
                job_type,
                status,
                project_id,
                user_id,
                related_entity_type,
                related_entity_id,
                progress_percent,
                current_step,
                result_payload,
                error_message,
                celery_task_id,
                created_at::text AS created_at,
                started_at::text AS started_at,
                finished_at::text AS finished_at,
                updated_at::text AS updated_at
            FROM background_jobs
            WHERE job_id = :job_id
            """,
        ),
        {'job_id': job_id},
    ).first()
    if row is None:
        raise HTTPException(status_code=404, detail='Job not found.')
    item = job_value(dict(row._mapping))
    return item


def list_jobs(
    session: Session,
    project_id: int | None,
    user_id: int | None,
    job_type: str | None,
    status: str | None,
    limit: int,
    offset: int,
) -> JobList:
    """List background jobs.
    Args:
        session (Session): Database session.
        project_id (int | None): Project identifier.
        user_id (int | None): User identifier.
        job_type (str | None): Job type.
        status (str | None): Job status.
        limit (int): Result limit.
        offset (int): Result offset."""
    filters = []
    params: dict[str, object] = {'limit': limit, 'offset': offset}
    if project_id is not None:
        filters.append('project_id = :project_id')
        params['project_id'] = project_id
    if user_id is not None:
        filters.append('user_id = :user_id')
        params['user_id'] = user_id
    if job_type is not None:
        filters.append('job_type = :job_type')
        params['job_type'] = job_type
    if status is not None:
        filters.append('status = :status')
        params['status'] = status
    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ''
    rows = session.execute(
        text(
            f"""
            SELECT *, job_id::text AS job_id, created_at::text AS created_at,
                   started_at::text AS started_at, finished_at::text AS finished_at,
                   updated_at::text AS updated_at, COUNT(*) OVER() AS total
            FROM background_jobs
            {where_clause}
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
            """,
        ),
        params,
    )
    data = [dict(row._mapping) for row in rows]
    total = int(data[0]['total']) if data else 0
    items = [job_value({key: value for key, value in row.items() if key != 'total'}) for row in data]
    return JobList(items=items, total=total)


def list_events(session: Session, job_id: str, after_event_id: int | None = None) -> JobEventList:
    """List job events.
    Args:
        session (Session): Database session.
        job_id (str): Job identifier.
        after_event_id (int | None): Lower event bound."""
    params: dict[str, object] = {'job_id': job_id}
    where_clause = 'job_id = :job_id'
    if after_event_id is not None:
        where_clause = f'{where_clause} AND event_id > :after_event_id'
        params['after_event_id'] = after_event_id
    rows = session.execute(
        text(
            f"""
            SELECT *, job_id::text AS job_id, created_at::text AS created_at, COUNT(*) OVER() AS total
            FROM background_job_events
            WHERE {where_clause}
            ORDER BY event_id ASC
            """,
        ),
        params,
    )
    data = [dict(row._mapping) for row in rows]
    total = int(data[0]['total']) if data else 0
    items = [event_value({key: value for key, value in row.items() if key != 'total'}) for row in data]
    return JobEventList(items=items, total=total)


def cancel_job(session: Session, job_id: str) -> JobItem:
    """Cancel background job.
    Args:
        session (Session): Database session.
        job_id (str): Job identifier."""
    update_job(session, job_id, 'cancelled', 100, 'Cancelled', None, None)
    add_event(session, job_id, 'cancelled', 'Cancelled', 'Job cancelled', 100, {})
    session.commit()
    job = get_job(session, job_id)
    return job
