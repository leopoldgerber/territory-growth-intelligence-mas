import json
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.update import UpdateScheduleCreate, UpdateScheduleItem, UpdateScheduleList, UpdateScheduleUpdate


def json_text(value: object) -> str:
    """Convert value to JSON text.
    Args:
        value (object): Source value."""
    serialized_value = json.dumps(value, default=str)
    return serialized_value


def next_run_time(frequency: str, reference_time: datetime | None = None) -> datetime:
    """Calculate next run time.
    Args:
        frequency (str): Schedule frequency.
        reference_time (datetime | None): Reference time."""
    base_time = reference_time or datetime.now(UTC)
    if frequency == 'daily':
        return base_time + timedelta(days=1)
    if frequency == 'weekly':
        return base_time + timedelta(days=7)
    if frequency == 'monthly':
        return base_time + timedelta(days=30)
    return base_time + timedelta(days=1)


def validate_schedule(frequency: str, update_type: str) -> str:
    """Validate schedule values.
    Args:
        frequency (str): Frequency value.
        update_type (str): Update type value."""
    if frequency not in ['daily', 'weekly', 'monthly', 'custom']:
        raise HTTPException(status_code=400, detail='Frequency is invalid.')
    if update_type not in ['parser', 'file_import', 'api_import', 'manual']:
        raise HTTPException(status_code=400, detail='Update type is invalid.')
    return frequency


def schedule_item(row: dict[str, object]) -> UpdateScheduleItem:
    """Build schedule item.
    Args:
        row (dict[str, object]): Schedule row."""
    data = dict(row)
    for key in ['next_run_at', 'last_run_at', 'created_at']:
        if data.get(key) is not None:
            data[key] = str(data[key])
    item = UpdateScheduleItem(**data)
    return item


def create_schedule(
    session: Session,
    request: UpdateScheduleCreate,
    user_id: int | None,
) -> UpdateScheduleItem:
    """Create update schedule.
    Args:
        session (Session): Database session.
        request (UpdateScheduleCreate): Schedule request.
        user_id (int | None): User identifier."""
    validate_schedule(request.frequency, request.update_type)
    row = session.execute(
        text(
            """
            INSERT INTO update_schedules (
                project_id, schedule_name, source_id, update_type, frequency, cron_expression,
                timezone, is_active, lookback_days, default_granularity, config, next_run_at,
                created_by_user_id
            )
            VALUES (
                :project_id, :schedule_name, :source_id, :update_type, :frequency, :cron_expression,
                :timezone, :is_active, :lookback_days, :default_granularity, CAST(:config AS jsonb),
                :next_run_at, :created_by_user_id
            )
            RETURNING *, NULL::text AS last_run_status
            """,
        ),
        {
            **request.model_dump(),
            'config': json_text(request.config or {}),
            'next_run_at': next_run_time(request.frequency) if request.is_active else None,
            'created_by_user_id': user_id,
        },
    ).first()
    session.commit()
    item = schedule_item(dict(row._mapping))
    return item


def update_schedule(
    session: Session,
    schedule_id: int,
    request: UpdateScheduleUpdate,
) -> UpdateScheduleItem:
    """Update schedule.
    Args:
        session (Session): Database session.
        schedule_id (int): Schedule identifier.
        request (UpdateScheduleUpdate): Schedule update."""
    current = get_schedule(session, schedule_id)
    payload = request.model_dump(exclude_unset=True)
    frequency = str(payload.get('frequency', current.frequency))
    update_type = str(payload.get('update_type', current.update_type))
    validate_schedule(frequency, update_type)
    is_active = bool(payload.get('is_active', current.is_active))
    row = session.execute(
        text(
            """
            UPDATE update_schedules
            SET schedule_name = :schedule_name,
                update_type = :update_type,
                frequency = :frequency,
                cron_expression = :cron_expression,
                timezone = :timezone,
                is_active = :is_active,
                lookback_days = :lookback_days,
                default_granularity = :default_granularity,
                config = CAST(:config AS jsonb),
                next_run_at = :next_run_at,
                updated_at = now()
            WHERE schedule_id = :schedule_id
            RETURNING *, NULL::text AS last_run_status
            """,
        ),
        {
            'schedule_id': schedule_id,
            'schedule_name': payload.get('schedule_name', current.schedule_name),
            'update_type': update_type,
            'frequency': frequency,
            'cron_expression': payload.get('cron_expression', current.cron_expression),
            'timezone': payload.get('timezone', current.timezone),
            'is_active': is_active,
            'lookback_days': payload.get('lookback_days', current.lookback_days),
            'default_granularity': payload.get('default_granularity', current.default_granularity),
            'config': json_text(payload.get('config', current.config or {})),
            'next_run_at': next_run_time(frequency) if is_active else None,
        },
    ).first()
    session.commit()
    item = schedule_item(dict(row._mapping))
    return item


def get_schedule(session: Session, schedule_id: int) -> UpdateScheduleItem:
    """Get schedule.
    Args:
        session (Session): Database session.
        schedule_id (int): Schedule identifier."""
    row = session.execute(
        text(
            """
            SELECT
                schedules.*,
                schedules.next_run_at::text AS next_run_at,
                schedules.last_run_at::text AS last_run_at,
                schedules.created_at::text AS created_at,
                latest.status AS last_run_status
            FROM update_schedules AS schedules
            LEFT JOIN LATERAL (
                SELECT status
                FROM update_runs
                WHERE update_runs.schedule_id = schedules.schedule_id
                ORDER BY created_at DESC
                LIMIT 1
            ) AS latest ON true
            WHERE schedules.schedule_id = :schedule_id
            """,
        ),
        {'schedule_id': schedule_id},
    ).first()
    if row is None:
        raise HTTPException(status_code=404, detail='Update schedule not found.')
    item = schedule_item(dict(row._mapping))
    return item


def list_schedules(session: Session, project_id: int | None, limit: int, offset: int) -> UpdateScheduleList:
    """List schedules.
    Args:
        session (Session): Database session.
        project_id (int | None): Project identifier.
        limit (int): Result limit.
        offset (int): Result offset."""
    filters = []
    params: dict[str, object] = {'limit': limit, 'offset': offset}
    if project_id is not None:
        filters.append('schedules.project_id = :project_id')
        params['project_id'] = project_id
    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ''
    rows = session.execute(
        text(
            f"""
            SELECT
                schedules.*,
                schedules.next_run_at::text AS next_run_at,
                schedules.last_run_at::text AS last_run_at,
                schedules.created_at::text AS created_at,
                latest.status AS last_run_status,
                COUNT(*) OVER() AS total
            FROM update_schedules AS schedules
            LEFT JOIN LATERAL (
                SELECT status
                FROM update_runs
                WHERE update_runs.schedule_id = schedules.schedule_id
                ORDER BY created_at DESC
                LIMIT 1
            ) AS latest ON true
            {where_clause}
            ORDER BY schedules.created_at DESC
            LIMIT :limit OFFSET :offset
            """,
        ),
        params,
    )
    data = [dict(row._mapping) for row in rows]
    total = int(data[0]['total']) if data else 0
    items = [schedule_item({key: value for key, value in row.items() if key != 'total'}) for row in data]
    return UpdateScheduleList(items=items, total=total)


def due_schedules(session: Session, limit: int = 20) -> list[UpdateScheduleItem]:
    """Get due schedules.
    Args:
        session (Session): Database session.
        limit (int): Result limit."""
    rows = session.execute(
        text(
            """
            SELECT schedules.*, schedules.next_run_at::text AS next_run_at,
                   schedules.last_run_at::text AS last_run_at,
                   schedules.created_at::text AS created_at,
                   NULL::text AS last_run_status
            FROM update_schedules AS schedules
            WHERE schedules.is_active = true
              AND schedules.next_run_at IS NOT NULL
              AND schedules.next_run_at <= now()
            ORDER BY schedules.next_run_at ASC
            LIMIT :limit
            """,
        ),
        {'limit': limit},
    )
    items = [schedule_item(dict(row._mapping)) for row in rows]
    return items


def mark_scheduled(session: Session, schedule_id: int, frequency: str) -> int:
    """Mark schedule queued.
    Args:
        session (Session): Database session.
        schedule_id (int): Schedule identifier.
        frequency (str): Schedule frequency."""
    session.execute(
        text(
            """
            UPDATE update_schedules
            SET last_run_at = now(), next_run_at = :next_run_at, updated_at = now()
            WHERE schedule_id = :schedule_id
            """,
        ),
        {'schedule_id': schedule_id, 'next_run_at': next_run_time(frequency)},
    )
    session.commit()
    return schedule_id
