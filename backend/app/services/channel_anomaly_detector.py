from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.alert_narrative_service import description_text, recommendation_hint, title_text
from app.services.alert_rule_service import THRESHOLDS, dedup_key, evidence_value, relative_change, severity_value, split_window
from app.services.country_query_service import channel_scope_quality


SPIKE_EVENTS = {
    'paid': 'paid_spike',
    'referral': 'referral_spike',
    'social': 'social_spike',
}


def channel_rows(
    session: Session,
    date_from: date,
    date_to: date,
    domain_id: int | None,
) -> list[dict[str, object]]:
    """Get channel rows.
    Args:
        session (Session): Database session.
        date_from (date): Period start date.
        date_to (date): Period end date.
        domain_id (int | None): Domain identifier."""
    baseline_start, baseline_end, current_start, current_end = split_window(date_from, date_to)
    filters = ['facts.date BETWEEN :date_from AND :date_to']
    params: dict[str, object] = {
        'date_from': date_from,
        'date_to': date_to,
        'baseline_start': baseline_start,
        'baseline_end': baseline_end,
        'current_start': current_start,
        'current_end': current_end,
    }
    if domain_id is not None:
        filters.append('facts.domain_id = :domain_id')
        params['domain_id'] = domain_id
    where_clause = ' AND '.join(filters)
    result = session.execute(
        text(
            f"""
            SELECT
                facts.domain_id,
                domains.domain,
                domains.company_id,
                companies.company_name,
                facts.channel_id,
                channels.channel_code,
                channels.channel_name,
                SUM(facts.traffic) FILTER (WHERE facts.date BETWEEN :baseline_start AND :baseline_end) AS baseline_value,
                SUM(facts.traffic) FILTER (WHERE facts.date BETWEEN :current_start AND :current_end) AS current_value,
                SUM(SUM(facts.traffic) FILTER (WHERE facts.date BETWEEN :baseline_start AND :baseline_end))
                    OVER (PARTITION BY facts.domain_id) AS baseline_total,
                SUM(SUM(facts.traffic) FILTER (WHERE facts.date BETWEEN :current_start AND :current_end))
                    OVER (PARTITION BY facts.domain_id) AS current_total
            FROM fact_domain_channel_daily AS facts
            JOIN dim_domain AS domains ON domains.domain_id = facts.domain_id
            LEFT JOIN dim_company AS companies ON companies.company_id = domains.company_id
            JOIN dim_channel AS channels ON channels.channel_id = facts.channel_id
            WHERE {where_clause}
            GROUP BY facts.domain_id, domains.domain, domains.company_id, companies.company_name,
                facts.channel_id, channels.channel_code, channels.channel_name
            """,
        ),
        params,
    )
    rows = [dict(row._mapping) for row in result]
    return rows


def channel_event(
    row: dict[str, object],
    event_type: str,
    event_date: date,
    metric_name: str,
    threshold: float,
    windows: tuple[date, date, date, date],
    calculation_version: str,
    data_quality_status: str,
) -> dict[str, object]:
    """Build channel event.
    Args:
        row (dict[str, object]): Source row.
        event_type (str): Event type.
        event_date (date): Event date.
        metric_name (str): Metric name.
        threshold (float): Meaningful threshold.
        windows (tuple[date, date, date, date]): Detection windows.
        calculation_version (str): Calculation version.
        data_quality_status (str): Data quality status."""
    previous_value = float(row.get('baseline_value') or 0)
    current_value = float(row.get('current_value') or 0)
    change = current_value - previous_value
    relative_value = relative_change(previous_value, current_value)
    event_row = {**row, 'previous_value': previous_value, 'current_value': current_value}
    event = {
        'dedup_key': dedup_key(event_type, event_date, None, row.get('domain_id'), row.get('channel_id'), calculation_version),
        'event_type': event_type,
        'event_category': 'channel',
        'event_date': event_date,
        'country_id': None,
        'region_id': None,
        'domain_id': row.get('domain_id'),
        'company_id': row.get('company_id'),
        'channel_id': row.get('channel_id'),
        'metric_name': metric_name,
        'previous_value': previous_value,
        'current_value': current_value,
        'absolute_change': change,
        'relative_change': relative_value,
        'baseline_value': previous_value,
        'threshold_value': threshold,
        'severity': severity_value(relative_value, change, threshold),
        'title': title_text(event_type, event_row),
        'description': description_text(event_type, event_row),
        'evidence': evidence_value(*windows, previous_value, current_value, threshold, data_quality_status),
        'recommendation_hint': recommendation_hint(event_type),
        'calculation_version': calculation_version,
        'data_quality_status': data_quality_status,
    }
    return event


def detect_channels(
    session: Session,
    date_from: date,
    date_to: date,
    domain_id: int | None,
    calculation_version: str,
) -> list[dict[str, object]]:
    """Detect channel anomalies.
    Args:
        session (Session): Database session.
        date_from (date): Period start date.
        date_to (date): Period end date.
        domain_id (int | None): Domain identifier.
        calculation_version (str): Calculation version."""
    windows = split_window(date_from, date_to)
    event_date = windows[3]
    events = []
    quality_status = channel_scope_quality(session, None, domain_id, date_from, date_to)
    for row in channel_rows(session, date_from, date_to, domain_id):
        previous_value = float(row.get('baseline_value') or 0)
        current_value = float(row.get('current_value') or 0)
        channel_code = str(row.get('channel_code') or '')
        baseline_total = float(row.get('baseline_total') or 0)
        current_total = float(row.get('current_total') or 0)
        baseline_share = previous_value / baseline_total if baseline_total else 0
        current_share = current_value / current_total if current_total else 0
        row['data_quality_status'] = quality_status
        if channel_code in SPIKE_EVENTS and previous_value >= THRESHOLDS['channel_traffic'] and current_value > previous_value * 2:
            event = channel_event(
                row,
                SPIKE_EVENTS[channel_code],
                event_date,
                'traffic',
                THRESHOLDS['channel_traffic'],
                windows,
                calculation_version,
                quality_status,
            )
            events.append(event)
        share_change = current_share - baseline_share
        if abs(share_change) > 0.20:
            row['baseline_value'] = baseline_share
            row['current_value'] = current_share
            event = channel_event(
                row,
                'channel_shift',
                event_date,
                'traffic_share',
                THRESHOLDS['share_change'],
                windows,
                calculation_version,
                quality_status,
            )
            events.append(event)
    return events
