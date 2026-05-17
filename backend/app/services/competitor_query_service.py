from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session


def list_competitors(
    session: Session,
    search: str | None,
    has_data: bool,
    limit: int,
    offset: int,
) -> dict[str, object]:
    """List competitors.
    Args:
        session (Session): Database session.
        search (str | None): Search text.
        has_data (bool): Has data flag.
        limit (int): Result limit.
        offset (int): Result offset."""
    filters = []
    params: dict[str, object] = {'limit': limit, 'offset': offset}
    if search:
        filters.append('(domains.domain ILIKE :search OR companies.company_name ILIKE :search)')
        params['search'] = f'%{search}%'
    if has_data:
        filters.append('facts.domain_id IS NOT NULL')
    where_clause = f'WHERE {" AND ".join(filters)}' if filters else ''
    result = session.execute(
        text(
            f"""
            WITH fact_domains AS (
                SELECT DISTINCT domain_id
                FROM fact_domain_country_daily
            )
            SELECT
                domains.domain_id,
                domains.domain,
                domains.company_id,
                companies.company_name,
                facts.domain_id IS NOT NULL AS has_data,
                COUNT(*) OVER() AS total
            FROM dim_domain AS domains
            LEFT JOIN dim_company AS companies ON companies.company_id = domains.company_id
            LEFT JOIN fact_domains AS facts ON facts.domain_id = domains.domain_id
            {where_clause}
            ORDER BY domains.domain
            LIMIT :limit OFFSET :offset
            """,
        ),
        params,
    )
    rows = [dict(row._mapping) for row in result]
    total = int(rows[0]['total']) if rows else 0
    for row in rows:
        row.pop('total', None)
    return {'items': rows, 'total': total}


def get_competitor(session: Session, domain_id: int) -> dict[str, object] | None:
    """Get competitor.
    Args:
        session (Session): Database session.
        domain_id (int): Domain identifier."""
    result = session.execute(
        text(
            """
            SELECT
                domains.domain_id,
                domains.domain,
                domains.company_id,
                companies.company_name,
                EXISTS (
                    SELECT 1 FROM fact_domain_country_daily AS facts WHERE facts.domain_id = domains.domain_id
                ) AS has_data
            FROM dim_domain AS domains
            LEFT JOIN dim_company AS companies ON companies.company_id = domains.company_id
            WHERE domains.domain_id = :domain_id
            """,
        ),
        {'domain_id': domain_id},
    )
    row = result.first()
    competitor = dict(row._mapping) if row else None
    return competitor


def get_period(session: Session, domain_id: int) -> dict[str, object]:
    """Get competitor period.
    Args:
        session (Session): Database session.
        domain_id (int): Domain identifier."""
    result = session.execute(
        text(
            """
            SELECT MIN(date) AS date_min, MAX(date) AS date_max, COUNT(DISTINCT date) AS available_days
            FROM fact_domain_country_daily
            WHERE domain_id = :domain_id
            """,
        ),
        {'domain_id': domain_id},
    )
    row = result.one()
    competitor = get_competitor(session, domain_id) or {}
    return {
        'domain_id': domain_id,
        'domain': competitor.get('domain') or '',
        'date_min': row.date_min,
        'date_max': row.date_max,
        'available_days': int(row.available_days or 0),
    }


def validate_period(session: Session, domain_id: int, date_from: date, date_to: date) -> str:
    """Validate competitor period.
    Args:
        session (Session): Database session.
        domain_id (int): Domain identifier.
        date_from (date): Period start date.
        date_to (date): Period end date."""
    period = get_period(session, domain_id)
    if period['date_min'] is None or period['date_max'] is None:
        return 'NO_DATA_FOR_COMPETITOR'
    if date_from > date_to:
        return 'INVALID_PERIOD'
    if date_from > period['date_max'] or date_to < period['date_min']:
        return 'PERIOD_OUT_OF_RANGE'
    return ''
