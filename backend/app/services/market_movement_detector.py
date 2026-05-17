from datetime import date

from sqlalchemy.orm import Session

from app.services.alert_narrative_service import description_text, recommendation_hint, title_text
from app.services.alert_rule_service import THRESHOLDS, dedup_key, evidence_value, relative_change, severity_value, split_window
from app.services.country_query_service import period_quality
from app.services.traffic_anomaly_detector import domain_rows


def market_event(
    row: dict[str, object],
    event_type: str,
    event_date: date,
    threshold: float,
    windows: tuple[date, date, date, date],
    calculation_version: str,
    data_quality_status: str,
) -> dict[str, object]:
    """Build market event.
    Args:
        row (dict[str, object]): Source row.
        event_type (str): Event type.
        event_date (date): Event date.
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
        'dedup_key': dedup_key(event_type, event_date, row.get('country_id'), row.get('domain_id'), None, calculation_version),
        'event_type': event_type,
        'event_category': 'market',
        'event_date': event_date,
        'country_id': row.get('country_id'),
        'region_id': row.get('region_id'),
        'domain_id': row.get('domain_id'),
        'company_id': row.get('company_id'),
        'channel_id': None,
        'metric_name': row.get('metric_name') or 'traffic',
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


def share_maps(rows: list[dict[str, object]]) -> dict[int, list[dict[str, object]]]:
    """Build country share maps.
    Args:
        rows (list[dict[str, object]]): Domain rows."""
    country_rows: dict[int, list[dict[str, object]]] = {}
    for row in rows:
        country_id = int(row['country_id'])
        country_rows.setdefault(country_id, []).append(row)
    for values in country_rows.values():
        baseline_total = sum(float(row.get('baseline_value') or 0) for row in values)
        current_total = sum(float(row.get('current_value') or 0) for row in values)
        for row in values:
            row['baseline_share'] = float(row.get('baseline_value') or 0) / baseline_total if baseline_total else 0
            row['current_share'] = float(row.get('current_value') or 0) / current_total if current_total else 0
        values.sort(key=lambda item: float(item.get('current_value') or 0), reverse=True)
    return country_rows


def detect_market(
    session: Session,
    date_from: date,
    date_to: date,
    country_id: int | None,
    domain_id: int | None,
    calculation_version: str,
) -> list[dict[str, object]]:
    """Detect market movement.
    Args:
        session (Session): Database session.
        date_from (date): Period start date.
        date_to (date): Period end date.
        country_id (int | None): Country identifier.
        domain_id (int | None): Domain identifier.
        calculation_version (str): Calculation version."""
    windows = split_window(date_from, date_to)
    event_date = windows[3]
    rows = domain_rows(session, date_from, date_to, country_id, domain_id)
    events = []
    for row in rows:
        previous_value = float(row.get('baseline_value') or 0)
        current_value = float(row.get('current_value') or 0)
        status = period_quality(session, int(row['country_id']), date_from, date_to)
        if previous_value < THRESHOLDS['domain_traffic'] * 0.1 and current_value >= THRESHOLDS['domain_traffic']:
            events.append(market_event(row, 'new_market_signal', event_date, THRESHOLDS['domain_traffic'], windows, calculation_version, status))
        if previous_value >= THRESHOLDS['domain_traffic'] and current_value < THRESHOLDS['domain_traffic'] * 0.1:
            events.append(market_event(row, 'abandoned_market_signal', event_date, THRESHOLDS['domain_traffic'], windows, calculation_version, status))
    for values in share_maps(rows).values():
        baseline_leader = max(values, key=lambda item: float(item.get('baseline_value') or 0), default=None)
        current_leader = max(values, key=lambda item: float(item.get('current_value') or 0), default=None)
        if baseline_leader and current_leader and baseline_leader.get('domain_id') != current_leader.get('domain_id'):
            status = period_quality(session, int(current_leader['country_id']), date_from, date_to)
            current_leader['baseline_value'] = baseline_leader.get('baseline_share')
            current_leader['current_value'] = current_leader.get('current_share')
            current_leader['metric_name'] = 'leader_share'
            events.append(market_event(current_leader, 'leader_changed', event_date, THRESHOLDS['share_change'], windows, calculation_version, status))
        if baseline_leader:
            leader_drop = float(baseline_leader.get('baseline_share') or 0) - float(baseline_leader.get('current_share') or 0)
            if leader_drop > 0.15:
                status = period_quality(session, int(baseline_leader['country_id']), date_from, date_to)
                baseline_leader['baseline_value'] = baseline_leader.get('baseline_share')
                baseline_leader['current_value'] = baseline_leader.get('current_share')
                baseline_leader['metric_name'] = 'leader_share'
                events.append(market_event(baseline_leader, 'leader_weakening', event_date, THRESHOLDS['share_change'], windows, calculation_version, status))
        for rank, row in enumerate(values[:3], start=1):
            share_gain = float(row.get('current_share') or 0) - float(row.get('baseline_share') or 0)
            if rank <= 3 and row is not baseline_leader and share_gain > 0.10:
                status = period_quality(session, int(row['country_id']), date_from, date_to)
                row['baseline_value'] = row.get('baseline_share')
                row['current_value'] = row.get('current_share')
                row['metric_name'] = 'traffic_share'
                events.append(market_event(row, 'challenger_growth', event_date, THRESHOLDS['share_change'], windows, calculation_version, status))
    return events
