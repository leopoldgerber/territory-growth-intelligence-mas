from datetime import date, timedelta


THRESHOLDS = {
    'domain_traffic': 1000,
    'channel_traffic': 500,
    'market_traffic': 5000,
    'share_change': 0.10,
    'quality_change': 0.20,
    'engagement_change': 0.20,
}


def split_window(date_from: date, date_to: date) -> tuple[date, date, date, date]:
    """Split detection window.
    Args:
        date_from (date): Period start date.
        date_to (date): Period end date."""
    days_count = (date_to - date_from).days + 1
    midpoint = date_from + timedelta(days=max(1, days_count // 2) - 1)
    current_start = midpoint + timedelta(days=1)
    return date_from, midpoint, current_start, date_to


def relative_change(previous_value: float, current_value: float) -> float | None:
    """Calculate relative change.
    Args:
        previous_value (float): Previous metric value.
        current_value (float): Current metric value."""
    if previous_value == 0:
        return None
    change = (current_value - previous_value) / previous_value
    return change


def severity_value(relative_value: float | None, absolute_change: float, threshold: float) -> str:
    """Calculate severity value.
    Args:
        relative_value (float | None): Relative change.
        absolute_change (float): Absolute change.
        threshold (float): Meaningful threshold."""
    relative_score = min(abs(relative_value or 0), 2) / 2
    absolute_score = min(abs(absolute_change) / max(threshold * 5, 1), 1)
    severity_score = 0.65 * relative_score + 0.35 * absolute_score
    if severity_score >= 0.85:
        return 'critical'
    if severity_score >= 0.65:
        return 'high'
    if severity_score >= 0.40:
        return 'medium'
    return 'low'


def dedup_key(
    event_type: str,
    event_date: date,
    country_id: object,
    domain_id: object,
    channel_id: object,
    calculation_version: str,
) -> str:
    """Build deduplication key.
    Args:
        event_type (str): Event type.
        event_date (date): Event date.
        country_id (object): Country identifier.
        domain_id (object): Domain identifier.
        channel_id (object): Channel identifier.
        calculation_version (str): Calculation version."""
    key = (
        f'{event_type}|{event_date.isoformat()}|country={country_id or "null"}|'
        f'domain={domain_id or "null"}|channel={channel_id or "null"}|{calculation_version}'
    )
    return key


def evidence_value(
    baseline_start: date,
    baseline_end: date,
    current_start: date,
    current_end: date,
    previous_value: float,
    current_value: float,
    threshold: float,
    data_quality_status: str,
) -> dict[str, object]:
    """Build alert evidence.
    Args:
        baseline_start (date): Baseline window start.
        baseline_end (date): Baseline window end.
        current_start (date): Current window start.
        current_end (date): Current window end.
        previous_value (float): Previous metric value.
        current_value (float): Current metric value.
        threshold (float): Detection threshold.
        data_quality_status (str): Data quality status."""
    change = relative_change(previous_value, current_value)
    evidence = {
        'baseline_window': {
            'date_from': baseline_start.isoformat(),
            'date_to': baseline_end.isoformat(),
            'value': previous_value,
        },
        'current_window': {
            'date_from': current_start.isoformat(),
            'date_to': current_end.isoformat(),
            'value': current_value,
        },
        'change': {
            'absolute_change': current_value - previous_value,
            'relative_change': change,
        },
        'thresholds': {
            'meaningful_threshold': threshold,
        },
    }
    if data_quality_status == 'warning':
        evidence['data_quality_warning'] = 'Alert detected on data with quality warnings.'
    if data_quality_status == 'unknown':
        evidence['data_quality_warning'] = 'No quality context found for selected alert scope.'
    return evidence
