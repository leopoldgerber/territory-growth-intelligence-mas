from datetime import date
import json

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.alert import AlertDetail, AlertItem


def json_text(value: object) -> str:
    """Convert value to JSON text.
    Args:
        value (object): Source value."""
    text_value = json.dumps(value)
    return text_value


def float_value(value: object) -> float | None:
    """Convert optional float.
    Args:
        value (object): Source value."""
    converted_value = None if value is None else float(value)
    return converted_value


def country_value(row: dict[str, object]) -> dict[str, object] | None:
    """Build country value.
    Args:
        row (dict[str, object]): Alert row."""
    if row.get('country_id') is None:
        return None
    return {
        'country_id': row.get('country_id'),
        'country_name_en': row.get('country_name_en'),
        'country_name_ru': row.get('country_name_ru'),
    }


def competitor_value(row: dict[str, object]) -> dict[str, object] | None:
    """Build competitor value.
    Args:
        row (dict[str, object]): Alert row."""
    if row.get('domain_id') is None:
        return None
    return {
        'domain_id': row.get('domain_id'),
        'domain': row.get('domain'),
        'company_id': row.get('company_id'),
        'company_name': row.get('company_name'),
    }


def channel_value(row: dict[str, object]) -> dict[str, object] | None:
    """Build channel value.
    Args:
        row (dict[str, object]): Alert row."""
    if row.get('channel_id') is None:
        return None
    return {
        'channel_id': row.get('channel_id'),
        'channel_code': row.get('channel_code'),
        'channel_name': row.get('channel_name'),
    }


def item_value(row: dict[str, object]) -> AlertItem:
    """Build alert item.
    Args:
        row (dict[str, object]): Alert row."""
    item = AlertItem(
        anomaly_id=int(row['anomaly_id']),
        event_type=str(row['event_type']),
        event_category=row.get('event_category'),
        event_date=row['event_date'],
        severity=row.get('severity'),
        status=str(row.get('status') or 'new'),
        country=country_value(row),
        competitor=competitor_value(row),
        channel=channel_value(row),
        title=str(row.get('title') or ''),
        description=row.get('description'),
        recommendation_hint=row.get('recommendation_hint'),
        relative_change=float_value(row.get('relative_change')),
        created_at=row.get('created_at'),
    )
    return item


def detail_value(row: dict[str, object]) -> AlertDetail:
    """Build alert detail.
    Args:
        row (dict[str, object]): Alert row."""
    detail = AlertDetail(
        **item_value(row).model_dump(),
        metric_name=row.get('metric_name'),
        previous_value=float_value(row.get('previous_value')),
        current_value=float_value(row.get('current_value')),
        absolute_change=float_value(row.get('absolute_change')),
        baseline_value=float_value(row.get('baseline_value')),
        threshold_value=float_value(row.get('threshold_value')),
        evidence=row.get('evidence') or {},
        calculation_version=row.get('calculation_version'),
        data_quality_status=row.get('data_quality_status'),
        detected_at=row.get('detected_at'),
        updated_at=row.get('updated_at'),
    )
    return detail


def joined_select() -> str:
    """Build joined select.
    Args:
        None (None): No arguments are required."""
    query = """
        SELECT
            events.*,
            events.created_at::text AS created_at,
            events.detected_at::text AS detected_at,
            events.updated_at::text AS updated_at,
            country.country_name_en,
            country.country_name_ru,
            domains.domain,
            companies.company_name,
            channels.channel_code,
            channels.channel_name
        FROM anomaly_events AS events
        LEFT JOIN dim_country AS country ON country.country_id = events.country_id
        LEFT JOIN dim_domain AS domains ON domains.domain_id = events.domain_id
        LEFT JOIN dim_company AS companies ON companies.company_id = events.company_id
        LEFT JOIN dim_channel AS channels ON channels.channel_id = events.channel_id
    """
    return query


def event_exists(session: Session, dedup_key: str) -> int | None:
    """Get existing alert identifier.
    Args:
        session (Session): Database session.
        dedup_key (str): Deduplication key."""
    result = session.execute(
        text('SELECT anomaly_id FROM anomaly_events WHERE dedup_key = :dedup_key'),
        {'dedup_key': dedup_key},
    )
    value = result.scalar_one_or_none()
    return None if value is None else int(value)


def save_event(session: Session, event: dict[str, object]) -> bool:
    """Save alert event.
    Args:
        session (Session): Database session.
        event (dict[str, object]): Alert event data."""
    existing_id = event_exists(session, str(event['dedup_key']))
    params = {
        **event,
        'evidence': json_text(event.get('evidence') or {}),
    }
    if existing_id is not None:
        params['anomaly_id'] = existing_id
        session.execute(
            text(
                """
                UPDATE anomaly_events
                SET event_category = :event_category,
                    previous_value = :previous_value,
                    current_value = :current_value,
                    absolute_change = :absolute_change,
                    relative_change = :relative_change,
                    baseline_value = :baseline_value,
                    threshold_value = :threshold_value,
                    severity = :severity,
                    title = :title,
                    description = :description,
                    evidence = CAST(:evidence AS jsonb),
                    recommendation_hint = :recommendation_hint,
                    data_quality_status = :data_quality_status,
                    updated_at = now()
                WHERE anomaly_id = :anomaly_id
                """,
            ),
            params,
        )
        return False
    session.execute(
        text(
            """
            INSERT INTO anomaly_events (
                dedup_key, event_type, event_category, event_date, country_id, region_id, domain_id, company_id,
                channel_id, metric_name, previous_value, current_value, absolute_change, relative_change,
                baseline_value, threshold_value, severity, status, title, description, evidence,
                recommendation_hint, calculation_version, data_quality_status
            )
            VALUES (
                :dedup_key, :event_type, :event_category, :event_date, :country_id, :region_id, :domain_id,
                :company_id, :channel_id, :metric_name, :previous_value, :current_value, :absolute_change,
                :relative_change, :baseline_value, :threshold_value, :severity, 'new', :title, :description,
                CAST(:evidence AS jsonb), :recommendation_hint, :calculation_version, :data_quality_status
            )
            """,
        ),
        params,
    )
    return True


def list_events(
    session: Session,
    filters: dict[str, object],
    limit: int,
    offset: int,
) -> dict[str, object]:
    """List alert events.
    Args:
        session (Session): Database session.
        filters (dict[str, object]): Filter values.
        limit (int): Result limit.
        offset (int): Result offset."""
    where_parts = []
    params: dict[str, object] = {'limit': limit, 'offset': offset}
    for key in ['project_id', 'country_id', 'domain_id', 'channel_id', 'event_type', 'event_category', 'severity', 'status']:
        if filters.get(key) is not None:
            where_parts.append(f'events.{key} = :{key}')
            params[key] = filters[key]
    if filters.get('date_from') is not None:
        where_parts.append('events.event_date >= :date_from')
        params['date_from'] = filters['date_from']
    if filters.get('date_to') is not None:
        where_parts.append('events.event_date <= :date_to')
        params['date_to'] = filters['date_to']
    where_clause = f"WHERE {' AND '.join(where_parts)}" if where_parts else ''
    result = session.execute(
        text(
            f"""
            {joined_select()}
            {where_clause}
            ORDER BY events.event_date DESC, events.created_at DESC, events.anomaly_id DESC
            LIMIT :limit OFFSET :offset
            """,
        ),
        params,
    )
    count_result = session.execute(
        text(f'SELECT COUNT(*) FROM anomaly_events AS events {where_clause}'),
        params,
    )
    rows = [dict(row._mapping) for row in result]
    total = int(count_result.scalar_one() or 0)
    return {'items': [item_value(row) for row in rows], 'total': total}


def get_event(session: Session, anomaly_id: int) -> AlertDetail:
    """Get alert event.
    Args:
        session (Session): Database session.
        anomaly_id (int): Alert identifier."""
    result = session.execute(
        text(f'{joined_select()} WHERE events.anomaly_id = :anomaly_id'),
        {'anomaly_id': anomaly_id},
    )
    row = result.first()
    if row is None:
        raise HTTPException(status_code=404, detail='Alert not found.')
    detail = detail_value(dict(row._mapping))
    return detail


def update_status(session: Session, anomaly_id: int, status: str) -> AlertDetail:
    """Update alert status.
    Args:
        session (Session): Database session.
        anomaly_id (int): Alert identifier.
        status (str): New status."""
    if status not in ['new', 'reviewed', 'dismissed']:
        raise HTTPException(status_code=400, detail='Invalid alert status.')
    session.execute(
        text(
            """
            UPDATE anomaly_events
            SET status = :status, updated_at = now()
            WHERE anomaly_id = :anomaly_id
            """,
        ),
        {'anomaly_id': anomaly_id, 'status': status},
    )
    session.commit()
    return get_event(session, anomaly_id)


def summary_events(session: Session) -> dict[str, object]:
    """Summarize alert events.
    Args:
        session (Session): Database session."""
    totals = session.execute(
        text(
            """
            SELECT
                COUNT(*) FILTER (WHERE status = 'new') AS total_new,
                COUNT(*) FILTER (WHERE severity = 'critical') AS critical,
                COUNT(*) FILTER (WHERE severity = 'high') AS high,
                COUNT(*) FILTER (WHERE severity = 'medium') AS medium
            FROM anomaly_events
            """,
        ),
    ).one()
    category_rows = session.execute(
        text(
            """
            SELECT event_category, COUNT(*) AS total
            FROM anomaly_events
            GROUP BY event_category
            """,
        ),
    )
    by_category = {str(row.event_category or 'unknown'): int(row.total or 0) for row in category_rows}
    summary = {
        'total_new': int(totals.total_new or 0),
        'critical': int(totals.critical or 0),
        'high': int(totals.high or 0),
        'medium': int(totals.medium or 0),
        'by_category': by_category,
    }
    return summary
