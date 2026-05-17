from datetime import date
from pathlib import Path

from app.db.session import SessionLocal
from app.schemas.alert import AlertDetectRequest
from app.schemas.mas import MASAnalyzeRequest
from app.schemas.report import CountryReportRequest
from app.schemas.workflow import WorkflowRequest
from app.services.scheduled_update_orchestration_service import fail_update, run_update_pipeline
from app.services.alert_detection_service import detect_events
from app.services.data_upload_service import upload_data_path
from app.services.progress_reporter import report_completed, report_failed, report_progress, report_started
from app.services.country_report_service import create_country_report
from app.services.workflow_orchestration_service import run_workflow
from app.worker.celery_app import celery_app
from app.services.update_schedule_service import due_schedules, get_schedule, mark_scheduled
from app.services.update_run_service import create_run as create_update_run
from app.services.update_run_service import link_job
from app.services.job_service import create_job, set_task_id


def date_value(value: str | None) -> date | None:
    """Parse optional date.
    Args:
        value (str | None): Date text."""
    parsed_value = date.fromisoformat(value) if value else None
    return parsed_value


@celery_app.task(name='data_upload_task', bind=True, max_retries=3, default_retry_delay=30)
def data_upload_task(
    self: object,
    job_id: str,
    upload_path: str,
    run_id: int,
    source_name: str,
    is_synthetic: bool,
    granularity: str,
    period_start: str | None,
    period_end: str | None,
) -> dict[str, object]:
    """Run data upload task.
    Args:
        self (object): Celery task instance.
        job_id (str): Job identifier.
        upload_path (str): Upload file path.
        run_id (int): Ingestion run identifier.
        source_name (str): Source name.
        is_synthetic (bool): Synthetic flag.
        granularity (str): Granularity.
        period_start (str | None): Period start.
        period_end (str | None): Period end."""
    session = SessionLocal()
    try:
        report_started(session, job_id, 'upload_started', 'Upload processing started')
        report_progress(session, job_id, 'file_saved', 'File saved and queued', 10)
        result = upload_data_path(
            session,
            Path(upload_path),
            run_id,
            source_name,
            is_synthetic,
            granularity,
            date_value(period_start),
            date_value(period_end),
        )
        status = 'success' if result.status == 'success' else 'partial' if result.status == 'partial' else 'failed'
        payload = result.model_dump(mode='json')
        if status == 'failed':
            report_failed(session, job_id, 'upload_failed', '; '.join(result.errors or ['Upload failed']))
        else:
            report_completed(session, job_id, 'upload_completed', 'Upload completed', payload, status)
        return payload
    except Exception as exc:
        report_failed(session, job_id, 'upload_failed', str(exc))
        raise
    finally:
        session.close()


@celery_app.task(name='workflow_strategy_task', bind=True, max_retries=3, default_retry_delay=30)
def workflow_strategy_task(self: object, job_id: str, payload: dict[str, object]) -> dict[str, object]:
    """Run workflow task.
    Args:
        self (object): Celery task instance.
        job_id (str): Job identifier.
        payload (dict[str, object]): Workflow payload."""
    session = SessionLocal()
    try:
        report_started(session, job_id, 'workflow_started', 'Strategy workflow started')
        report_progress(session, job_id, 'mas_running', 'MAS orchestration is running', 35)
        request = WorkflowRequest(**payload)
        response = run_workflow(session, request)
        report_completed(session, job_id, 'workflow_completed', 'Strategy workflow completed', response.model_dump(mode='json'))
        return response.model_dump(mode='json')
    except Exception as exc:
        report_failed(session, job_id, 'workflow_failed', str(exc))
        raise
    finally:
        session.close()


@celery_app.task(name='alerts_detection_task', bind=True, max_retries=3, default_retry_delay=30)
def alerts_detection_task(self: object, job_id: str, payload: dict[str, object]) -> dict[str, object]:
    """Run alerts detection task.
    Args:
        self (object): Celery task instance.
        job_id (str): Job identifier.
        payload (dict[str, object]): Alert payload."""
    session = SessionLocal()
    try:
        report_started(session, job_id, 'alerts_started', 'Alert detection started')
        request = AlertDetectRequest(**payload)
        response = detect_events(
            session,
            request.date_from,
            request.date_to,
            request.country_id,
            request.domain_id,
            request.calculation_version,
        )
        report_completed(session, job_id, 'alerts_completed', 'Alert detection completed', response.model_dump(mode='json'))
        return response.model_dump(mode='json')
    except Exception as exc:
        report_failed(session, job_id, 'alerts_failed', str(exc))
        raise
    finally:
        session.close()


@celery_app.task(name='mas_analysis_task', bind=True, max_retries=3, default_retry_delay=30)
def mas_analysis_task(self: object, job_id: str, payload: dict[str, object]) -> dict[str, object]:
    """Run MAS task.
    Args:
        self (object): Celery task instance.
        job_id (str): Job identifier.
        payload (dict[str, object]): MAS payload."""
    session = SessionLocal()
    try:
        from app.services.mas_orchestration_service import run_analysis

        report_started(session, job_id, 'mas_started', 'MAS analysis started')
        request = MASAnalyzeRequest(**payload)
        response = run_analysis(session, request)
        report_completed(session, job_id, 'mas_completed', 'MAS analysis completed', response.model_dump(mode='json'))
        return response.model_dump(mode='json')
    except Exception as exc:
        report_failed(session, job_id, 'mas_failed', str(exc))
        raise
    finally:
        session.close()


@celery_app.task(name='report_generation_task', bind=True, max_retries=3, default_retry_delay=30)
def report_generation_task(self: object, job_id: str, payload: dict[str, object]) -> dict[str, object]:
    """Run report generation task.
    Args:
        self (object): Celery task instance.
        job_id (str): Job identifier.
        payload (dict[str, object]): Report payload."""
    session = SessionLocal()
    try:
        report_started(session, job_id, 'report_started', 'Country report generation started')
        request = CountryReportRequest(**payload)
        report_progress(session, job_id, 'report_generating', 'Building country report', 50)
        response = create_country_report(session, request)
        report_completed(session, job_id, 'report_completed', 'Country report generated', response.model_dump(mode='json'))
        return response.model_dump(mode='json')
    except Exception as exc:
        report_failed(session, job_id, 'report_failed', str(exc))
        raise
    finally:
        session.close()


@celery_app.task(name='scheduled_update_task', bind=True, max_retries=3, default_retry_delay=30)
def scheduled_update_task(
    self: object,
    job_id: str,
    update_run_id: int,
    schedule_id: int,
    period_start: str | None,
    period_end: str | None,
) -> dict[str, object]:
    """Run scheduled update task.
    Args:
        self (object): Celery task instance.
        job_id (str): Job identifier.
        update_run_id (int): Update run identifier.
        schedule_id (int): Schedule identifier.
        period_start (str | None): Period start.
        period_end (str | None): Period end."""
    session = SessionLocal()
    try:
        schedule = get_schedule(session, schedule_id).model_dump(mode='json')
        result = run_update_pipeline(
            session,
            job_id,
            update_run_id,
            schedule,
            date_value(period_start),
            date_value(period_end),
        )
        return result
    except Exception as exc:
        return fail_update(session, job_id, update_run_id, str(exc))
    finally:
        session.close()


@celery_app.task(name='scan_update_schedules_task')
def scan_update_schedules_task() -> dict[str, object]:
    """Scan due update schedules.
    Args:
        None (None): No arguments are required."""
    session = SessionLocal()
    queued_count = 0
    try:
        for schedule in due_schedules(session):
            update_run_id = create_update_run(
                session,
                schedule.schedule_id,
                schedule.project_id,
                'scheduled',
                None,
                None,
            )
            payload = {'schedule_id': schedule.schedule_id, 'update_run_id': update_run_id}
            job_id = create_job(
                session,
                'scheduled_update',
                payload,
                schedule.project_id,
                None,
                'update_run',
                update_run_id,
            )
            link_job(session, update_run_id, job_id)
            task = celery_app.send_task('scheduled_update_task', args=[job_id, update_run_id, schedule.schedule_id, None, None])
            set_task_id(session, job_id, str(task.id))
            mark_scheduled(session, schedule.schedule_id, schedule.frequency)
            queued_count += 1
    finally:
        session.close()
    return {'queued_count': queued_count}
