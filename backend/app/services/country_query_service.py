from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session


def float_value(value: object) -> float:
    """Convert value to float.
    Args:
        value (object): Source value."""
    converted_value = float(value or 0)
    return converted_value


def optional_float(value: object) -> float | None:
    """Convert optional float.
    Args:
        value (object): Source value."""
    converted_value = None if value is None else float(value)
    return converted_value


def ratio_value(numerator: float | None, denominator: float | None) -> float | None:
    """Calculate ratio value.
    Args:
        numerator (float | None): Ratio numerator.
        denominator (float | None): Ratio denominator."""
    if denominator is None or denominator == 0 or numerator is None:
        return None
    ratio = numerator / denominator
    return ratio


def list_countries(
    session: Session,
    search: str | None,
    has_data: bool,
    limit: int,
    offset: int,
) -> dict[str, object]:
    """List countries.
    Args:
        session (Session): Database session.
        search (str | None): Search text.
        has_data (bool): Has data filter.
        limit (int): Result limit.
        offset (int): Result offset."""
    filters = []
    params: dict[str, object] = {'limit': limit, 'offset': offset}
    if search:
        filters.append('(country.country_name_en ILIKE :search OR country.country_name_ru ILIKE :search)')
        params['search'] = f'%{search}%'
    if has_data:
        filters.append('facts.country_id IS NOT NULL')
    where_clause = f'WHERE {" AND ".join(filters)}' if filters else ''
    query = text(
        f"""
        WITH fact_countries AS (
            SELECT DISTINCT country_id
            FROM fact_domain_country_daily
        )
        SELECT
            country.country_id,
            country.country_name_en,
            country.country_name_ru,
            region.region_name AS region_name_en,
            region.region_name AS region_name_ru,
            facts.country_id IS NOT NULL AS has_data,
            COUNT(*) OVER() AS total
        FROM dim_country AS country
        LEFT JOIN dim_region AS region ON region.region_id = country.region_id
        LEFT JOIN fact_countries AS facts ON facts.country_id = country.country_id
        {where_clause}
        ORDER BY country.country_name_en
        LIMIT :limit OFFSET :offset
        """,
    )
    result = session.execute(query, params)
    rows = [dict(row._mapping) for row in result]
    total = int(rows[0]['total']) if rows else 0
    for row in rows:
        row.pop('total', None)
    return {'items': rows, 'total': total}


def get_country(session: Session, country_id: int) -> dict[str, object] | None:
    """Get country.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier."""
    result = session.execute(
        text(
            """
            SELECT
                country.country_id,
                country.country_name_en,
                country.country_name_ru,
                region.region_name AS region_name_en,
                region.region_name AS region_name_ru,
                EXISTS (
                    SELECT 1 FROM fact_domain_country_daily AS facts WHERE facts.country_id = country.country_id
                ) AS has_data
            FROM dim_country AS country
            LEFT JOIN dim_region AS region ON region.region_id = country.region_id
            WHERE country.country_id = :country_id
            """,
        ),
        {'country_id': country_id},
    )
    row = result.first()
    country = dict(row._mapping) if row else None
    return country


def get_period(session: Session, country_id: int) -> dict[str, object]:
    """Get available period.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier."""
    result = session.execute(
        text(
            """
            SELECT
                MIN(date) AS date_min,
                MAX(date) AS date_max,
                COUNT(DISTINCT date) AS available_days
            FROM fact_domain_country_daily
            WHERE country_id = :country_id
            """,
        ),
        {'country_id': country_id},
    )
    row = result.one()
    period = {
        'country_id': country_id,
        'date_min': row.date_min,
        'date_max': row.date_max,
        'available_days': int(row.available_days or 0),
    }
    return period


def latest_quality(session: Session) -> str | None:
    """Get latest quality status.
    Args:
        session (Session): Database session."""
    result = session.execute(
        text(
            """
            SELECT quality_status
            FROM ingestion_runs
            ORDER BY started_at DESC NULLS LAST, run_id DESC
            LIMIT 1
            """,
        ),
    )
    quality_status = result.scalar_one_or_none()
    return quality_status


def quality_result(statuses: list[str], fallback: str) -> str:
    """Resolve quality result.
    Args:
        statuses (list[str]): Quality status list.
        fallback (str): Fallback status."""
    if not statuses:
        return fallback
    if 'failed' in statuses:
        return 'failed'
    if 'warning' in statuses:
        return 'warning'
    if all(status == 'passed' for status in statuses):
        return 'passed'
    return 'unknown'


def period_quality(
    session: Session,
    country_id: int,
    date_from: date,
    date_to: date,
) -> str:
    """Get period quality status.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date."""
    result = session.execute(
        text(
            """
            SELECT DISTINCT runs.quality_status
            FROM fact_domain_country_daily AS facts
            JOIN ingestion_runs AS runs ON runs.run_id = facts.run_id
            WHERE facts.country_id = :country_id
              AND facts.date BETWEEN :date_from AND :date_to
            """,
        ),
        {'country_id': country_id, 'date_from': date_from, 'date_to': date_to},
    )
    statuses = [status for status in result.scalars().all() if status is not None]
    return quality_result(statuses, 'unknown')


def domain_period_quality(
    session: Session,
    domain_id: int,
    date_from: date,
    date_to: date,
) -> str:
    """Get domain period quality status.
    Args:
        session (Session): Database session.
        domain_id (int): Domain identifier.
        date_from (date): Period start date.
        date_to (date): Period end date."""
    result = session.execute(
        text(
            """
            SELECT DISTINCT runs.quality_status
            FROM fact_domain_country_daily AS facts
            JOIN ingestion_runs AS runs ON runs.run_id = facts.run_id
            WHERE facts.domain_id = :domain_id
              AND facts.date BETWEEN :date_from AND :date_to
            """,
        ),
        {'domain_id': domain_id, 'date_from': date_from, 'date_to': date_to},
    )
    statuses = [status for status in result.scalars().all() if status is not None]
    return quality_result(statuses, 'unknown')


def channel_scope_quality(
    session: Session,
    country_id: int | None,
    domain_id: int | None,
    date_from: date,
    date_to: date,
) -> str:
    """Get channel scope quality status.
    Args:
        session (Session): Database session.
        country_id (int | None): Country identifier.
        domain_id (int | None): Domain identifier.
        date_from (date): Period start date.
        date_to (date): Period end date."""
    if country_id is not None:
        return period_quality(session, country_id, date_from, date_to)
    filters = ['facts.date BETWEEN :date_from AND :date_to']
    params: dict[str, object] = {'date_from': date_from, 'date_to': date_to}
    if domain_id is not None:
        filters.append('facts.domain_id = :domain_id')
        params['domain_id'] = domain_id
    where_clause = ' AND '.join(filters)
    result = session.execute(
        text(
            f"""
            SELECT DISTINCT runs.quality_status
            FROM fact_domain_channel_daily AS facts
            JOIN ingestion_runs AS runs ON runs.run_id = facts.run_id
            WHERE {where_clause}
            """,
        ),
        params,
    )
    statuses = [status for status in result.scalars().all() if status is not None]
    return quality_result(statuses, 'unknown')


def validate_period(
    session: Session,
    country_id: int,
    date_from: date,
    date_to: date,
) -> str:
    """Validate country period.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date."""
    period = get_period(session, country_id)
    date_min = period['date_min']
    date_max = period['date_max']
    if date_min is None or date_max is None:
        return 'NO_DATA_FOR_COUNTRY'
    if date_from > date_to:
        return 'INVALID_PERIOD'
    if date_from > date_max or date_to < date_min:
        return 'PERIOD_OUT_OF_RANGE'
    return ''
