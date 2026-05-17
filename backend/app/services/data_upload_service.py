import json
from datetime import date
from pathlib import Path

import pandas as pd
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.schemas.data_upload import UploadFileResult, UploadRunResult
from app.services.archive_service import collect_excels
from app.services.data_quality_service import run_quality
from app.services.extended_ingestion_service import ingest_extended
from app.services.fact_ingestion_service import ingest_facts
from app.services.ingestion_run_service import create_run, finish_run, update_quality
from app.services.reference_ingestion_service import ingest_reference
from app.services.report_detector import validate_columns, detect_type
from app.services.source_file_service import add_quality, create_file
from app.services.upload_service import file_hash, save_upload, validate_upload


REFERENCE_TYPES = {
    'calendar_daily',
    'domains_list',
    'company_list',
    'countries_en_list',
    'countries_ru_list',
    'countries_location_ru_list',
}

FACT_TYPES = {
    'traffic_countries_daily',
    'domain_device_daily',
    'domain_channel_daily',
    'domain_journey_source_daily',
}

EXTENDED_TYPES = {
    'audience_demographics_daily',
    'organic_keywords_daily',
    'paid_keywords_daily',
    'top_pages_daily',
    'ads_creatives_daily',
    'backlinks_daily',
    'referring_domains_daily',
}

PROJECT_SCOPED_TYPES = {
    'campaign_performance_daily',
}


def read_excel(file_path: Path) -> tuple[pd.DataFrame | None, list[str]]:
    """Read Excel data.
    Args:
        file_path (Path): Excel file path."""
    errors = []
    try:
        data = pd.read_excel(file_path)
    except Exception as exc:
        errors.append(f'Excel file is not readable: {exc}')
        return None, errors
    if data.empty:
        errors.append('Excel file is empty.')
    return data, errors


def process_excel(
    session: Session,
    file_path: Path,
    run_id: int,
    is_synthetic: bool,
) -> UploadFileResult:
    """Process Excel file.
    Args:
        session (Session): Database session.
        file_path (Path): Excel file path.
        run_id (int): Ingestion run identifier.
        is_synthetic (bool): Synthetic data flag."""
    report_type = detect_type(file_path)
    file_id = create_file(session, run_id, file_path, report_type, file_hash(file_path), is_synthetic)
    session.commit()
    warnings = []
    errors = []
    row_count = 0
    if report_type == 'unknown':
        warnings.append('Report type is not recognized. File was registered but not ingested.')
        add_quality(session, run_id, file_id, 'report_type_detection', 'warning', json.dumps({'warnings': warnings}))
        session.commit()
        return UploadFileResult(
            file_id=file_id,
            file_name=file_path.name,
            report_type=report_type,
            status='skipped',
            warnings=warnings,
        )
    if report_type in PROJECT_SCOPED_TYPES:
        warnings.append('Campaign performance must be uploaded from a project campaign page.')
        add_quality(session, run_id, file_id, 'project_scoped_ingestion', 'warning', json.dumps({'warnings': warnings}))
        session.commit()
        return UploadFileResult(
            file_id=file_id,
            file_name=file_path.name,
            report_type=report_type,
            status='skipped',
            warnings=warnings,
        )
    data, read_errors = read_excel(file_path)
    errors.extend(read_errors)
    if data is not None:
        missing_columns = validate_columns(report_type, list(data.columns))
        if missing_columns:
            errors.append(f'Missing required columns: {", ".join(missing_columns)}')
    if errors:
        add_quality(session, run_id, file_id, 'file_validation', 'failed', json.dumps({'errors': errors}))
        session.commit()
        return UploadFileResult(
            file_id=file_id,
            file_name=file_path.name,
            report_type=report_type,
            status='failed',
            errors=errors,
        )
    try:
        if report_type in REFERENCE_TYPES:
            row_count = ingest_reference(session, report_type, data)
        if report_type in FACT_TYPES:
            row_count = ingest_facts(session, report_type, data, file_id, run_id, is_synthetic)
        if report_type in EXTENDED_TYPES:
            row_count = ingest_extended(session, report_type, data, file_id, run_id, is_synthetic)
        add_quality(
            session,
            run_id,
            file_id,
            'file_ingestion',
            'passed',
            json.dumps({'row_count': row_count}),
        )
        session.commit()
    except Exception as exc:
        session.rollback()
        errors.append(str(exc))
        add_quality(session, run_id, file_id, 'file_ingestion', 'failed', json.dumps({'errors': errors}))
        session.commit()
        return UploadFileResult(
            file_id=file_id,
            file_name=file_path.name,
            report_type=report_type,
            status='failed',
            errors=errors,
        )
    return UploadFileResult(
        file_id=file_id,
        file_name=file_path.name,
        report_type=report_type,
        status='success',
        row_count=row_count,
        warnings=warnings,
    )


def upload_data(
    session: Session,
    upload_file: UploadFile,
    source_name: str,
    is_synthetic: bool,
    granularity: str,
    period_start: date | None,
    period_end: date | None,
) -> UploadRunResult:
    """Upload data file.
    Args:
        session (Session): Database session.
        upload_file (UploadFile): Uploaded file.
        source_name (str): Source name.
        is_synthetic (bool): Synthetic data flag.
        granularity (str): Data granularity.
        period_start (date | None): Period start date.
        period_end (date | None): Period end date."""
    validation_error = validate_upload(upload_file)
    if validation_error:
        return UploadRunResult(run_id=0, status='failed', errors=[validation_error])
    upload_path = save_upload(upload_file)
    run_id = create_run(session, source_name, granularity, period_start, period_end)
    session.commit()
    result = upload_data_path(session, upload_path, run_id, source_name, is_synthetic, granularity, period_start, period_end)
    return result


def upload_data_path(
    session: Session,
    upload_path: Path,
    run_id: int,
    source_name: str,
    is_synthetic: bool,
    granularity: str,
    period_start: date | None,
    period_end: date | None,
) -> UploadRunResult:
    """Upload data path.
    Args:
        session (Session): Database session.
        upload_path (Path): Saved upload path.
        run_id (int): Ingestion run identifier.
        source_name (str): Source name.
        is_synthetic (bool): Synthetic data flag.
        granularity (str): Data granularity.
        period_start (date | None): Period start date.
        period_end (date | None): Period end date."""
    excel_paths, archive_errors = collect_excels(upload_path)
    file_results = []
    warnings = archive_errors.copy()
    if not excel_paths:
        warnings.append('No Excel files were found for ingestion.')
    for excel_path in excel_paths:
        file_result = process_excel(session, excel_path, run_id, is_synthetic)
        file_results.append(file_result)
    row_count = sum(file_result.row_count for file_result in file_results)
    has_failed = any(file_result.status == 'failed' for file_result in file_results)
    has_success = any(file_result.status == 'success' for file_result in file_results)
    if has_failed and has_success:
        status = 'partial'
    elif has_failed or not has_success:
        status = 'failed'
    else:
        status = 'success'
    error_message = '; '.join(warnings) if warnings and status == 'failed' else None
    finish_run(session, run_id, status, row_count, error_message)
    session.commit()
    if file_results:
        quality_result = run_quality(session, run_id)
        quality_status = quality_result.quality_status
        quality_summary = quality_result.summary
    else:
        update_quality(session, run_id, 'failed')
        session.commit()
        quality_status = 'failed'
        quality_summary = None
    return UploadRunResult(
        run_id=run_id,
        status=status,
        quality_status=quality_status,
        quality_summary=quality_summary,
        row_count=row_count,
        files=file_results,
        warnings=warnings,
    )
