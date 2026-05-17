from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.alert import AlertList
from app.schemas.job import JobQueuedResponse
from app.schemas.project import (
    ProjectCompetitorCreate,
    ProjectCompetitorItem,
    ProjectCompetitorList,
    ProjectCountryCreate,
    ProjectCountryItem,
    ProjectCountryList,
    ProjectCountryUpdate,
    ProjectCreate,
    ProjectItem,
    ProjectList,
    ProjectMemberCreate,
    ProjectMemberItem,
    ProjectMemberList,
    ProjectMemberUpdate,
    ProjectUpdate,
)
from app.schemas.report import ReportList
from app.schemas.workflow import WorkflowRequest
from app.services.permission_service import current_user, require_project_role
from app.services.project_service import (
    add_competitor,
    add_member,
    add_target_country,
    create_project,
    get_project,
    list_competitors,
    list_members,
    list_projects,
    list_target_countries,
    remove_competitor,
    update_member,
    update_project,
    update_target_country,
)
from app.services.alert_storage_service import list_events
from app.services.report_storage_service import list_reports
from app.services.job_service import create_job
from app.services.task_dispatcher import enqueue_task


router = APIRouter(prefix='/projects', tags=['projects'])


@router.get('', response_model=ProjectList)
def get_projects(
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> ProjectList:
    """Get projects.
    Args:
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    response = list_projects(session, user)
    return response


@router.post('', response_model=ProjectItem)
def post_project(
    request: ProjectCreate,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> ProjectItem:
    """Create project.
    Args:
        request (ProjectCreate): Project request.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    response = create_project(session, request, user)
    return response


@router.get('/{project_id}', response_model=ProjectItem)
def get_project_by_id(
    project_id: int,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> ProjectItem:
    """Get project by id.
    Args:
        project_id (int): Project identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    response = get_project(session, project_id, user)
    return response


@router.patch('/{project_id}', response_model=ProjectItem)
def patch_project(
    project_id: int,
    request: ProjectUpdate,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> ProjectItem:
    """Update project.
    Args:
        project_id (int): Project identifier.
        request (ProjectUpdate): Project update.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    response = update_project(session, project_id, request, user)
    return response


@router.get('/{project_id}/members', response_model=ProjectMemberList)
def get_project_members(
    project_id: int,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> ProjectMemberList:
    """Get project members.
    Args:
        project_id (int): Project identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    response = list_members(session, project_id, user)
    return response


@router.post('/{project_id}/members', response_model=ProjectMemberItem)
def post_project_member(
    project_id: int,
    request: ProjectMemberCreate,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> ProjectMemberItem:
    """Add project member.
    Args:
        project_id (int): Project identifier.
        request (ProjectMemberCreate): Member request.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    response = add_member(session, project_id, request, user)
    return response


@router.patch('/{project_id}/members/{user_id}', response_model=ProjectMemberItem)
def patch_project_member(
    project_id: int,
    user_id: int,
    request: ProjectMemberUpdate,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> ProjectMemberItem:
    """Update project member.
    Args:
        project_id (int): Project identifier.
        user_id (int): Member user identifier.
        request (ProjectMemberUpdate): Member update.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    response = update_member(session, project_id, user_id, request, user)
    return response


@router.get('/{project_id}/competitors', response_model=ProjectCompetitorList)
def get_project_competitors(
    project_id: int,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> ProjectCompetitorList:
    """Get project competitors.
    Args:
        project_id (int): Project identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    response = list_competitors(session, project_id, user)
    return response


@router.post('/{project_id}/competitors', response_model=ProjectCompetitorItem)
def post_project_competitor(
    project_id: int,
    request: ProjectCompetitorCreate,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> ProjectCompetitorItem:
    """Add project competitor.
    Args:
        project_id (int): Project identifier.
        request (ProjectCompetitorCreate): Competitor request.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    response = add_competitor(session, project_id, request, user)
    return response


@router.delete('/{project_id}/competitors/{domain_id}')
def delete_project_competitor(
    project_id: int,
    domain_id: int,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> dict[str, object]:
    """Delete project competitor.
    Args:
        project_id (int): Project identifier.
        domain_id (int): Domain identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    response = remove_competitor(session, project_id, domain_id, user)
    return response


@router.get('/{project_id}/target-countries', response_model=ProjectCountryList)
def get_project_target_countries(
    project_id: int,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> ProjectCountryList:
    """Get target countries.
    Args:
        project_id (int): Project identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    response = list_target_countries(session, project_id, user)
    return response


@router.post('/{project_id}/target-countries', response_model=ProjectCountryItem)
def post_project_target_country(
    project_id: int,
    request: ProjectCountryCreate,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> ProjectCountryItem:
    """Add target country.
    Args:
        project_id (int): Project identifier.
        request (ProjectCountryCreate): Target country request.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    response = add_target_country(session, project_id, request, user)
    return response


@router.patch('/{project_id}/target-countries/{country_id}', response_model=ProjectCountryItem)
def patch_project_target_country(
    project_id: int,
    country_id: int,
    request: ProjectCountryUpdate,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> ProjectCountryItem:
    """Update target country.
    Args:
        project_id (int): Project identifier.
        country_id (int): Country identifier.
        request (ProjectCountryUpdate): Target country update.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    response = update_target_country(session, project_id, country_id, request, user)
    return response


@router.post('/{project_id}/workflow/strategy-analysis', response_model=JobQueuedResponse)
def post_project_strategy_analysis(
    project_id: int,
    request: WorkflowRequest,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> JobQueuedResponse:
    """Run project workflow.
    Args:
        project_id (int): Project identifier.
        request (WorkflowRequest): Workflow request.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_project_role(session, user, project_id, ['admin', 'analyst'])
    request.project_id = project_id
    payload = request.model_dump(mode='json')
    job_id = create_job(session, 'workflow_strategy_analysis', payload, project_id, int(user['user_id']), 'workflow_run', None)
    enqueue_task(session, job_id, 'workflow_strategy_task', [job_id, payload])
    response = JobQueuedResponse(
        job_id=job_id,
        status='queued',
        message='Strategy workflow job queued',
        related_entity_type='workflow_run',
        related_entity_id=None,
    )
    return response


@router.get('/{project_id}/reports', response_model=ReportList)
def get_project_reports(
    project_id: int,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> ReportList:
    """Get project reports.
    Args:
        project_id (int): Project identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_project_role(session, user, project_id, ['admin', 'analyst', 'viewer'])
    response = list_reports(session, None, None, 50, 0, project_id)
    return response


@router.get('/{project_id}/alerts', response_model=AlertList)
def get_project_alerts(
    project_id: int,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> AlertList:
    """Get project alerts.
    Args:
        project_id (int): Project identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_project_role(session, user, project_id, ['admin', 'analyst', 'viewer'])
    response = list_events(session, {'project_id': project_id}, 50, 0)
    return response
