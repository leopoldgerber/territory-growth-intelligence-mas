import json
from datetime import date

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.update import UpdateLatestStatus, UpdateRunItem, UpdateRunList, UpdateRunStepItem, UpdateRunStepList


def json_text(value: object) -> str:
    """Convert value to JSON text.
    Args:
        value (object): Source value."""
    serialized_value = json.dumps(value, default=str)
    return serialized_value


def run_item(row: dict[str, object]) -> UpdateRunItem:
    """Build update run item.
    Args:
        row (dict[str, object]): Update run row."""
    data = dict(row)
    if data.get('job_id') is not None:
        data['job_id'] = str(data['job_id'])
    for key in ['started_at', 'finished_at', 'created_at']:
        if data.get(key) is not None:
            data[key] = str(data[key])
    item = UpdateRunItem(**data)
    return item


def step_item(row: dict[str, object]) -> UpdateRunStepItem:
    """Build update step item.
    Args:
        row (dict[str, object]): Step row."""
    data = dict(row)
    for key in ['started_at', 'finished_at']:
        if data.get(key) is not None:
            data[key] = str(data[key])
    item = UpdateRunStepItem(**data)
    return item


def active_run(session: Session, schedule_id: int) -> int | None:
    """Get active update run.
    Args:
        session (Session): Database session.
        schedule_id (int): Schedule identifier."""
    value = session.execute(
        text(
            """
            SELECT update_run_id
            FROM update_runs
            WHERE schedule_id = :schedule_id
              AND status IN ('queued', 'running')
            ORDER BY created_at DESC
            LIMIT 1
            """,
        ),
        {'schedule_id': schedule_id},
    ).scalar_one_or_none()
    run_id = None if value is None else int(value)
    return run_id


def create_run(
    session: Session,
    schedule_id: int | None,
    project_id: int | None,
    run_type: str,
    period_start: date | None,
    period_end: date | None,
) -> int:
    """Create update run.
    Args:
        session (Session): Database session.
        schedule_id (int | None): Schedule identifier.
        project_id (int | None): Project identifier.
        run_type (str): Run type.
        period_start (date | None): Period start.
        period_end (date | None): Period end."""
    if schedule_id is not None and active_run(session, schedule_id) is not None:
        raise HTTPException(status_code=409, detail='Update schedule already has an active run.')
    result = session.execute(
        text(
            """
            INSERT INTO update_runs (schedule_id, project_id, run_type, status, period_start, period_end)
            VALUES (:schedule_id, :project_id, :run_type, 'queued', :period_start, :period_end)
            RETURNING update_run_id
            """,
        ),
        {
            'schedule_id': schedule_id,
            'project_id': project_id,
            'run_type': run_type,
            'period_start': period_start,
            'period_end': period_end,
        },
    )
    run_id = int(result.scalar_one())
    session.commit()
    return run_id


def link_job(session: Session, update_run_id: int, job_id: str) -> int:
    """Link update run job.
    Args:
        session (Session): Database session.
        update_run_id (int): Update run identifier.
        job_id (str): Job identifier."""
    session.execute(
        text('UPDATE update_runs SET job_id = :job_id WHERE update_run_id = :update_run_id'),
        {'update_run_id': update_run_id, 'job_id': job_id},
    )
    session.commit()
    return update_run_id


def add_step(
    session: Session,
    update_run_id: int,
    step_order: int,
    step_name: str,
    step_status: str,
    message: str,
    details: dict[str, object] | None = None,
) -> int:
    """Add update run step.
    Args:
        session (Session): Database session.
        update_run_id (int): Update run identifier.
        step_order (int): Step order.
        step_name (str): Step name.
        step_status (str): Step status.
        message (str): Step message.
        details (dict[str, object] | None): Step details."""
    result = session.execute(
        text(
            """
            INSERT INTO update_run_steps (
                update_run_id, step_order, step_name, step_status, started_at, finished_at, message, details
            )
            VALUES (
                :update_run_id, :step_order, :step_name, :step_status, now(), now(), :message, CAST(:details AS jsonb)
            )
            RETURNING update_run_step_id
            """,
        ),
        {
            'update_run_id': update_run_id,
            'step_order': step_order,
            'step_name': step_name,
            'step_status': step_status,
            'message': message,
            'details': json_text(details or {}),
        },
    )
    step_id = int(result.scalar_one())
    session.commit()
    return step_id


def update_run(
    session: Session,
    update_run_id: int,
    status: str,
    files_imported_count: int,
    rows_loaded_count: int,
    quality_status: str,
    metrics_recalculated: bool,
    scores_recalculated: bool,
    alerts_detected_count: int,
    result_payload: dict[str, object],
    ingestion_run_id: int | None = None,
    error_message: str | None = None,
) -> int:
    """Update update run.
    Args:
        session (Session): Database session.
        update_run_id (int): Update run identifier.
        status (str): Run status.
        files_imported_count (int): Imported files count.
        rows_loaded_count (int): Loaded rows count.
        quality_status (str): Quality status.
        metrics_recalculated (bool): Metrics flag.
        scores_recalculated (bool): Scores flag.
        alerts_detected_count (int): Alerts count.
        result_payload (dict[str, object]): Result payload.
        ingestion_run_id (int | None): Ingestion run identifier.
        error_message (str | None): Error message."""
    session.execute(
        text(
            """
            UPDATE update_runs
            SET status = :status,
                ingestion_run_id = COALESCE(:ingestion_run_id, ingestion_run_id),
                started_at = COALESCE(started_at, now()),
                finished_at = CASE WHEN :status IN ('success', 'partial', 'failed', 'cancelled') THEN now() ELSE finished_at END,
                files_imported_count = :files_imported_count,
                rows_loaded_count = :rows_loaded_count,
                quality_status = :quality_status,
                metrics_recalculated = :metrics_recalculated,
                scores_recalculated = :scores_recalculated,
                alerts_detected_count = :alerts_detected_count,
                error_message = :error_message,
                result_payload = CAST(:result_payload AS jsonb)
            WHERE update_run_id = :update_run_id
            """,
        ),
        {
            'update_run_id': update_run_id,
            'status': status,
            'ingestion_run_id': ingestion_run_id,
            'files_imported_count': files_imported_count,
            'rows_loaded_count': rows_loaded_count,
            'quality_status': quality_status,
            'metrics_recalculated': metrics_recalculated,
            'scores_recalculated': scores_recalculated,
            'alerts_detected_count': alerts_detected_count,
            'error_message': error_message,
            'result_payload': json_text(result_payload),
        },
    )
    session.commit()
    return update_run_id


def get_run(session: Session, update_run_id: int) -> UpdateRunItem:
    """Get update run.
    Args:
        session (Session): Database session.
        update_run_id (int): Update run identifier."""
    row = session.execute(
        text(
            """
            SELECT *, job_id::text AS job_id, started_at::text AS started_at,
                   finished_at::text AS finished_at, created_at::text AS created_at
            FROM update_runs
            WHERE update_run_id = :update_run_id
            """,
        ),
        {'update_run_id': update_run_id},
    ).first()
    if row is None:
        raise HTTPException(status_code=404, detail='Update run not found.')
    item = run_item(dict(row._mapping))
    return item


def list_runs(
    session: Session,
    project_id: int | None,
    schedule_id: int | None,
    status: str | None,
    limit: int,
    offset: int,
) -> UpdateRunList:
    """List update runs.
    Args:
        session (Session): Database session.
        project_id (int | None): Project identifier.
        schedule_id (int | None): Schedule identifier.
        status (str | None): Status filter.
        limit (int): Result limit.
        offset (int): Result offset."""
    filters = []
    params: dict[str, object] = {'limit': limit, 'offset': offset}
    if project_id is not None:
        filters.append('project_id = :project_id')
        params['project_id'] = project_id
    if schedule_id is not None:
        filters.append('schedule_id = :schedule_id')
        params['schedule_id'] = schedule_id
    if status is not None:
        filters.append('status = :status')
        params['status'] = status
    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ''
    rows = session.execute(
        text(
            f"""
            SELECT *, job_id::text AS job_id, started_at::text AS started_at,
                   finished_at::text AS finished_at, created_at::text AS created_at,
                   COUNT(*) OVER() AS total
            FROM update_runs
            {where_clause}
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
            """,
        ),
        params,
    )
    data = [dict(row._mapping) for row in rows]
    total = int(data[0]['total']) if data else 0
    items = [run_item({key: value for key, value in row.items() if key != 'total'}) for row in data]
    return UpdateRunList(items=items, total=total)


def list_steps(session: Session, update_run_id: int) -> UpdateRunStepList:
    """List update run steps.
    Args:
        session (Session): Database session.
        update_run_id (int): Update run identifier."""
    rows = session.execute(
        text(
            """
            SELECT *, started_at::text AS started_at, finished_at::text AS finished_at, COUNT(*) OVER() AS total
            FROM update_run_steps
            WHERE update_run_id = :update_run_id
            ORDER BY step_order, update_run_step_id
            """,
        ),
        {'update_run_id': update_run_id},
    )
    data = [dict(row._mapping) for row in rows]
    total = int(data[0]['total']) if data else 0
    items = [step_item({key: value for key, value in row.items() if key != 'total'}) for row in data]
    return UpdateRunStepList(items=items, total=total)


def latest_status(session: Session, project_id: int | None) -> UpdateLatestStatus:
    """Get latest update status.
    Args:
        session (Session): Database session.
        project_id (int | None): Project identifier."""
    filters = []
    params: dict[str, object] = {}
    if project_id is not None:
        filters.append('project_id = :project_id')
        params['project_id'] = project_id
    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ''
    row = session.execute(
        text(
            f"""
            SELECT *
            FROM update_runs
            {where_clause}
            ORDER BY created_at DESC
            LIMIT 1
            """,
        ),
        params,
    ).first()
    if row is None:
        return UpdateLatestStatus(
            project_id=project_id,
            latest_data_period={'date_from': None, 'date_to': None},
            quality_status='unknown',
            alerts_detected_count=0,
            data_freshness_status='missing',
        )
    data = dict(row._mapping)
    freshness = 'fresh' if data['status'] == 'success' else 'failed_recently' if data['status'] == 'failed' else 'stale'
    status_value = UpdateLatestStatus(
        project_id=project_id,
        last_successful_update_at=str(data.get('finished_at')) if data.get('status') == 'success' else None,
        last_update_status=str(data.get('status')),
        latest_data_period={'date_from': data.get('period_start'), 'date_to': data.get('period_end')},
        quality_status=str(data.get('quality_status') or 'unknown'),
        alerts_detected_count=int(data.get('alerts_detected_count') or 0),
        data_freshness_status=freshness,
    )
    return status_value
