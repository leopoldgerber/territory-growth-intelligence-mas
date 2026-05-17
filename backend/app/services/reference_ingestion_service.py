from datetime import date

import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session


def clean_value(value: object) -> str:
    """Clean string value.
    Args:
        value (object): Source value."""
    if pd.isna(value):
        return ''
    cleaned_value = str(value).strip()
    return cleaned_value


def make_slug(value: str) -> str:
    """Build slug value.
    Args:
        value (str): Source value."""
    slug = value.strip().lower().replace(' ', '-')
    return slug


def date_identity(value: object) -> tuple[int, date] | None:
    """Build date identity.
    Args:
        value (object): Source date value."""
    parsed_date = pd.to_datetime(value, errors='coerce')
    if pd.isna(parsed_date):
        return None
    date_value = parsed_date.date()
    date_id = int(date_value.strftime('%Y%m%d'))
    return date_id, date_value


def upsert_date(session: Session, value: object) -> tuple[int, date] | None:
    """Upsert date dimension.
    Args:
        session (Session): Database session.
        value (object): Source date value."""
    date_data = date_identity(value)
    if date_data is None:
        return None
    date_id, date_value = date_data
    session.execute(
        text(
            """
            INSERT INTO dim_date (
                date_id, date, year, quarter, month_number, month_name_en, month_year,
                week_number, day_of_month, day_of_week, day_name_en, is_weekend, is_month_start, is_month_end
            )
            VALUES (
                :date_id, :date, :year, :quarter, :month_number, :month_name_en, :month_year,
                :week_number, :day_of_month, :day_of_week, :day_name_en, :is_weekend, :is_month_start, :is_month_end
            )
            ON CONFLICT (date_id) DO NOTHING
            """,
        ),
        {
            'date_id': date_id,
            'date': date_value,
            'year': date_value.year,
            'quarter': ((date_value.month - 1) // 3) + 1,
            'month_number': date_value.month,
            'month_name_en': date_value.strftime('%B'),
            'month_year': date_value.strftime('%Y-%m'),
            'week_number': date_value.isocalendar().week,
            'day_of_month': date_value.day,
            'day_of_week': date_value.isoweekday(),
            'day_name_en': date_value.strftime('%A'),
            'is_weekend': date_value.isoweekday() in [6, 7],
            'is_month_start': date_value.day == 1,
            'is_month_end': (date_value + pd.Timedelta(days=1)).month != date_value.month,
        },
    )
    return date_id, date_value


def upsert_company(session: Session, company_name: str) -> int | None:
    """Upsert company dimension.
    Args:
        session (Session): Database session.
        company_name (str): Company name."""
    cleaned_name = clean_value(company_name)
    if not cleaned_name:
        return None
    result = session.execute(
        text(
            """
            INSERT INTO dim_company (company_name, company_slug)
            VALUES (:company_name, :company_slug)
            ON CONFLICT (company_slug) DO UPDATE
            SET company_name = EXCLUDED.company_name, updated_at = now()
            RETURNING company_id
            """,
        ),
        {'company_name': cleaned_name, 'company_slug': make_slug(cleaned_name)},
    )
    company_id = int(result.scalar_one())
    return company_id


def upsert_domain(session: Session, domain: str, company_id: int | None) -> int | None:
    """Upsert domain dimension.
    Args:
        session (Session): Database session.
        domain (str): Domain value.
        company_id (int | None): Company identifier."""
    cleaned_domain = clean_value(domain).lower()
    if not cleaned_domain:
        return None
    root_domain = '.'.join(cleaned_domain.split('.')[-2:])
    result = session.execute(
        text(
            """
            INSERT INTO dim_domain (domain, root_domain, company_id)
            VALUES (:domain, :root_domain, :company_id)
            ON CONFLICT (domain) DO UPDATE
            SET company_id = COALESCE(EXCLUDED.company_id, dim_domain.company_id), updated_at = now()
            RETURNING domain_id
            """,
        ),
        {'domain': cleaned_domain, 'root_domain': root_domain, 'company_id': company_id},
    )
    domain_id = int(result.scalar_one())
    return domain_id


def upsert_region(session: Session, region_name: str) -> int | None:
    """Upsert region dimension.
    Args:
        session (Session): Database session.
        region_name (str): Region name."""
    cleaned_name = clean_value(region_name)
    if not cleaned_name:
        return None
    region_code = make_slug(cleaned_name)
    result = session.execute(
        text(
            """
            INSERT INTO dim_region (region_code, region_name)
            VALUES (:region_code, :region_name)
            ON CONFLICT (region_code) DO UPDATE
            SET region_name = EXCLUDED.region_name, updated_at = now()
            RETURNING region_id
            """,
        ),
        {'region_code': region_code, 'region_name': cleaned_name},
    )
    region_id = int(result.scalar_one())
    return region_id


def upsert_country(session: Session, country_name: str, region_id: int | None = None) -> int | None:
    """Upsert country dimension.
    Args:
        session (Session): Database session.
        country_name (str): Country name.
        region_id (int | None): Region identifier."""
    cleaned_name = clean_value(country_name)
    if not cleaned_name:
        return None
    country_code = make_slug(cleaned_name)[:10]
    result = session.execute(
        text(
            """
            INSERT INTO dim_country (region_id, country_code, country_name_en)
            VALUES (:region_id, :country_code, :country_name_en)
            ON CONFLICT (country_code) DO UPDATE
            SET region_id = COALESCE(EXCLUDED.region_id, dim_country.region_id), updated_at = now()
            RETURNING country_id
            """,
        ),
        {'region_id': region_id, 'country_code': country_code, 'country_name_en': cleaned_name},
    )
    country_id = int(result.scalar_one())
    return country_id


def get_channel(session: Session, channel_code: str) -> int:
    """Get channel dimension.
    Args:
        session (Session): Database session.
        channel_code (str): Channel code."""
    cleaned_code = clean_value(channel_code).lower()
    result = session.execute(
        text(
            """
            INSERT INTO dim_channel (channel_code, channel_name, channel_group)
            VALUES (:channel_code, :channel_name, :channel_group)
            ON CONFLICT (channel_code) DO UPDATE SET channel_name = EXCLUDED.channel_name
            RETURNING channel_id
            """,
        ),
        {
            'channel_code': cleaned_code,
            'channel_name': cleaned_code.replace('_', ' ').title(),
            'channel_group': 'uploaded',
        },
    )
    channel_id = int(result.scalar_one())
    return channel_id


def upsert_journey(session: Session, source_name: str, source_type: str, traffic_type: str) -> tuple[int, int]:
    """Upsert journey source.
    Args:
        session (Session): Database session.
        source_name (str): Journey source name.
        source_type (str): Source type.
        traffic_type (str): Traffic type."""
    channel_id = get_channel(session, traffic_type or 'unknown')
    cleaned_name = clean_value(source_name) or 'unknown'
    result = session.execute(
        text(
            """
            INSERT INTO dim_journey_source (channel_id, source_name, source_type)
            VALUES (:channel_id, :source_name, :source_type)
            ON CONFLICT (source_name, channel_id) DO UPDATE
            SET source_type = EXCLUDED.source_type
            RETURNING journey_source_id
            """,
        ),
        {'channel_id': channel_id, 'source_name': cleaned_name, 'source_type': clean_value(source_type)},
    )
    journey_source_id = int(result.scalar_one())
    return journey_source_id, channel_id


def ingest_reference(session: Session, report_type: str, data: pd.DataFrame) -> int:
    """Ingest reference report.
    Args:
        session (Session): Database session.
        report_type (str): Report type.
        data (pd.DataFrame): Report data."""
    row_count = 0
    columns = {str(column).strip().lower(): column for column in data.columns}
    if report_type == 'company_list':
        company_column = columns.get('company') or columns.get('company_name')
        for _, row in data.iterrows():
            if company_column:
                upsert_company(session, row[company_column])
                row_count += 1
    if report_type == 'domains_list':
        domain_column = columns.get('domain')
        company_column = columns.get('company') or columns.get('company_name')
        for _, row in data.iterrows():
            company_id = upsert_company(session, row[company_column]) if company_column else None
            if domain_column:
                upsert_domain(session, row[domain_column], company_id)
                row_count += 1
    if report_type in ['countries_en_list', 'countries_ru_list', 'countries_location_ru_list']:
        country_column = columns.get('country') or columns.get('country_name') or next(iter(columns.values()), None)
        region_column = columns.get('region')
        for _, row in data.iterrows():
            region_id = upsert_region(session, row[region_column]) if region_column else None
            if country_column:
                upsert_country(session, row[country_column], region_id)
                row_count += 1
    if report_type == 'calendar_daily':
        date_column = columns.get('date')
        for _, row in data.iterrows():
            if date_column:
                upsert_date(session, row[date_column])
                row_count += 1
    return row_count
