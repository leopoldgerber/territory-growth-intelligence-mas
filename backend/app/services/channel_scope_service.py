from datetime import date

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.channel import ChannelScope


def scope_type(country_id: int | None, domain_id: int | None) -> str:
    """Resolve scope type.
    Args:
        country_id (int | None): Country identifier.
        domain_id (int | None): Domain identifier."""
    if country_id is not None and domain_id is not None:
        return 'country_domain'
    if country_id is not None:
        return 'country'
    if domain_id is not None:
        return 'domain'
    return 'global'


def get_country(session: Session, country_id: int | None) -> dict[str, object] | None:
    """Get country data.
    Args:
        session (Session): Database session.
        country_id (int | None): Country identifier."""
    if country_id is None:
        return None
    result = session.execute(
        text(
            """
            SELECT country_id, country_name_en
            FROM dim_country
            WHERE country_id = :country_id
            """,
        ),
        {'country_id': country_id},
    )
    row = result.first()
    country = dict(row._mapping) if row else None
    return country


def get_domain(session: Session, domain_id: int | None) -> dict[str, object] | None:
    """Get domain data.
    Args:
        session (Session): Database session.
        domain_id (int | None): Domain identifier."""
    if domain_id is None:
        return None
    result = session.execute(
        text(
            """
            SELECT
                domains.domain_id,
                domains.domain,
                domains.company_id,
                companies.company_name
            FROM dim_domain AS domains
            LEFT JOIN dim_company AS companies ON companies.company_id = domains.company_id
            WHERE domains.domain_id = :domain_id
            """,
        ),
        {'domain_id': domain_id},
    )
    row = result.first()
    domain = dict(row._mapping) if row else None
    return domain


def resolve_scope(session: Session, country_id: int | None, domain_id: int | None) -> ChannelScope:
    """Resolve channel scope.
    Args:
        session (Session): Database session.
        country_id (int | None): Country identifier.
        domain_id (int | None): Domain identifier."""
    country = get_country(session, country_id)
    domain = get_domain(session, domain_id)
    if country_id is not None and country is None:
        raise HTTPException(status_code=404, detail='Country not found.')
    if domain_id is not None and domain is None:
        raise HTTPException(status_code=404, detail='Domain not found.')
    resolved_scope = ChannelScope(
        scope_type=scope_type(country_id, domain_id),
        country_id=country_id,
        country_name_en=country.get('country_name_en') if country else None,
        domain_id=domain_id,
        domain=domain.get('domain') if domain else None,
        company_id=domain.get('company_id') if domain else None,
        company_name=domain.get('company_name') if domain else None,
        is_estimated=country_id is not None,
    )
    return resolved_scope


def validate_dates(date_from: date, date_to: date) -> str:
    """Validate date range.
    Args:
        date_from (date): Period start date.
        date_to (date): Period end date."""
    if date_from > date_to:
        return 'INVALID_PERIOD'
    return ''
