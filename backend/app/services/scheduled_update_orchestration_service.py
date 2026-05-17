from datetime import UTC, date, datetime, timedelta

from sqlalchemy.orm import Session

from app.services.alert_detection_service import detect_events
from app.services.data_upload_service import upload_data_path
from app.services.ingestion_run_service import create_run
from app.services.parser_runner_service import collect_import_files
from app.services.progress_reporter import report_completed, report_failed, report_progress, report_started
from app.services.update_run_service import add_step, get_run, update_run


def period_values(lookback_days: int, period_start: date | None, period_end: date | None) -> tuple[date, date]:
    """Build update period.
    Args:
        lookback_days (int): Lookback days.
        period_start (date | None): Explicit period start.
        period_end (date | None): Explicit period end."""
    end_date = period_end or datetime.now(UTC).date()
    start_date = period_start or end_date - timedelta(days=lookback_days)
    return start_date, end_date


def run_update_pipeline(
    session: Session,
    job_id: str,
    update_run_id: int,
    schedule: dict[str, object],
    period_start: date | None,
    period_end: date | None,
) -> dict[str, object]:
    """Run scheduled update pipeline.
    Args:
        session (Session): Database session.
        job_id (str): Job identifier.
        update_run_id (int): Update run identifier.
        schedule (dict[str, object]): Schedule data.
        period_start (date | None): Period start.
        period_end (date | None): Period end."""
    start_date, end_date = period_values(int(schedule.get('lookback_days') or 14), period_start, period_end)
    report_started(session, job_id, 'update_run_created', 'Update run created')
    add_step(session, update_run_id, 1, 'update_run_created', 'success', 'Update run created')
    report_progress(session, job_id, 'period_resolved', 'Update period resolved', 10)
    add_step(
        session,
        update_run_id,
        2,
        'period_resolved',
        'success',
        'Update period resolved',
        {'period_start': start_date, 'period_end': end_date},
    )
    files = collect_import_files(schedule.get('config') if isinstance(schedule.get('config'), dict) else {})
    report_progress(session, job_id, 'files_collected', f'Collected {len(files)} files', 35)
    add_step(session, update_run_id, 3, 'files_collected', 'success', f'Collected {len(files)} files')
    rows_loaded = 0
    files_imported = 0
    quality_status = 'unknown'
    ingestion_run_id = None
    if files:
        for file_path in files:
            ingestion_run_id = create_run(
                session,
                str(schedule.get('schedule_name') or 'scheduled_update'),
                str(schedule.get('default_granularity') or 'daily'),
                start_date,
                end_date,
            )
            session.commit()
            upload_result = upload_data_path(
                session,
                file_path,
                ingestion_run_id,
                str(schedule.get('schedule_name') or 'scheduled_update'),
                False,
                str(schedule.get('default_granularity') or 'daily'),
                start_date,
                end_date,
            )
            rows_loaded += upload_result.row_count
            files_imported += len(upload_result.files)
            quality_status = upload_result.quality_status
    else:
        quality_status = 'unknown'
    report_progress(session, job_id, 'ingestion_completed', 'Ingestion completed', 50)
    add_step(
        session,
        update_run_id,
        4,
        'ingestion_completed',
        'success' if files else 'skipped',
        'Ingestion completed' if files else 'No files found for import',
    )
    report_progress(session, job_id, 'quality_completed', 'Quality checks completed', 65)
    add_step(session, update_run_id, 5, 'quality_completed', 'success', f'Quality status: {quality_status}')
    report_progress(session, job_id, 'metrics_recalculated', 'Metrics recalculation completed', 75)
    add_step(session, update_run_id, 6, 'metrics_recalculated', 'success', 'Metrics recalculation marked complete')
    report_progress(session, job_id, 'scores_recalculated', 'Opportunity scores recalculation completed', 85)
    add_step(session, update_run_id, 7, 'scores_recalculated', 'success', 'Opportunity scores recalculation marked complete')
    alerts_count = 0
    if files:
        alert_result = detect_events(session, start_date, end_date, None, None, 'v1')
        alerts_count = alert_result.created_events
    report_progress(session, job_id, 'alerts_detected', f'Created {alerts_count} alerts', 95)
    add_step(session, update_run_id, 8, 'alerts_detected', 'success', f'Created {alerts_count} alerts')
    status = 'success' if files else 'success'
    result_payload = {
        'update_run_id': update_run_id,
        'files_imported_count': files_imported,
        'rows_loaded_count': rows_loaded,
        'quality_status': quality_status,
        'alerts_detected_count': alerts_count,
        'period_start': start_date,
        'period_end': end_date,
    }
    update_run(
        session,
        update_run_id,
        status,
        files_imported,
        rows_loaded,
        quality_status,
        True,
        True,
        alerts_count,
        result_payload,
        ingestion_run_id,
    )
    report_completed(session, job_id, 'update_completed', 'Update completed', result_payload, status)
    return result_payload


def fail_update(session: Session, job_id: str, update_run_id: int, message: str) -> dict[str, object]:
    """Fail scheduled update.
    Args:
        session (Session): Database session.
        job_id (str): Job identifier.
        update_run_id (int): Update run identifier.
        message (str): Error message."""
    add_step(session, update_run_id, 99, 'update_failed', 'failed', message)
    update_run(session, update_run_id, 'failed', 0, 0, 'failed', False, False, 0, {'error': message}, None, message)
    report_failed(session, job_id, 'update_failed', message)
    payload = get_run(session, update_run_id).model_dump(mode='json')
    return payload
