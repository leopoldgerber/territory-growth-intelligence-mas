from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.alert_narrative_service import description_text, recommendation_hint, title_text
from app.services.alert_rule_service import THRESHOLDS, dedup_key, evidence_value, relative_change, severity_value, split_window
from app.services.country_query_service import period_quality


def quality_rows(
    session: Session,
    date_from: date,
    date_to: date,
    country_id: int | None,
    domain_id: int | None,
) -> list[dict[str, object]]:
    """Get quality rows.
    Args:
        session (Session): Database session.
        date_from (date): Period start date.
        date_to (date): Period end date.
        country_id (int | None): Country identifier.
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
    if country_id is not None:
        filters.append('facts.country_id = :country_id')
        params['country_id'] = country_id
    if domain_id is not None:
        filters.append('facts.domain_id = :domain_id')
        params['domain_id'] = domain_id
    where_clause = ' AND '.join(filters)
    result = session.execute(
        text(
            f"""
            SELECT
                facts.country_id,
                country.region_id,
                country.country_name_en,
                facts.domain_id,
                domains.domain,
                domains.company_id,
                companies.company_name,
                SUM(facts.traffic_no_bounce) FILTER (WHERE facts.date BETWEEN :baseline_start AND :baseline_end)
                    / NULLIF(SUM(facts.traffic) FILTER (WHERE facts.date BETWEEN :baseline_start AND :baseline_end), 0) AS baseline_no_bounce,
                SUM(facts.traffic_no_bounce) FILTER (WHERE facts.date BETWEEN :current_start AND :current_end)
                    / NULLIF(SUM(facts.traffic) FILTER (WHERE facts.date BETWEEN :current_start AND :current_end), 0) AS current_no_bounce,
                SUM(facts.traffic_bounce) FILTER (WHERE facts.date BETWEEN :baseline_start AND :baseline_end)
                    / NULLIF(SUM(facts.traffic) FILTER (WHERE facts.date BETWEEN :baseline_start AND :baseline_end), 0) AS baseline_bounce,
                SUM(facts.traffic_bounce) FILTER (WHERE facts.date BETWEEN :current_start AND :current_end)
                    / NULLIF(SUM(facts.traffic) FILTER (WHERE facts.date BETWEEN :current_start AND :current_end), 0) AS current_bounce
            FROM fact_domain_country_daily AS facts
            JOIN dim_country AS country ON country.country_id = facts.country_id
            JOIN dim_domain AS domains ON domains.domain_id = facts.domain_id
            LEFT JOIN dim_company AS companies ON companies.company_id = domains.company_id
            WHERE {where_clause}
            GROUP BY facts.country_id, country.region_id, country.country_name_en, facts.domain_id, domains.domain,
                domains.company_id, companies.company_name
            """,
        ),
        params,
    )
    rows = [dict(row._mapping) for row in result]
    return rows


def quality_event(
    row: dict[str, object],
    event_type: str,
    event_date: date,
    metric_name: str,
    previous_value: float,
    current_value: float,
    windows: tuple[date, date, date, date],
    calculation_version: str,
    data_quality_status: str,
) -> dict[str, object]:
    """Build quality event.
    Args:
        row (dict[str, object]): Source row.
        event_type (str): Event type.
        event_date (date): Event date.
        metric_name (str): Metric name.
        previous_value (float): Previous value.
        current_value (float): Current value.
        windows (tuple[date, date, date, date]): Detection windows.
        calculation_version (str): Calculation version.
        data_quality_status (str): Data quality status."""
    change = current_value - previous_value
    relative_value = relative_change(previous_value, current_value)
    event_row = {**row, 'previous_value': previous_value, 'current_value': current_value}
    event = {
        'dedup_key': dedup_key(event_type, event_date, row.get('country_id'), row.get('domain_id'), None, calculation_version),
        'event_type': event_type,
        'event_category': 'quality',
        'event_date': event_date,
        'country_id': row.get('country_id'),
        'region_id': row.get('region_id'),
        'domain_id': row.get('domain_id'),
        'company_id': row.get('company_id'),
        'channel_id': None,
        'metric_name': metric_name,
        'previous_value': previous_value,
        'current_value': current_value,
        'absolute_change': change,
        'relative_change': relative_value,
        'baseline_value': previous_value,
        'threshold_value': THRESHOLDS['quality_change'],
        'severity': severity_value(relative_value, change, THRESHOLDS['quality_change']),
        'title': title_text(event_type, event_row),
        'description': description_text(event_type, event_row),
        'evidence': evidence_value(*windows, previous_value, current_value, THRESHOLDS['quality_change'], data_quality_status),
        'recommendation_hint': recommendation_hint(event_type),
        'calculation_version': calculation_version,
        'data_quality_status': data_quality_status,
    }
    return event


def detect_quality(
    session: Session,
    date_from: date,
    date_to: date,
    country_id: int | None,
    domain_id: int | None,
    calculation_version: str,
) -> list[dict[str, object]]:
    """Detect quality anomalies.
    Args:
        session (Session): Database session.
        date_from (date): Period start date.
        date_to (date): Period end date.
        country_id (int | None): Country identifier.
        domain_id (int | None): Domain identifier.
        calculation_version (str): Calculation version."""
    windows = split_window(date_from, date_to)
    event_date = windows[3]
    events = []
    for row in quality_rows(session, date_from, date_to, country_id, domain_id):
        status = period_quality(session, int(row['country_id']), date_from, date_to)
        baseline_no_bounce = float(row.get('baseline_no_bounce') or 0)
        current_no_bounce = float(row.get('current_no_bounce') or 0)
        baseline_bounce = float(row.get('baseline_bounce') or 0)
        current_bounce = float(row.get('current_bounce') or 0)
        if current_no_bounce < baseline_no_bounce - THRESHOLDS['quality_change']:
            events.append(quality_event(row, 'no_bounce_drop', event_date, 'no_bounce_share', baseline_no_bounce, current_no_bounce, windows, calculation_version, status))
            events.append(quality_event(row, 'quality_drop', event_date, 'no_bounce_share', baseline_no_bounce, current_no_bounce, windows, calculation_version, status))
        if current_bounce > baseline_bounce + THRESHOLDS['quality_change']:
            events.append(quality_event(row, 'bounce_spike', event_date, 'bounce_share', baseline_bounce, current_bounce, windows, calculation_version, status))
    return events
