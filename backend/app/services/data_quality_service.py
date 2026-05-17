import json
from datetime import date
from pathlib import Path

import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.data_upload import QualityResult, QualitySummary
from app.services.ingestion_run_service import update_quality
from app.services.report_detector import REQUIRED_COLUMNS, normalize_columns, validate_columns


FACT_TABLES = {
    'traffic_countries_daily': {
        'table_name': 'fact_domain_country_daily',
        'duplicate_columns': ['date_id', 'domain_id', 'country_id', 'source_file_id'],
        'range_columns': ['traffic', 'traffic_share', 'unique_visitors', 'pages_per_visit', 'bounce_rate'],
    },
    'domain_device_daily': {
        'table_name': 'fact_domain_device_daily',
        'duplicate_columns': ['date_id', 'domain_id', 'source_file_id'],
        'range_columns': ['visits_total', 'visits_desktop', 'visits_mobile', 'unique_total'],
    },
    'domain_channel_daily': {
        'table_name': 'fact_domain_channel_daily',
        'duplicate_columns': ['date_id', 'domain_id', 'channel_id', 'source_file_id'],
        'range_columns': ['traffic', 'traffic_share'],
    },
    'domain_journey_source_daily': {
        'table_name': 'fact_domain_journey_source_daily',
        'duplicate_columns': ['date_id', 'domain_id', 'journey_source_id', 'source_file_id'],
        'range_columns': ['traffic', 'traffic_share', 'change_value', 'change_rate'],
    },
    'audience_demographics_daily': {
        'table_name': 'fact_audience_demographics_daily',
        'duplicate_columns': ['date_id', 'domain_id', 'country_id', 'audience_segment_id', 'source_file_id'],
        'range_columns': ['traffic', 'traffic_share', 'confidence_score'],
    },
    'organic_keywords_daily': {
        'table_name': 'fact_organic_keyword_daily',
        'duplicate_columns': ['date_id', 'domain_id', 'country_id', 'keyword_id', 'source_file_id'],
        'range_columns': ['position', 'search_volume', 'estimated_traffic', 'traffic_share', 'keyword_difficulty'],
    },
    'paid_keywords_daily': {
        'table_name': 'fact_paid_keyword_daily',
        'duplicate_columns': ['date_id', 'domain_id', 'country_id', 'keyword_id', 'source_file_id'],
        'range_columns': ['position', 'search_volume', 'estimated_traffic', 'traffic_share', 'cpc', 'estimated_cost', 'competition'],
    },
    'top_pages_daily': {
        'table_name': 'fact_top_page_daily',
        'duplicate_columns': ['date_id', 'domain_id', 'country_id', 'page_id', 'source_file_id'],
        'range_columns': ['estimated_traffic', 'traffic_share', 'organic_traffic', 'paid_traffic', 'keywords_count', 'backlinks_count'],
    },
    'ads_creatives_daily': {
        'table_name': 'fact_ad_creative_daily',
        'duplicate_columns': ['date_id', 'domain_id', 'country_id', 'creative_hash', 'source_file_id'],
        'range_columns': ['estimated_spend', 'estimated_traffic'],
    },
    'backlinks_daily': {
        'table_name': 'fact_referring_domain_daily',
        'duplicate_columns': ['date_id', 'domain_id', 'country_id', 'referring_domain', 'source_file_id'],
        'range_columns': ['backlinks_count', 'authority_score', 'estimated_referral_traffic'],
    },
    'referring_domains_daily': {
        'table_name': 'fact_referring_domain_daily',
        'duplicate_columns': ['date_id', 'domain_id', 'country_id', 'referring_domain', 'source_file_id'],
        'range_columns': ['backlinks_count', 'authority_score', 'estimated_referral_traffic'],
    },
}

RECOMMENDED_COLUMNS = {
    'traffic_countries_daily': [
        'unique visitors',
        'desktop',
        'mobile',
        'bounce rate',
        'traffic_no_bounce',
        'traffic_bounce',
        'pages per visit',
        'average visit duration',
    ],
    'domain_device_daily': [
        'unique_devices',
        'unique_desktop',
        'unique_mobile',
        'all_no_bounce',
        'all_bounce',
        'desktop_no_bounce',
        'desktop_bounce',
        'mobile_no_bounce',
        'mobile_bounce',
    ],
    'domain_journey_source_daily': ['traffic share', 'search', 'changes'],
    'audience_demographics_daily': ['traffic share', 'confidence_score'],
    'organic_keywords_daily': ['position', 'search volume', 'estimated traffic', 'keyword difficulty'],
    'paid_keywords_daily': ['position', 'search volume', 'cpc', 'estimated cost', 'competition'],
    'top_pages_daily': ['estimated traffic', 'organic traffic', 'paid traffic', 'keywords_count'],
    'ads_creatives_daily': ['headline', 'description', 'cta', 'landing page', 'estimated spend'],
    'backlinks_daily': ['source url', 'target url', 'backlinks_count', 'authority_score'],
    'referring_domains_daily': ['source url', 'target url', 'backlinks_count', 'authority_score'],
}

NUMERIC_COLUMNS = {
    'traffic_countries_daily': ['traffic', 'unique visitors', 'desktop', 'mobile', 'bounce rate'],
    'domain_device_daily': ['visits_devices', 'visits_desktop', 'visits_mobile', 'unique_devices'],
    'domain_channel_daily': ['direct', 'referral', 'paid', 'social', 'search'],
    'domain_journey_source_daily': ['traffic', 'traffic share', 'changes'],
    'audience_demographics_daily': ['traffic', 'traffic share', 'confidence_score'],
    'organic_keywords_daily': ['position', 'search volume', 'estimated traffic', 'keyword difficulty'],
    'paid_keywords_daily': ['position', 'search volume', 'estimated traffic', 'cpc', 'estimated cost', 'competition'],
    'top_pages_daily': ['estimated traffic', 'organic traffic', 'paid traffic', 'keywords_count', 'backlinks_count'],
    'ads_creatives_daily': ['estimated spend', 'estimated traffic'],
    'backlinks_daily': ['backlinks_count', 'authority_score', 'estimated_referral_traffic'],
    'referring_domains_daily': ['backlinks_count', 'authority_score', 'estimated_referral_traffic'],
}


def json_value(value: object) -> str:
    """Build JSON value.
    Args:
        value (object): Source value."""
    data = json.dumps(value, default=str)
    return data


def list_files(session: Session, run_id: int) -> list[dict[str, object]]:
    """List quality files.
    Args:
        session (Session): Database session.
        run_id (int): Ingestion run identifier."""
    result = session.execute(
        text(
            """
            SELECT file_id, source_file_name, report_type, file_path
            FROM source_files
            WHERE run_id = :run_id
            ORDER BY file_id
            """,
        ),
        {'run_id': run_id},
    )
    files = [dict(row._mapping) for row in result]
    return files


def get_period(session: Session, run_id: int) -> tuple[date | None, date | None]:
    """Get run period.
    Args:
        session (Session): Database session.
        run_id (int): Ingestion run identifier."""
    result = session.execute(
        text('SELECT period_start, period_end FROM ingestion_runs WHERE run_id = :run_id'),
        {'run_id': run_id},
    )
    row = result.first()
    period = (row.period_start, row.period_end) if row else (None, None)
    return period


def clear_checks(session: Session, run_id: int) -> int:
    """Clear quality checks.
    Args:
        session (Session): Database session.
        run_id (int): Ingestion run identifier."""
    session.execute(
        text(
            """
            DELETE FROM data_quality_checks
            WHERE run_id = :run_id AND quality_dimension IS NOT NULL
            """,
        ),
        {'run_id': run_id},
    )
    return run_id


def save_check(
    session: Session,
    run_id: int,
    file_id: int | None,
    table_name: str | None,
    check_name: str,
    check_type: str,
    quality_dimension: str,
    status: str,
    severity: str,
    message: str,
    affected_rows_count: int | None = None,
    details: dict[str, object] | None = None,
    sample_rows: list[dict[str, object]] | None = None,
) -> int:
    """Save quality check.
    Args:
        session (Session): Database session.
        run_id (int): Ingestion run identifier.
        file_id (int | None): Source file identifier.
        table_name (str | None): Target table name.
        check_name (str): Check name.
        check_type (str): Check type.
        quality_dimension (str): Quality dimension.
        status (str): Check status.
        severity (str): Check severity.
        message (str): Check message.
        affected_rows_count (int | None): Affected row count.
        details (dict[str, object] | None): Check details.
        sample_rows (list[dict[str, object]] | None): Sample rows."""
    result = session.execute(
        text(
            """
            INSERT INTO data_quality_checks (
                run_id, file_id, table_name, check_name, check_type, status, severity, message,
                affected_rows_count, sample_rows, quality_dimension, details
            )
            VALUES (
                :run_id, :file_id, :table_name, :check_name, :check_type, :status, :severity, :message,
                :affected_rows_count, CAST(:sample_rows AS jsonb), :quality_dimension, CAST(:details AS jsonb)
            )
            RETURNING check_id
            """,
        ),
        {
            'run_id': run_id,
            'file_id': file_id,
            'table_name': table_name,
            'check_name': check_name,
            'check_type': check_type,
            'status': status,
            'severity': severity,
            'message': message,
            'affected_rows_count': affected_rows_count,
            'sample_rows': json_value(sample_rows or []),
            'quality_dimension': quality_dimension,
            'details': json_value(details or {}),
        },
    )
    check_id = int(result.scalar_one())
    return check_id


def read_file(file_data: dict[str, object]) -> tuple[pd.DataFrame | None, list[str]]:
    """Read quality file.
    Args:
        file_data (dict[str, object]): Source file metadata."""
    file_path = Path(str(file_data.get('file_path') or ''))
    errors = []
    if not file_path.exists():
        errors.append('Source file is missing on disk.')
        return None, errors
    try:
        data = pd.read_excel(file_path)
    except Exception as exc:
        errors.append(f'Excel file is not readable: {exc}')
        return None, errors
    return data, errors


def sample_data(data: pd.DataFrame) -> list[dict[str, object]]:
    """Build sample rows.
    Args:
        data (pd.DataFrame): Source data."""
    sample_rows = data.head(5).astype(str).to_dict(orient='records')
    return sample_rows


def schema_checks(session: Session, run_id: int, file_data: dict[str, object], data: pd.DataFrame) -> int:
    """Run schema checks.
    Args:
        session (Session): Database session.
        run_id (int): Ingestion run identifier.
        file_data (dict[str, object]): Source file metadata.
        data (pd.DataFrame): Source data."""
    report_type = str(file_data['report_type'])
    file_id = int(file_data['file_id'])
    missing_columns = validate_columns(report_type, list(data.columns))
    status = 'failed' if missing_columns else 'passed'
    severity = 'critical' if missing_columns else 'info'
    message = (
        f'Missing required columns: {", ".join(missing_columns)}'
        if missing_columns
        else 'All required columns are present.'
    )
    save_check(
        session,
        run_id,
        file_id,
        None,
        'required_columns_present',
        'schema',
        'schema',
        status,
        severity,
        message,
        len(missing_columns),
        {'missing_columns': missing_columns, 'required_columns': REQUIRED_COLUMNS.get(report_type, [])},
    )
    normalized_columns = normalize_columns(list(data.columns))
    empty_columns = [column for column in data.columns if data[column].isna().all()]
    save_check(
        session,
        run_id,
        file_id,
        None,
        'empty_columns_absent',
        'schema',
        'schema',
        'warning' if empty_columns else 'passed',
        'warning' if empty_columns else 'info',
        f'Empty columns found: {", ".join(map(str, empty_columns))}' if empty_columns else 'No fully empty columns found.',
        len(empty_columns),
        {'empty_columns': [str(column) for column in empty_columns]},
    )
    recommended_missing = [
        column for column in RECOMMENDED_COLUMNS.get(report_type, []) if column not in normalized_columns
    ]
    if recommended_missing:
        save_check(
            session,
            run_id,
            file_id,
            None,
            'recommended_columns_present',
            'schema',
            'schema',
            'warning',
            'warning',
            f'Recommended columns are missing: {", ".join(recommended_missing)}',
            len(recommended_missing),
            {'missing_columns': recommended_missing},
        )
    return len(missing_columns) + len(empty_columns) + len(recommended_missing)


def type_checks(session: Session, run_id: int, file_data: dict[str, object], data: pd.DataFrame) -> int:
    """Run type checks.
    Args:
        session (Session): Database session.
        run_id (int): Ingestion run identifier.
        file_data (dict[str, object]): Source file metadata.
        data (pd.DataFrame): Source data."""
    report_type = str(file_data['report_type'])
    file_id = int(file_data['file_id'])
    columns = {str(column).strip().lower(): column for column in data.columns}
    issue_count = 0
    if 'date' in columns:
        invalid_dates = pd.to_datetime(data[columns['date']], errors='coerce').isna()
        affected_rows = int(invalid_dates.sum())
        issue_count += affected_rows
        save_check(
            session,
            run_id,
            file_id,
            None,
            'date_values_parse',
            'types',
            'types',
            'failed' if affected_rows else 'passed',
            'critical' if affected_rows else 'info',
            f'{affected_rows} rows have invalid dates.' if affected_rows else 'All date values are valid.',
            affected_rows,
            {'column': 'date'},
            sample_data(data[invalid_dates]),
        )
    for column_name in NUMERIC_COLUMNS.get(report_type, []):
        if column_name not in columns:
            continue
        normalized_values = data[columns[column_name]].astype(str).str.replace('%', '', regex=False)
        numeric_values = pd.to_numeric(normalized_values.str.replace(',', '.', regex=False), errors='coerce')
        invalid_numbers = numeric_values.isna() & data[columns[column_name]].notna()
        affected_rows = int(invalid_numbers.sum())
        issue_count += affected_rows
        save_check(
            session,
            run_id,
            file_id,
            None,
            f'{column_name}_numeric_parse',
            'types',
            'types',
            'failed' if affected_rows else 'passed',
            'critical' if affected_rows else 'info',
            f'{affected_rows} rows have invalid numeric values.' if affected_rows else f'{column_name} parses as numeric.',
            affected_rows,
            {'column': column_name},
            sample_data(data[invalid_numbers]),
        )
    return issue_count


def date_checks(
    session: Session,
    run_id: int,
    file_data: dict[str, object],
    data: pd.DataFrame,
    period_start: date | None,
    period_end: date | None,
) -> int:
    """Run date checks.
    Args:
        session (Session): Database session.
        run_id (int): Ingestion run identifier.
        file_data (dict[str, object]): Source file metadata.
        data (pd.DataFrame): Source data.
        period_start (date | None): Period start date.
        period_end (date | None): Period end date."""
    file_id = int(file_data['file_id'])
    columns = {str(column).strip().lower(): column for column in data.columns}
    if 'date' not in columns:
        return 0
    parsed_dates = pd.to_datetime(data[columns['date']], errors='coerce')
    null_dates = parsed_dates.isna()
    save_check(
        session,
        run_id,
        file_id,
        None,
        'date_values_not_null',
        'dates',
        'dates',
        'failed' if int(null_dates.sum()) else 'passed',
        'critical' if int(null_dates.sum()) else 'info',
        f'{int(null_dates.sum())} rows have null dates.' if int(null_dates.sum()) else 'No null dates found.',
        int(null_dates.sum()),
        {'column': 'date'},
        sample_data(data[null_dates]),
    )
    period_mask = pd.Series(False, index=data.index)
    if period_start is not None:
        period_mask = period_mask | (parsed_dates.dt.date < period_start)
    if period_end is not None:
        period_mask = period_mask | (parsed_dates.dt.date > period_end)
    affected_rows = int(period_mask.sum())
    save_check(
        session,
        run_id,
        file_id,
        None,
        'dates_inside_upload_period',
        'dates',
        'dates',
        'warning' if affected_rows else 'passed',
        'warning' if affected_rows else 'info',
        f'{affected_rows} rows are outside upload period.' if affected_rows else 'All dates are inside upload period.',
        affected_rows,
        {'period_start': period_start, 'period_end': period_end},
        sample_data(data[period_mask]),
    )
    return int(null_dates.sum()) + affected_rows


def count_query(session: Session, query: str, params: dict[str, object]) -> int:
    """Run count query.
    Args:
        session (Session): Database session.
        query (str): SQL query.
        params (dict[str, object]): Query parameters."""
    result = session.execute(text(query), params)
    count_value = int(result.scalar_one() or 0)
    return count_value


def duplicate_checks(session: Session, run_id: int, file_data: dict[str, object]) -> int:
    """Run duplicate checks.
    Args:
        session (Session): Database session.
        run_id (int): Ingestion run identifier.
        file_data (dict[str, object]): Source file metadata."""
    report_type = str(file_data['report_type'])
    table_config = FACT_TABLES.get(report_type)
    if table_config is None:
        return 0
    file_id = int(file_data['file_id'])
    table_name = str(table_config['table_name'])
    duplicate_columns = ', '.join(table_config['duplicate_columns'])
    duplicate_count = count_query(
        session,
        f"""
        SELECT COALESCE(SUM(row_count - 1), 0)
        FROM (
            SELECT COUNT(*) AS row_count
            FROM {table_name}
            WHERE source_file_id = :file_id
            GROUP BY {duplicate_columns}
            HAVING COUNT(*) > 1
        ) AS duplicates
        """,
        {'file_id': file_id},
    )
    save_check(
        session,
        run_id,
        file_id,
        table_name,
        'fact_duplicates_absent',
        'duplicates',
        'duplicates',
        'warning' if duplicate_count else 'passed',
        'warning' if duplicate_count else 'info',
        f'{duplicate_count} duplicate fact rows found.' if duplicate_count else 'No duplicate fact rows found.',
        duplicate_count,
        {'duplicate_columns': table_config['duplicate_columns']},
    )
    return duplicate_count


def range_checks(session: Session, run_id: int, file_data: dict[str, object]) -> int:
    """Run range checks.
    Args:
        session (Session): Database session.
        run_id (int): Ingestion run identifier.
        file_data (dict[str, object]): Source file metadata."""
    report_type = str(file_data['report_type'])
    table_config = FACT_TABLES.get(report_type)
    if table_config is None:
        return 0
    file_id = int(file_data['file_id'])
    table_name = str(table_config['table_name'])
    issue_count = 0
    for column_name in table_config['range_columns']:
        negative_count = count_query(
            session,
            f"""
            SELECT COUNT(*)
            FROM {table_name}
            WHERE source_file_id = :file_id AND {column_name} < 0
            """,
            {'file_id': file_id},
        )
        issue_count += negative_count
        save_check(
            session,
            run_id,
            file_id,
            table_name,
            f'{column_name}_non_negative',
            'ranges',
            'ranges',
            'failed' if negative_count else 'passed',
            'critical' if negative_count else 'info',
            f'{negative_count} negative values found in {column_name}.'
            if negative_count
            else f'{column_name} values are non-negative.',
            negative_count,
            {'column': column_name},
        )
    return issue_count


def reference_checks(session: Session, run_id: int, file_data: dict[str, object]) -> int:
    """Run reference checks.
    Args:
        session (Session): Database session.
        run_id (int): Ingestion run identifier.
        file_data (dict[str, object]): Source file metadata."""
    report_type = str(file_data['report_type'])
    table_config = FACT_TABLES.get(report_type)
    if table_config is None:
        return 0
    file_id = int(file_data['file_id'])
    table_name = str(table_config['table_name'])
    fact_count = count_query(
        session,
        f'SELECT COUNT(*) FROM {table_name} WHERE source_file_id = :file_id',
        {'file_id': file_id},
    )
    status = 'failed' if fact_count == 0 else 'passed'
    save_check(
        session,
        run_id,
        file_id,
        table_name,
        'fact_rows_loaded',
        'references',
        'references',
        status,
        'critical' if fact_count == 0 else 'info',
        'No fact rows were loaded.' if fact_count == 0 else f'{fact_count} fact rows are linked to dimensions.',
        0 if fact_count else 1,
        {'fact_count': fact_count},
    )
    return 0 if fact_count else 1


def reconciliation_checks(session: Session, run_id: int) -> int:
    """Run reconciliation checks.
    Args:
        session (Session): Database session.
        run_id (int): Ingestion run identifier."""
    save_check(
        session,
        run_id,
        None,
        None,
        'reconciliation_source_available',
        'reconciliation',
        'reconciliation',
        'passed',
        'info',
        'No reconciliation source was provided for this upload.',
        0,
        {'reconciliation_available': False},
    )
    return 0


def quality_status(session: Session, run_id: int) -> str:
    """Calculate quality status.
    Args:
        session (Session): Database session.
        run_id (int): Ingestion run identifier."""
    result = session.execute(
        text(
            """
            SELECT
                SUM(CASE WHEN status = 'failed' AND severity = 'critical' THEN 1 ELSE 0 END) AS critical_failed,
                SUM(CASE WHEN status IN ('warning', 'failed') AND severity <> 'critical' THEN 1 ELSE 0 END) AS warnings
            FROM data_quality_checks
            WHERE run_id = :run_id AND quality_dimension IS NOT NULL
            """,
        ),
        {'run_id': run_id},
    )
    row = result.first()
    if row and int(row.critical_failed or 0) > 0:
        return 'failed'
    if row and int(row.warnings or 0) > 0:
        return 'warning'
    return 'passed'


def quality_summary(session: Session, run_id: int) -> QualitySummary:
    """Build quality summary.
    Args:
        session (Session): Database session.
        run_id (int): Ingestion run identifier."""
    result = session.execute(
        text(
            """
            SELECT
                COUNT(*) AS total_checks,
                SUM(CASE WHEN status = 'passed' THEN 1 ELSE 0 END) AS passed,
                SUM(CASE WHEN status = 'warning' THEN 1 ELSE 0 END) AS warnings,
                SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS failed
            FROM data_quality_checks
            WHERE run_id = :run_id AND quality_dimension IS NOT NULL
            """,
        ),
        {'run_id': run_id},
    )
    row = result.first()
    summary = QualitySummary(
        total_checks=int(row.total_checks or 0),
        passed=int(row.passed or 0),
        warnings=int(row.warnings or 0),
        failed=int(row.failed or 0),
    )
    return summary


def list_checks(session: Session, run_id: int) -> list[dict[str, object]]:
    """List quality checks.
    Args:
        session (Session): Database session.
        run_id (int): Ingestion run identifier."""
    result = session.execute(
        text(
            """
            SELECT
                checks.check_id,
                files.source_file_name AS file_name,
                checks.table_name,
                checks.check_name,
                checks.check_type,
                checks.status,
                checks.severity,
                checks.message,
                checks.affected_rows_count,
                checks.quality_dimension
            FROM data_quality_checks AS checks
            LEFT JOIN source_files AS files ON files.file_id = checks.file_id
            WHERE checks.run_id = :run_id AND checks.quality_dimension IS NOT NULL
            ORDER BY checks.check_id
            """,
        ),
        {'run_id': run_id},
    )
    checks = [dict(row._mapping) for row in result]
    return checks


def run_quality(session: Session, run_id: int) -> QualityResult:
    """Run quality checks.
    Args:
        session (Session): Database session.
        run_id (int): Ingestion run identifier."""
    clear_checks(session, run_id)
    period_start, period_end = get_period(session, run_id)
    files = list_files(session, run_id)
    for file_data in files:
        report_type = str(file_data['report_type'])
        file_id = int(file_data['file_id'])
        if report_type == 'unknown':
            save_check(
                session,
                run_id,
                file_id,
                None,
                'report_type_known',
                'schema',
                'schema',
                'failed',
                'critical',
                'Report type is unknown.',
                1,
                {'report_type': report_type},
            )
            continue
        data, errors = read_file(file_data)
        if errors or data is None:
            save_check(
                session,
                run_id,
                file_id,
                None,
                'source_file_readable',
                'schema',
                'schema',
                'failed',
                'critical',
                '; '.join(errors),
                len(errors),
                {'errors': errors},
            )
            continue
        schema_checks(session, run_id, file_data, data)
        type_checks(session, run_id, file_data, data)
        date_checks(session, run_id, file_data, data, period_start, period_end)
        reference_checks(session, run_id, file_data)
        duplicate_checks(session, run_id, file_data)
        range_checks(session, run_id, file_data)
    reconciliation_checks(session, run_id)
    status = quality_status(session, run_id)
    update_quality(session, run_id, status)
    session.commit()
    result = QualityResult(
        run_id=run_id,
        quality_status=status,
        summary=quality_summary(session, run_id),
        checks=list_checks(session, run_id),
    )
    return result


def get_quality(session: Session, run_id: int) -> QualityResult:
    """Get quality checks.
    Args:
        session (Session): Database session.
        run_id (int): Ingestion run identifier."""
    result = session.execute(
        text('SELECT quality_status FROM ingestion_runs WHERE run_id = :run_id'),
        {'run_id': run_id},
    )
    quality_value = result.scalar_one_or_none()
    status = str(quality_value or 'not_run')
    quality_result = QualityResult(
        run_id=run_id,
        quality_status=status,
        summary=quality_summary(session, run_id),
        checks=list_checks(session, run_id),
    )
    return quality_result


def summary_runs(session: Session) -> list[dict[str, object]]:
    """Summarize quality runs.
    Args:
        session (Session): Database session."""
    result = session.execute(
        text(
            """
            SELECT
                runs.run_id,
                runs.started_at::text AS started_at,
                runs.status,
                runs.quality_status,
                COUNT(checks.check_id) AS total_checks,
                SUM(CASE WHEN checks.status = 'failed' THEN 1 ELSE 0 END) AS failed,
                SUM(CASE WHEN checks.status = 'warning' THEN 1 ELSE 0 END) AS warnings
            FROM ingestion_runs AS runs
            LEFT JOIN data_quality_checks AS checks
                ON checks.run_id = runs.run_id AND checks.quality_dimension IS NOT NULL
            GROUP BY runs.run_id, runs.started_at, runs.status, runs.quality_status
            ORDER BY runs.started_at DESC NULLS LAST, runs.run_id DESC
            LIMIT 50
            """,
        ),
    )
    rows = [dict(row._mapping) for row in result]
    return rows
