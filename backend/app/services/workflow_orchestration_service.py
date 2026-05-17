from sqlalchemy.orm import Session

from app.schemas.mas import MASAnalyzeRequest
from app.schemas.workflow import WorkflowRequest, WorkflowResponse
from app.services.country_query_service import get_country
from app.services.mas_orchestration_service import run_analysis
from app.services.workflow_result_service import workflow_response
from app.services.workflow_store_service import create_workflow, link_project_results, update_workflow
from app.services.workflow_validation_service import validate_workflow


def query_text(session: Session, request: WorkflowRequest) -> str:
    """Build workflow query.
    Args:
        session (Session): Database session.
        request (WorkflowRequest): Workflow request."""
    if request.user_query:
        return request.user_query
    country = get_country(session, request.country_id) or {}
    country_name = country.get('country_name_en') or 'selected country'
    if request.budget_amount is None:
        return f'Analyze {country_name} and suggest a market entry strategy.'
    return (
        f'Analyze {country_name} and suggest a strategy with budget '
        f'{request.budget_amount} {request.currency_code[:3].upper()}.'
    )


def run_workflow(session: Session, request: WorkflowRequest) -> WorkflowResponse:
    """Run strategy workflow.
    Args:
        session (Session): Database session.
        request (WorkflowRequest): Workflow request."""
    quality_status = validate_workflow(session, request)
    warnings = []
    if quality_status == 'warning':
        warnings.append('Selected data has quality warnings.')
    if quality_status == 'unknown':
        warnings.append('No quality context found for selected workflow scope.')
    workflow_run_id = create_workflow(session, request, quality_status)
    agent_run_id = None
    try:
        mas_request = MASAnalyzeRequest(
            user_query=query_text(session, request),
            country_id=request.country_id,
            date_from=request.date_from,
            date_to=request.date_to,
            budget_amount=request.budget_amount,
            currency_code=request.currency_code[:3].upper(),
            campaign_goal=request.campaign_goal,
            risk_appetite=request.risk_appetite,
            calculation_version=request.calculation_version,
        )
        mas_run = run_analysis(session, mas_request)
        agent_run_id = mas_run.agent_run_id
        status = 'success' if mas_run.run_status == 'completed' else 'partial'
        response = workflow_response(session, workflow_run_id, agent_run_id, status, request.save_result, warnings)
        response.project_id = request.project_id
        link_project_results(
            session,
            request.project_id,
            response.agent_run_id,
            response.report_id,
            response.strategy_id,
            response.summary_id,
        )
        update_workflow(
            session,
            workflow_run_id,
            status,
            response.model_dump(mode='json'),
            response.agent_run_id,
            response.report_id,
            response.strategy_id,
            response.summary_id,
        )
        return response
    except Exception as exc:
        response = workflow_response(session, workflow_run_id, agent_run_id, 'failed', False, warnings)
        response.project_id = request.project_id
        update_workflow(
            session,
            workflow_run_id,
            'failed',
            response.model_dump(mode='json'),
            response.agent_run_id,
            response.report_id,
            response.strategy_id,
            response.summary_id,
            str(exc),
        )
        raise
