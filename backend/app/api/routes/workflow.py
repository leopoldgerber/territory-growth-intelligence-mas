from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.job import JobQueuedResponse
from app.schemas.workflow import WorkflowOptions, WorkflowRequest, WorkflowRunDetail, WorkflowRunList
from app.services.country_query_service import latest_quality, list_countries
from app.services.job_service import create_job
from app.services.task_dispatcher import enqueue_task
from app.services.workflow_store_service import get_workflow, list_workflows
from app.services.workflow_validation_service import CAMPAIGN_GOALS, CURRENCIES, RISK_APPETITES


router = APIRouter(prefix='/workflow', tags=['workflow'])


@router.get('/options', response_model=WorkflowOptions)
def get_options(session: Session = Depends(get_session)) -> WorkflowOptions:
    """Get workflow options.
    Args:
        session (Session): Database session."""
    countries = list_countries(session, None, True, 200, 0)
    response = WorkflowOptions(
        countries=countries['items'],
        campaign_goals=CAMPAIGN_GOALS,
        risk_appetites=RISK_APPETITES,
        currencies=CURRENCIES,
        latest_data_quality_status=latest_quality(session) or 'unknown',
    )
    return response


@router.post('/strategy-analysis', response_model=JobQueuedResponse)
def post_strategy_analysis(request: WorkflowRequest, session: Session = Depends(get_session)) -> JobQueuedResponse:
    """Run strategy analysis workflow.
    Args:
        request (WorkflowRequest): Workflow request.
        session (Session): Database session."""
    payload = request.model_dump(mode='json')
    job_id = create_job(session, 'workflow_strategy_analysis', payload, request.project_id, None, 'workflow_run', None)
    enqueue_task(session, job_id, 'workflow_strategy_task', [job_id, payload])
    response = JobQueuedResponse(
        job_id=job_id,
        status='queued',
        message='Strategy workflow job queued',
        related_entity_type='workflow_run',
        related_entity_id=None,
    )
    return response


@router.get('/recent', response_model=WorkflowRunList)
def get_recent_workflows(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_session),
) -> WorkflowRunList:
    """Get recent workflows.
    Args:
        limit (int): Result limit.
        offset (int): Result offset.
        session (Session): Database session."""
    response = list_workflows(session, limit, offset)
    return response


@router.get('/runs/{workflow_run_id}', response_model=WorkflowRunDetail)
def get_workflow_run(workflow_run_id: int, session: Session = Depends(get_session)) -> WorkflowRunDetail:
    """Get workflow run.
    Args:
        workflow_run_id (int): Workflow run identifier.
        session (Session): Database session."""
    response = get_workflow(session, workflow_run_id)
    if response is None:
        raise HTTPException(status_code=404, detail='Workflow run not found.')
    return response
