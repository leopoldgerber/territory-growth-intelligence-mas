from datetime import date

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.data_upload import (
    QualityResult,
    QualityRunSummary,
    UploadRunDetail,
    UploadRunResult,
    UploadRunSummary,
)
from app.schemas.job import JobQueuedResponse
from app.services.ingestion_run_service import create_run
from app.services.job_service import create_job
from app.services.task_dispatcher import enqueue_task
from app.services.data_quality_service import get_quality, run_quality, summary_runs
from app.services.ingestion_run_service import get_run, list_runs
from app.services.source_file_service import list_files
from app.services.upload_service import save_upload, validate_upload


router = APIRouter(prefix='/data', tags=['data'])


@router.post('/upload', response_model=JobQueuedResponse)
def upload_file(
    file: UploadFile = File(...),
    source_name: str = Form('manual_upload'),
    is_synthetic: bool = Form(False),
    granularity: str = Form('daily'),
    period_start: date | None = Form(None),
    period_end: date | None = Form(None),
    session: Session = Depends(get_session),
) -> JobQueuedResponse:
    """Upload data file.
    Args:
        file (UploadFile): Uploaded file.
        source_name (str): Source name.
        is_synthetic (bool): Synthetic data flag.
        granularity (str): Data granularity.
        period_start (date | None): Period start date.
        period_end (date | None): Period end date.
        session (Session): Database session."""
    validation_error = validate_upload(file)
    if validation_error:
        raise HTTPException(status_code=400, detail=[validation_error])
    upload_path = save_upload(file)
    run_id = create_run(session, source_name, granularity, period_start, period_end)
    session.commit()
    payload = {
        'upload_path': str(upload_path),
        'run_id': run_id,
        'source_name': source_name,
        'is_synthetic': is_synthetic,
        'granularity': granularity,
        'period_start': period_start,
        'period_end': period_end,
    }
    job_id = create_job(session, 'data_upload', payload, None, None, 'ingestion_run', run_id)
    enqueue_task(
        session,
        job_id,
        'data_upload_task',
        [job_id, str(upload_path), run_id, source_name, is_synthetic, granularity, str(period_start) if period_start else None, str(period_end) if period_end else None],
    )
    return JobQueuedResponse(
        job_id=job_id,
        status='queued',
        message='Upload job queued',
        related_entity_type='ingestion_run',
        related_entity_id=run_id,
    )


@router.get('/uploads', response_model=list[UploadRunSummary])
def get_uploads(session: Session = Depends(get_session)) -> list[UploadRunSummary]:
    """Get upload runs.
    Args:
        session (Session): Database session."""
    runs = list_runs(session)
    return runs


@router.get('/uploads/{run_id}', response_model=UploadRunDetail)
def get_upload(run_id: int, session: Session = Depends(get_session)) -> UploadRunDetail:
    """Get upload run.
    Args:
        run_id (int): Ingestion run identifier.
        session (Session): Database session."""
    run = get_run(session, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail='Upload run not found.')
    files = list_files(session, run_id)
    run['files'] = files
    return run


@router.get('/uploads/{run_id}/quality-checks', response_model=QualityResult)
def get_quality_checks(run_id: int, session: Session = Depends(get_session)) -> QualityResult:
    """Get quality checks.
    Args:
        run_id (int): Ingestion run identifier.
        session (Session): Database session."""
    run = get_run(session, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail='Upload run not found.')
    result = get_quality(session, run_id)
    return result


@router.post('/uploads/{run_id}/quality-checks/run', response_model=QualityResult)
def run_quality_checks(run_id: int, session: Session = Depends(get_session)) -> QualityResult:
    """Run quality checks.
    Args:
        run_id (int): Ingestion run identifier.
        session (Session): Database session."""
    run = get_run(session, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail='Upload run not found.')
    result = run_quality(session, run_id)
    return result


@router.get('/quality-summary', response_model=list[QualityRunSummary])
def get_quality_summary(session: Session = Depends(get_session)) -> list[QualityRunSummary]:
    """Get quality summary.
    Args:
        session (Session): Database session."""
    rows = summary_runs(session)
    return rows
