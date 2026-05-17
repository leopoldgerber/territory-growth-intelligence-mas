from decimal import Decimal, InvalidOperation
from hashlib import sha256
from urllib.parse import urlparse

import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.reference_ingestion_service import clean_value, upsert_company, upsert_country, upsert_date, upsert_domain


def column_map(data: pd.DataFrame) -> dict[str, str]:
    """Map columns.
    Args:
        data (pd.DataFrame): Source data."""
    columns = {str(column).strip().lower(): column for column in data.columns}
    return columns


def number_value(value: object) -> Decimal | None:
    """Convert number value.
    Args:
        value (object): Source value."""
    if value is None or pd.isna(value):
        return None
    try:
        normalized_value = str(value).replace('%', '').replace(',', '.').replace(' ', '')
        numeric_value = Decimal(normalized_value)
    except (InvalidOperation, ValueError):
        return None
    return numeric_value


def string_value(row: pd.Series, columns: dict[str, str], names: list[str], default: str = '') -> str:
    """Get string value.
    Args:
        row (pd.Series): Source row.
        columns (dict[str, str]): Column mapping.
        names (list[str]): Candidate column names.
        default (str): Default value."""
    for name in names:
        column = columns.get(name)
        if column is not None:
            value = clean_value(row.get(column))
            if value:
                return value
    return default


def numeric_value(row: pd.Series, columns: dict[str, str], names: list[str]) -> Decimal | None:
    """Get numeric value.
    Args:
        row (pd.Series): Source row.
        columns (dict[str, str]): Column mapping.
        names (list[str]): Candidate column names."""
    for name in names:
        column = columns.get(name)
        if column is not None:
            value = number_value(row.get(column))
            if value is not None:
                return value
    return None


def date_value(row: pd.Series, columns: dict[str, str], names: list[str]) -> object:
    """Get date value.
    Args:
        row (pd.Series): Source row.
        columns (dict[str, str]): Column mapping.
        names (list[str]): Candidate column names."""
    for name in names:
        column = columns.get(name)
        if column is not None:
            return row.get(column)
    return None


def row_context(session: Session, row: pd.Series, columns: dict[str, str]) -> dict[str, object] | None:
    """Build row context.
    Args:
        session (Session): Database session.
        row (pd.Series): Source row.
        columns (dict[str, str]): Column mapping."""
    date_data = upsert_date(session, date_value(row, columns, ['date', 'report date', 'period']))
    company_id = upsert_company(session, string_value(row, columns, ['company', 'company_name', 'brand'], 'Unknown'))
    domain_id = upsert_domain(session, string_value(row, columns, ['domain', 'site', 'website']), company_id)
    country_name = string_value(row, columns, ['country', 'country_name', 'database'])
    country_id = upsert_country(session, country_name) if country_name else None
    if date_data is None or domain_id is None:
        return None
    context = {
        'date_id': date_data[0],
        'date': date_data[1],
        'company_id': company_id,
        'domain_id': domain_id,
        'country_id': country_id,
    }
    return context


def hash_url(url: str) -> str:
    """Hash URL.
    Args:
        url (str): Source URL."""
    url_hash = sha256(url.strip().lower().encode('utf-8')).hexdigest()
    return url_hash


def page_path(url: str) -> str:
    """Extract path.
    Args:
        url (str): Source URL."""
    parsed_url = urlparse(url)
    path = parsed_url.path or '/'
    return path


def upsert_page(session: Session, domain_id: int, url: str, title: str = '', page_type: str = 'unknown') -> int | None:
    """Upsert page.
    Args:
        session (Session): Database session.
        domain_id (int): Domain identifier.
        url (str): Page URL.
        title (str): Page title.
        page_type (str): Page type."""
    cleaned_url = clean_value(url)
    if not cleaned_url:
        return None
    result = session.execute(
        text(
            """
            INSERT INTO dim_page (domain_id, url, url_hash, page_path, page_type, title, first_seen_date, last_seen_date)
            VALUES (:domain_id, :url, :url_hash, :page_path, :page_type, :title, CURRENT_DATE, CURRENT_DATE)
            ON CONFLICT (url_hash) DO UPDATE
            SET title = COALESCE(EXCLUDED.title, dim_page.title), last_seen_date = CURRENT_DATE
            RETURNING page_id
            """,
        ),
        {
            'domain_id': domain_id,
            'url': cleaned_url,
            'url_hash': hash_url(cleaned_url),
            'page_path': page_path(cleaned_url),
            'page_type': page_type or 'unknown',
            'title': title or None,
        },
    )
    page_id = int(result.scalar_one())
    return page_id


def upsert_keyword(
    session: Session,
    keyword_text: str,
    country_id: int | None,
    language_code: str | None,
    intent: str,
    is_branded: bool,
) -> int | None:
    """Upsert keyword.
    Args:
        session (Session): Database session.
        keyword_text (str): Keyword text.
        country_id (int | None): Country identifier.
        language_code (str | None): Language code.
        intent (str): Keyword intent.
        is_branded (bool): Branded flag."""
    cleaned_keyword = clean_value(keyword_text)
    if not cleaned_keyword:
        return None
    normalized_keyword = ' '.join(cleaned_keyword.lower().split())
    result = session.execute(
        text(
            """
            INSERT INTO dim_keyword (keyword_text, keyword_normalized, language_code, country_id, intent, is_branded)
            VALUES (:keyword_text, :keyword_normalized, :language_code, :country_id, :intent, :is_branded)
            ON CONFLICT (keyword_normalized, country_id, language_code) DO UPDATE
            SET keyword_text = EXCLUDED.keyword_text, intent = EXCLUDED.intent
            RETURNING keyword_id
            """,
        ),
        {
            'keyword_text': cleaned_keyword,
            'keyword_normalized': normalized_keyword,
            'language_code': language_code,
            'country_id': country_id,
            'intent': intent or 'unknown',
            'is_branded': is_branded,
        },
    )
    keyword_id = int(result.scalar_one())
    return keyword_id


def upsert_segment(session: Session, segment_type: str, segment_name: str, segment_value: str) -> int | None:
    """Upsert segment.
    Args:
        session (Session): Database session.
        segment_type (str): Segment type.
        segment_name (str): Segment name.
        segment_value (str): Segment value."""
    cleaned_name = clean_value(segment_name)
    if not cleaned_name:
        return None
    result = session.execute(
        text(
            """
            INSERT INTO dim_audience_segment (segment_type, segment_name, segment_value)
            VALUES (:segment_type, :segment_name, :segment_value)
            ON CONFLICT (segment_type, segment_name, segment_value) DO UPDATE
            SET segment_name = EXCLUDED.segment_name
            RETURNING audience_segment_id
            """,
        ),
        {'segment_type': segment_type or 'custom', 'segment_name': cleaned_name, 'segment_value': segment_value or None},
    )
    segment_id = int(result.scalar_one())
    return segment_id


def ingest_audience(session: Session, data: pd.DataFrame, file_id: int, run_id: int, is_synthetic: bool) -> int:
    """Ingest audience facts.
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
        segment_id = upsert_segment(
            session,
            string_value(row, columns, ['segment type', 'segment_type', 'type'], 'custom'),
            string_value(row, columns, ['segment', 'segment_name', 'audience segment', 'interest', 'age', 'gender']),
            string_value(row, columns, ['segment value', 'segment_value', 'value']),
        )
        if context is None or segment_id is None:
            continue
        session.execute(
            text(
                """
                INSERT INTO fact_audience_demographics_daily (
                    date_id, date, domain_id, company_id, country_id, is_synthetic, source_file_id, run_id,
                    source_row_id, audience_segment_id, traffic, traffic_share, confidence_score
                )
                VALUES (
                    :date_id, :date, :domain_id, :company_id, :country_id, :is_synthetic, :source_file_id, :run_id,
                    :source_row_id, :audience_segment_id, :traffic, :traffic_share, :confidence_score
                )
                ON CONFLICT (date_id, domain_id, country_id, audience_segment_id, source_file_id) DO NOTHING
                """,
            ),
            {
                **context,
                'is_synthetic': is_synthetic,
                'source_file_id': file_id,
                'run_id': run_id,
                'source_row_id': str(index),
                'audience_segment_id': segment_id,
                'traffic': numeric_value(row, columns, ['traffic', 'visits']),
                'traffic_share': numeric_value(row, columns, ['traffic share', 'traffic_share', 'share']),
                'confidence_score': numeric_value(row, columns, ['confidence', 'confidence_score']),
            },
        )
        row_count += 1
    return row_count


def ingest_keywords(
    session: Session,
    data: pd.DataFrame,
    file_id: int,
    run_id: int,
    is_synthetic: bool,
    paid_mode: bool,
) -> int:
    """Ingest keyword facts.
    Args:
        session (Session): Database session.
        data (pd.DataFrame): Source data.
        file_id (int): Source file identifier.
        run_id (int): Ingestion run identifier.
        is_synthetic (bool): Synthetic data flag.
        paid_mode (bool): Paid keyword flag."""
    columns = column_map(data)
    row_count = 0
    table_name = 'fact_paid_keyword_daily' if paid_mode else 'fact_organic_keyword_daily'
    for index, row in data.iterrows():
        context = row_context(session, row, columns)
        if context is None:
            continue
        keyword_id = upsert_keyword(
            session,
            string_value(row, columns, ['keyword', 'keyword_text', 'query']),
            context.get('country_id'),
            string_value(row, columns, ['language', 'language_code']),
            string_value(row, columns, ['intent'], 'unknown'),
            string_value(row, columns, ['branded', 'is_branded']).lower() in ['true', '1', 'yes'],
        )
        page_url = string_value(row, columns, ['url', 'page', 'landing page', 'landing_page'])
        page_id = upsert_page(session, int(context['domain_id']), page_url) if page_url else None
        if keyword_id is None:
            continue
        if paid_mode:
            session.execute(
                text(
                    f"""
                    INSERT INTO {table_name} (
                        date_id, date, domain_id, company_id, country_id, is_synthetic, source_file_id, run_id,
                        source_row_id, keyword_id, page_id, position, search_volume, estimated_traffic,
                        traffic_share, cpc, estimated_cost, competition, currency_code
                    )
                    VALUES (
                        :date_id, :date, :domain_id, :company_id, :country_id, :is_synthetic, :source_file_id, :run_id,
                        :source_row_id, :keyword_id, :page_id, :position, :search_volume, :estimated_traffic,
                        :traffic_share, :cpc, :estimated_cost, :competition, :currency_code
                    )
                    ON CONFLICT (date_id, domain_id, country_id, keyword_id, source_file_id) DO NOTHING
                    """,
                ),
                {
                    **context,
                    'is_synthetic': is_synthetic,
                    'source_file_id': file_id,
                    'run_id': run_id,
                    'source_row_id': str(index),
                    'keyword_id': keyword_id,
                    'page_id': page_id,
                    'position': numeric_value(row, columns, ['position', 'pos']),
                    'search_volume': numeric_value(row, columns, ['search volume', 'search_volume', 'volume']),
                    'estimated_traffic': numeric_value(row, columns, ['estimated traffic', 'estimated_traffic', 'traffic']),
                    'traffic_share': numeric_value(row, columns, ['traffic share', 'traffic_share']),
                    'cpc': numeric_value(row, columns, ['cpc', 'cost per click']),
                    'estimated_cost': numeric_value(row, columns, ['estimated cost', 'estimated_cost', 'traffic cost']),
                    'competition': numeric_value(row, columns, ['competition', 'competitive density']),
                    'currency_code': string_value(row, columns, ['currency', 'currency_code'], 'USD')[:3],
                },
            )
        else:
            session.execute(
                text(
                    f"""
                    INSERT INTO {table_name} (
                        date_id, date, domain_id, company_id, country_id, is_synthetic, source_file_id, run_id,
                        source_row_id, keyword_id, page_id, position, previous_position, search_volume,
                        estimated_traffic, traffic_share, keyword_difficulty
                    )
                    VALUES (
                        :date_id, :date, :domain_id, :company_id, :country_id, :is_synthetic, :source_file_id, :run_id,
                        :source_row_id, :keyword_id, :page_id, :position, :previous_position, :search_volume,
                        :estimated_traffic, :traffic_share, :keyword_difficulty
                    )
                    ON CONFLICT (date_id, domain_id, country_id, keyword_id, source_file_id) DO NOTHING
                    """,
                ),
                {
                    **context,
                    'is_synthetic': is_synthetic,
                    'source_file_id': file_id,
                    'run_id': run_id,
                    'source_row_id': str(index),
                    'keyword_id': keyword_id,
                    'page_id': page_id,
                    'position': numeric_value(row, columns, ['position', 'pos']),
                    'previous_position': numeric_value(row, columns, ['previous position', 'previous_position']),
                    'search_volume': numeric_value(row, columns, ['search volume', 'search_volume', 'volume']),
                    'estimated_traffic': numeric_value(row, columns, ['estimated traffic', 'estimated_traffic', 'traffic']),
                    'traffic_share': numeric_value(row, columns, ['traffic share', 'traffic_share']),
                    'keyword_difficulty': numeric_value(row, columns, ['keyword difficulty', 'keyword_difficulty', 'difficulty']),
                },
            )
        row_count += 1
    return row_count


def ingest_pages(session: Session, data: pd.DataFrame, file_id: int, run_id: int, is_synthetic: bool) -> int:
    """Ingest page facts.
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
        page_id = upsert_page(
            session,
            int(context['domain_id']),
            string_value(row, columns, ['url', 'page']),
            string_value(row, columns, ['title']),
            string_value(row, columns, ['page type', 'page_type'], 'unknown'),
        )
        if page_id is None:
            continue
        session.execute(
            text(
                """
                INSERT INTO fact_top_page_daily (
                    date_id, date, domain_id, company_id, country_id, is_synthetic, source_file_id, run_id,
                    source_row_id, page_id, estimated_traffic, traffic_share, organic_traffic, paid_traffic,
                    keywords_count, backlinks_count
                )
                VALUES (
                    :date_id, :date, :domain_id, :company_id, :country_id, :is_synthetic, :source_file_id, :run_id,
                    :source_row_id, :page_id, :estimated_traffic, :traffic_share, :organic_traffic, :paid_traffic,
                    :keywords_count, :backlinks_count
                )
                ON CONFLICT (date_id, domain_id, country_id, page_id, source_file_id) DO NOTHING
                """,
            ),
            {
                **context,
                'is_synthetic': is_synthetic,
                'source_file_id': file_id,
                'run_id': run_id,
                'source_row_id': str(index),
                'page_id': page_id,
                'estimated_traffic': numeric_value(row, columns, ['estimated traffic', 'estimated_traffic', 'traffic']),
                'traffic_share': numeric_value(row, columns, ['traffic share', 'traffic_share']),
                'organic_traffic': numeric_value(row, columns, ['organic traffic', 'organic_traffic']),
                'paid_traffic': numeric_value(row, columns, ['paid traffic', 'paid_traffic']),
                'keywords_count': numeric_value(row, columns, ['keywords', 'keywords_count']),
                'backlinks_count': numeric_value(row, columns, ['backlinks', 'backlinks_count']),
            },
        )
        row_count += 1
    return row_count


def ingest_ads(session: Session, data: pd.DataFrame, file_id: int, run_id: int, is_synthetic: bool) -> int:
    """Ingest ads facts.
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
        headline = string_value(row, columns, ['headline', 'title'])
        description = string_value(row, columns, ['description', 'text'])
        creative_hash = string_value(row, columns, ['creative hash', 'creative_hash']) or hash_url(f'{headline}|{description}')
        page_url = string_value(row, columns, ['landing page', 'landing_page', 'url'])
        page_id = upsert_page(session, int(context['domain_id']), page_url) if page_url else None
        session.execute(
            text(
                """
                INSERT INTO fact_ad_creative_daily (
                    date_id, date, domain_id, company_id, country_id, is_synthetic, source_file_id, run_id,
                    source_row_id, creative_hash, headline, description, cta, landing_page_id, ad_network,
                    estimated_spend, estimated_traffic, first_seen_date, last_seen_date
                )
                VALUES (
                    :date_id, :date, :domain_id, :company_id, :country_id, :is_synthetic, :source_file_id, :run_id,
                    :source_row_id, :creative_hash, :headline, :description, :cta, :landing_page_id, :ad_network,
                    :estimated_spend, :estimated_traffic, :first_seen_date, :last_seen_date
                )
                ON CONFLICT (date_id, domain_id, country_id, creative_hash, source_file_id) DO NOTHING
                """,
            ),
            {
                **context,
                'is_synthetic': is_synthetic,
                'source_file_id': file_id,
                'run_id': run_id,
                'source_row_id': str(index),
                'creative_hash': creative_hash,
                'headline': headline or None,
                'description': description or None,
                'cta': string_value(row, columns, ['cta', 'call to action']) or None,
                'landing_page_id': page_id,
                'ad_network': string_value(row, columns, ['ad network', 'ad_network', 'network']) or None,
                'estimated_spend': numeric_value(row, columns, ['estimated spend', 'estimated_spend', 'spend']),
                'estimated_traffic': numeric_value(row, columns, ['estimated traffic', 'estimated_traffic', 'traffic']),
                'first_seen_date': date_value(row, columns, ['first seen', 'first_seen_date']),
                'last_seen_date': date_value(row, columns, ['last seen', 'last_seen_date']),
            },
        )
        row_count += 1
    return row_count


def ingest_backlinks(session: Session, data: pd.DataFrame, file_id: int, run_id: int, is_synthetic: bool) -> int:
    """Ingest backlinks facts.
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
        referring_domain = string_value(row, columns, ['referring domain', 'referring_domain', 'source domain'])
        if context is None or not referring_domain:
            continue
        session.execute(
            text(
                """
                INSERT INTO fact_referring_domain_daily (
                    date_id, date, domain_id, company_id, country_id, is_synthetic, source_file_id, run_id,
                    source_row_id, referring_domain, source_url, target_url, link_type, anchor_text,
                    backlinks_count, authority_score, estimated_referral_traffic
                )
                VALUES (
                    :date_id, :date, :domain_id, :company_id, :country_id, :is_synthetic, :source_file_id, :run_id,
                    :source_row_id, :referring_domain, :source_url, :target_url, :link_type, :anchor_text,
                    :backlinks_count, :authority_score, :estimated_referral_traffic
                )
                ON CONFLICT (date_id, domain_id, country_id, referring_domain, source_file_id) DO NOTHING
                """,
            ),
            {
                **context,
                'is_synthetic': is_synthetic,
                'source_file_id': file_id,
                'run_id': run_id,
                'source_row_id': str(index),
                'referring_domain': referring_domain,
                'source_url': string_value(row, columns, ['source url', 'source_url']) or None,
                'target_url': string_value(row, columns, ['target url', 'target_url']) or None,
                'link_type': string_value(row, columns, ['link type', 'link_type']) or None,
                'anchor_text': string_value(row, columns, ['anchor', 'anchor_text']) or None,
                'backlinks_count': numeric_value(row, columns, ['backlinks', 'backlinks_count']),
                'authority_score': numeric_value(row, columns, ['authority', 'authority_score']),
                'estimated_referral_traffic': numeric_value(row, columns, ['referral traffic', 'estimated_referral_traffic']),
            },
        )
        row_count += 1
    return row_count


def ingest_extended(
    session: Session,
    report_type: str,
    data: pd.DataFrame,
    file_id: int,
    run_id: int,
    is_synthetic: bool,
) -> int:
    """Ingest extended report.
    Args:
        session (Session): Database session.
        report_type (str): Report type.
        data (pd.DataFrame): Source data.
        file_id (int): Source file identifier.
        run_id (int): Ingestion run identifier.
        is_synthetic (bool): Synthetic data flag."""
    handlers = {
        'audience_demographics_daily': lambda: ingest_audience(session, data, file_id, run_id, is_synthetic),
        'organic_keywords_daily': lambda: ingest_keywords(session, data, file_id, run_id, is_synthetic, False),
        'paid_keywords_daily': lambda: ingest_keywords(session, data, file_id, run_id, is_synthetic, True),
        'top_pages_daily': lambda: ingest_pages(session, data, file_id, run_id, is_synthetic),
        'ads_creatives_daily': lambda: ingest_ads(session, data, file_id, run_id, is_synthetic),
        'backlinks_daily': lambda: ingest_backlinks(session, data, file_id, run_id, is_synthetic),
        'referring_domains_daily': lambda: ingest_backlinks(session, data, file_id, run_id, is_synthetic),
    }
    handler = handlers.get(report_type)
    row_count = handler() if handler else 0
    return row_count
