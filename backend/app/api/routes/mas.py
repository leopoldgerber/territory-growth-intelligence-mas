from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.job import JobQueuedResponse
from app.schemas.mas import MASAnalyzeRequest, MASEvidenceItem, MASRunList, MASRunResponse, MASStepItem
from app.services.job_service import create_job
from app.services.mas_store_service import evidence_items, get_run, list_runs, step_items
from app.services.task_dispatcher import enqueue_task


router = APIRouter(prefix='/mas', tags=['mas'])


@router.post('/analyze', response_model=JobQueuedResponse)
def analyze_market(request: MASAnalyzeRequest, session: Session = Depends(get_session)) -> JobQueuedResponse:
    """Analyze market.
    Args:
        request (MASAnalyzeRequest): MAS analyze request.
        session (Session): Database session."""
    payload = request.model_dump(mode='json')
    job_id = create_job(session, 'mas_analysis', payload, None, None, 'agent_run', None)
    enqueue_task(session, job_id, 'mas_analysis_task', [job_id, payload])
    response = JobQueuedResponse(
        job_id=job_id,
        status='queued',
        message='MAS analysis job queued',
        related_entity_type='agent_run',
        related_entity_id=None,
    )
    return response


@router.get('/runs', response_model=MASRunList)
def get_runs(
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: Session = Depends(get_session),
) -> MASRunList:
    """Get MAS runs.
    Args:
        limit (int): Result limit.
        offset (int): Result offset.
        session (Session): Database session."""
    result = list_runs(session, limit, offset)
    response = MASRunList(**result)
    return response


@router.get('/runs/{agent_run_id}', response_model=MASRunResponse)
def get_run_detail(agent_run_id: int, session: Session = Depends(get_session)) -> MASRunResponse:
    """Get MAS run detail.
    Args:
        agent_run_id (int): Agent run identifier.
        session (Session): Database session."""
    response = get_run(session, agent_run_id)
    if response is None:
        raise HTTPException(status_code=404, detail='MAS run not found.')
    return response


@router.get('/runs/{agent_run_id}/steps', response_model=list[MASStepItem])
def get_run_steps(agent_run_id: int, session: Session = Depends(get_session)) -> list[MASStepItem]:
    """Get MAS run steps.
    Args:
        agent_run_id (int): Agent run identifier.
        session (Session): Database session."""
    items = step_items(session, agent_run_id)
    return items


@router.get('/runs/{agent_run_id}/evidence', response_model=list[MASEvidenceItem])
def get_run_evidence(agent_run_id: int, session: Session = Depends(get_session)) -> list[MASEvidenceItem]:
    """Get MAS run evidence.
    Args:
        agent_run_id (int): Agent run identifier.
        session (Session): Database session."""
    items = evidence_items(session, agent_run_id)
    return items
