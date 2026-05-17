from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.job import JobQueuedResponse
from app.schemas.report import CountryReportRequest, ReportList, ReportResponse
from app.services.country_report_service import create_country_report, response_from_row
from app.services.job_service import create_job
from app.services.report_storage_service import archive_report, get_report, list_reports
from app.services.task_dispatcher import enqueue_task


router = APIRouter(prefix='/reports', tags=['reports'])


@router.post('/country', response_model=JobQueuedResponse)
def create_country(request: CountryReportRequest, session: Session = Depends(get_session)) -> JobQueuedResponse:
    """Create country report.
    Args:
        request (CountryReportRequest): Report request.
        session (Session): Database session."""
    payload = request.model_dump(mode='json')
    job_id = create_job(session, 'report_generation', payload, None, None, 'report', None)
    enqueue_task(session, job_id, 'report_generation_task', [job_id, payload])
    response = JobQueuedResponse(
        job_id=job_id,
        status='queued',
        message='Report generation job queued',
        related_entity_type='report',
        related_entity_id=None,
    )
    return response


@router.get('', response_model=ReportList)
def get_reports(
    report_type: str | None = None,
    country_id: int | None = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
) -> ReportList:
    """Get reports.
    Args:
        report_type (str | None): Report type.
        country_id (int | None): Country identifier.
        limit (int): Result limit.
        offset (int): Result offset.
        session (Session): Database session."""
    reports = list_reports(session, report_type, country_id, limit, offset)
    return reports


@router.get('/{report_id}', response_model=ReportResponse)
def get_report_by_id(report_id: int, session: Session = Depends(get_session)) -> ReportResponse:
    """Get report by id.
    Args:
        report_id (int): Report identifier.
        session (Session): Database session."""
    report = get_report(session, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail='Report not found.')
    response = response_from_row(report)
    return response


@router.delete('/{report_id}')
def delete_report(report_id: int, session: Session = Depends(get_session)) -> dict[str, object]:
    """Delete report.
    Args:
        report_id (int): Report identifier.
        session (Session): Database session."""
    report = get_report(session, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail='Report not found.')
    archive_report(session, report_id)
    return {'report_id': report_id, 'status': 'archived'}
