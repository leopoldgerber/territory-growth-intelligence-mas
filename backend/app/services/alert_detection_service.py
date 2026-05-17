from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.alert_storage_service import save_event
from app.services.channel_anomaly_detector import detect_channels
from app.services.country_query_service import period_quality
from app.services.market_movement_detector import detect_market
from app.services.quality_anomaly_detector import detect_quality
from app.services.traffic_anomaly_detector import detect_traffic


def validate_detection(session: Session, date_from: date, date_to: date, country_id: int | None) -> str:
    """Validate detection request.
    Args:
        session (Session): Database session.
        date_from (date): Period start date.
        date_to (date): Period end date.
        country_id (int | None): Country identifier."""
    days_count = (date_to - date_from).days + 1
    if days_count < 14:
        raise HTTPException(status_code=400, detail='Insufficient data for reliable anomaly detection.')
    if date_from > date_to:
        raise HTTPException(status_code=400, detail='Selected period is invalid.')
    if country_id is None:
        return 'unknown'
    status = period_quality(session, country_id, date_from, date_to)
    if status == 'failed':
        raise HTTPException(status_code=409, detail='Alert detection cannot run on failed quality data.')
    return status


def detect_events(
    session: Session,
    date_from: date,
    date_to: date,
    country_id: int | None,
    domain_id: int | None,
    calculation_version: str,
) -> dict[str, int | str]:
    """Detect alert events.
    Args:
        session (Session): Database session.
        date_from (date): Period start date.
        date_to (date): Period end date.
        country_id (int | None): Country identifier.
        domain_id (int | None): Domain identifier.
        calculation_version (str): Calculation version."""
    validate_detection(session, date_from, date_to, country_id)
    events = []
    events.extend(detect_traffic(session, date_from, date_to, country_id, domain_id, calculation_version))
    events.extend(detect_market(session, date_from, date_to, country_id, domain_id, calculation_version))
    events.extend(detect_channels(session, date_from, date_to, domain_id, calculation_version))
    events.extend(detect_quality(session, date_from, date_to, country_id, domain_id, calculation_version))
    created_events = 0
    duplicates_skipped = 0
    for event in events:
        created = save_event(session, event)
        if created:
            created_events += 1
        else:
            duplicates_skipped += 1
    session.commit()
    response = {
        'status': 'success',
        'detected_events': len(events),
        'created_events': created_events,
        'duplicates_skipped': duplicates_skipped,
    }
    return response
