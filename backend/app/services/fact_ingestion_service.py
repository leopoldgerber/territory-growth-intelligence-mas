from decimal import Decimal, InvalidOperation

import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.reference_ingestion_service import (
    clean_value,
    get_channel,
    upsert_company,
    upsert_country,
    upsert_date,
    upsert_domain,
    upsert_journey,
)


def number_value(value: object) -> Decimal | None:
    """Convert numeric value.
    Args:
        value (object): Source value."""
    if pd.isna(value):
        return None
    try:
        normalized_value = str(value).replace('%', '').replace(',', '.').replace(' ', '')
        numeric_value = Decimal(normalized_value)
    except (InvalidOperation, ValueError):
        return None
    return numeric_value


def column_map(data: pd.DataFrame) -> dict[str, str]:
    """Map columns.
    Args:
        data (pd.DataFrame): Source data."""
    columns = {str(column).strip().lower(): column for column in data.columns}
    return columns


def row_context(session: Session, row: pd.Series, columns: dict[str, str]) -> dict[str, object] | None:
    """Build row context.
    Args:
        session (Session): Database session.
        row (pd.Series): Source row.
        columns (dict[str, str]): Column map."""
    date_data = upsert_date(session, row[columns['date']])
    company_id = upsert_company(session, row[columns['company']])
    domain_id = upsert_domain(session, row[columns['domain']], company_id)
    if date_data is None or domain_id is None:
        return None
    context = {
        'date_id': date_data[0],
        'date': date_data[1],
        'company_id': company_id,
        'domain_id': domain_id,
    }
    return context


def ingest_country(
    session: Session,
    data: pd.DataFrame,
    file_id: int,
    run_id: int,
    is_synthetic: bool,
) -> int:
    """Ingest country facts.
    Args:
        session (Session): Database session.
        data (pd.DataFrame): Source data.
        file_id (int): Source file identifier.
        run_id (int): Ingestion run identifier.
        is_synthetic (bool): Synthetic data flag."""
    columns = column_map(data)
    row_count = 0
    for index, row in data.iterrows():
        context = row_context(session, row, columns)
        country_id = upsert_country(session, row[columns['country']])
        if context is None or country_id is None:
            continue
        session.execute(
            text(
                """
                INSERT INTO fact_domain_country_daily (
                    date_id, date, domain_id, company_id, country_id, traffic, traffic_share,
                    is_synthetic, source_file_id, run_id, source_row_id
                )
                VALUES (
                    :date_id, :date, :domain_id, :company_id, :country_id, :traffic, :traffic_share,
                    :is_synthetic, :source_file_id, :run_id, :source_row_id
                )
                ON CONFLICT (date_id, domain_id, country_id, source_file_id) DO NOTHING
                """,
            ),
            {
                **context,
                'country_id': country_id,
                'traffic': number_value(row.get(columns.get('traffic'))),
                'traffic_share': number_value(row.get(columns.get('traffic share', ''))),
                'is_synthetic': is_synthetic,
                'source_file_id': file_id,
                'run_id': run_id,
                'source_row_id': str(index),
            },
        )
        row_count += 1
    return row_count


def ingest_device(
    session: Session,
    data: pd.DataFrame,
    file_id: int,
    run_id: int,
    is_synthetic: bool,
) -> int:
    """Ingest device facts.
    Args:
        session (Session): Database session.
        data (pd.DataFrame): Source data.
        file_id (int): Source file identifier.
        run_id (int): Ingestion run identifier.
        is_synthetic (bool): Synthetic data flag."""
    columns = column_map(data)
    row_count = 0
    for index, row in data.iterrows():
        context = row_context(session, row, columns)
        if context is None:
            continue
        session.execute(
            text(
                """
                INSERT INTO fact_domain_device_daily (
                    date_id, date, domain_id, company_id, visits_total, visits_desktop, visits_mobile,
                    is_synthetic, source_file_id, run_id, source_row_id
                )
                VALUES (
                    :date_id, :date, :domain_id, :company_id, :visits_total, :visits_desktop, :visits_mobile,
                    :is_synthetic, :source_file_id, :run_id, :source_row_id
                )
                ON CONFLICT (date_id, domain_id, source_file_id) DO NOTHING
                """,
            ),
            {
                **context,
                'visits_total': number_value(row.get(columns.get('visits_devices'))),
                'visits_desktop': number_value(row.get(columns.get('visits_desktop'))),
                'visits_mobile': number_value(row.get(columns.get('visits_mobile'))),
                'is_synthetic': is_synthetic,
                'source_file_id': file_id,
                'run_id': run_id,
                'source_row_id': str(index),
            },
        )
        row_count += 1
    return row_count


def ingest_channel(
    session: Session,
    data: pd.DataFrame,
    file_id: int,
    run_id: int,
    is_synthetic: bool,
) -> int:
    """Ingest channel facts.
    Args:
        session (Session): Database session.
        data (pd.DataFrame): Source data.
        file_id (int): Source file identifier.
        run_id (int): Ingestion run identifier.
        is_synthetic (bool): Synthetic data flag."""
    columns = column_map(data)
    channel_codes = ['direct', 'referral', 'paid', 'social', 'search']
    row_count = 0
    for index, row in data.iterrows():
        context = row_context(session, row, columns)
        if context is None:
            continue
        for channel_code in channel_codes:
            channel_id = get_channel(session, channel_code)
            session.execute(
                text(
                    """
                    INSERT INTO fact_domain_channel_daily (
                        date_id, date, domain_id, company_id, channel_id, traffic,
                        is_synthetic, source_file_id, run_id, source_row_id
                    )
                    VALUES (
                        :date_id, :date, :domain_id, :company_id, :channel_id, :traffic,
                        :is_synthetic, :source_file_id, :run_id, :source_row_id
                    )
                    ON CONFLICT (date_id, domain_id, channel_id, source_file_id) DO NOTHING
                    """,
                ),
                {
                    **context,
                    'channel_id': channel_id,
                    'traffic': number_value(row.get(columns.get(channel_code))),
                    'is_synthetic': is_synthetic,
                    'source_file_id': file_id,
                    'run_id': run_id,
                    'source_row_id': f'{index}:{channel_code}',
                },
            )
            row_count += 1
    return row_count


def ingest_journey(
    session: Session,
    data: pd.DataFrame,
    file_id: int,
    run_id: int,
    is_synthetic: bool,
) -> int:
    """Ingest journey facts.
    Args:
        session (Session): Database session.
        data (pd.DataFrame): Source data.
        file_id (int): Source file identifier.
        run_id (int): Ingestion run identifier.
        is_synthetic (bool): Synthetic data flag."""
    columns = column_map(data)
    row_count = 0
    for index, row in data.iterrows():
        context = row_context(session, row, columns)
        if context is None:
            continue
        source_name = clean_value(row.get(columns.get('source', ''), '')) or clean_value(row.get(columns.get('source name', ''), ''))
        source_type = clean_value(row[columns['source type']])
        traffic_type = clean_value(row[columns['traffic type']])
        journey_source_id, channel_id = upsert_journey(session, source_name, source_type, traffic_type)
        session.execute(
            text(
                """
                INSERT INTO fact_domain_journey_source_daily (
                    date_id, date, domain_id, company_id, journey_source_id, channel_id, source_type,
                    traffic_type, source_name_raw, traffic, is_synthetic, source_file_id, run_id, source_row_id
                )
                VALUES (
                    :date_id, :date, :domain_id, :company_id, :journey_source_id, :channel_id, :source_type,
                    :traffic_type, :source_name_raw, :traffic, :is_synthetic, :source_file_id, :run_id, :source_row_id
                )
                ON CONFLICT (date_id, domain_id, journey_source_id, source_file_id) DO NOTHING
                """,
            ),
            {
                **context,
                'journey_source_id': journey_source_id,
                'channel_id': channel_id,
                'source_type': source_type,
                'traffic_type': traffic_type,
                'source_name_raw': source_name,
                'traffic': number_value(row[columns['traffic']]),
                'is_synthetic': is_synthetic,
                'source_file_id': file_id,
                'run_id': run_id,
                'source_row_id': str(index),
            },
        )
        row_count += 1
    return row_count


def ingest_facts(
    session: Session,
    report_type: str,
    data: pd.DataFrame,
    file_id: int,
    run_id: int,
    is_synthetic: bool,
) -> int:
    """Ingest fact report.
    Args:
        session (Session): Database session.
        report_type (str): Report type.
        data (pd.DataFrame): Source data.
        file_id (int): Source file identifier.
        run_id (int): Ingestion run identifier.
        is_synthetic (bool): Synthetic data flag."""
    handlers = {
        'traffic_countries_daily': ingest_country,
        'domain_device_daily': ingest_device,
        'domain_channel_daily': ingest_channel,
        'domain_journey_source_daily': ingest_journey,
    }
    handler = handlers.get(report_type)
    row_count = handler(session, data, file_id, run_id, is_synthetic) if handler else 0
    return row_count
