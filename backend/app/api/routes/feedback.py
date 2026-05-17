from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.feedback import (
    AgentFeedbackCreate,
    AgentFeedbackItem,
    CampaignSnapshotCreate,
    CampaignSnapshotItem,
    CampaignSnapshotList,
    ConfidenceResponse,
    ForecastComparisonList,
    ForecastComparisonRequest,
    LearningSummary,
    RecommendationFeedbackCreate,
    RecommendationFeedbackItem,
    RecommendationFeedbackList,
    ScoringWeightAdjustmentCreate,
    ScoringWeightAdjustmentItem,
    ScoringWeightAdjustmentList,
    ScoringWeightAdjustmentUpdate,
    ScoringWeightVersionList,
)
from app.services.feedback_loop_service import (
    active_weights,
    aggregate_snapshot,
    calibrated_confidence,
    compare_forecast,
    create_adjustment,
    create_agent_event,
    create_feedback,
    create_snapshot,
    learning_summary,
    list_adjustments,
    list_comparisons,
    list_feedback,
    list_snapshots,
    similar_campaigns,
    update_adjustment,
)
from app.services.permission_service import current_user, require_project_role


router = APIRouter(prefix='/projects/{project_id}/feedback', tags=['feedback'])


def user_identifier(user: dict[str, object]) -> int | None:
    """Get user identifier.
    Args:
        user (dict[str, object]): Current user."""
    value = user.get('user_id')
    identifier = int(value) if value is not None else None
    return identifier


def require_view(session: Session, user: dict[str, object], project_id: int) -> str:
    """Require view access.
    Args:
        session (Session): Database session.
        user (dict[str, object]): Current user.
        project_id (int): Project identifier."""
    role = require_project_role(session, user, project_id, ['admin', 'analyst', 'viewer'])
    return role


def require_edit(session: Session, user: dict[str, object], project_id: int) -> str:
    """Require edit access.
    Args:
        session (Session): Database session.
        user (dict[str, object]): Current user.
        project_id (int): Project identifier."""
    role = require_project_role(session, user, project_id, ['admin', 'analyst'])
    return role


def require_admin(session: Session, user: dict[str, object], project_id: int) -> str:
    """Require admin access.
    Args:
        session (Session): Database session.
        user (dict[str, object]): Current user.
        project_id (int): Project identifier."""
    role = require_project_role(session, user, project_id, ['admin'])
    return role


@router.get('/recommendations', response_model=RecommendationFeedbackList)
def get_recommendation_feedback(
    project_id: int,
    limit: int = 50,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> RecommendationFeedbackList:
    """Get recommendation feedback.
    Args:
        project_id (int): Project identifier.
        limit (int): Result limit.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_view(session, user, project_id)
    response = list_feedback(session, project_id, limit)
    return response


@router.post('/recommendations', response_model=RecommendationFeedbackItem)
def post_recommendation_feedback(
    project_id: int,
    request: RecommendationFeedbackCreate,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> RecommendationFeedbackItem:
    """Post recommendation feedback.
    Args:
        project_id (int): Project identifier.
        request (RecommendationFeedbackCreate): Feedback payload.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_edit(session, user, project_id)
    response = create_feedback(session, project_id, request, user_identifier(user))
    return response


@router.get('/campaign-snapshots', response_model=CampaignSnapshotList)
def get_campaign_snapshots(
    project_id: int,
    limit: int = 50,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> CampaignSnapshotList:
    """Get campaign snapshots.
    Args:
        project_id (int): Project identifier.
        limit (int): Result limit.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_view(session, user, project_id)
    response = list_snapshots(session, project_id, limit)
    return response


@router.post('/campaign-snapshots', response_model=CampaignSnapshotItem)
def post_campaign_snapshot(
    project_id: int,
    request: CampaignSnapshotCreate,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> CampaignSnapshotItem:
    """Post campaign snapshot.
    Args:
        project_id (int): Project identifier.
        request (CampaignSnapshotCreate): Snapshot payload.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_edit(session, user, project_id)
    response = create_snapshot(session, project_id, request)
    return response


@router.post('/campaigns/{campaign_id}/aggregate-snapshot', response_model=CampaignSnapshotItem)
def post_aggregate_snapshot(
    project_id: int,
    campaign_id: int,
    period_start: date,
    period_end: date,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> CampaignSnapshotItem:
    """Post aggregate snapshot.
    Args:
        project_id (int): Project identifier.
        campaign_id (int): Campaign identifier.
        period_start (date): Period start.
        period_end (date): Period end.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_edit(session, user, project_id)
    response = aggregate_snapshot(session, project_id, campaign_id, period_start, period_end)
    return response


@router.get('/forecast-comparisons', response_model=ForecastComparisonList)
def get_forecast_comparisons(
    project_id: int,
    limit: int = 100,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> ForecastComparisonList:
    """Get forecast comparisons.
    Args:
        project_id (int): Project identifier.
        limit (int): Result limit.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_view(session, user, project_id)
    response = list_comparisons(session, project_id, limit)
    return response


@router.post('/forecast-comparisons', response_model=ForecastComparisonList)
def post_forecast_comparisons(
    project_id: int,
    request: ForecastComparisonRequest,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> ForecastComparisonList:
    """Post forecast comparisons.
    Args:
        project_id (int): Project identifier.
        request (ForecastComparisonRequest): Comparison payload.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_edit(session, user, project_id)
    response = compare_forecast(session, project_id, request)
    return response


@router.get('/learning-summary', response_model=LearningSummary)
def get_learning_summary(
    project_id: int,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> LearningSummary:
    """Get learning summary.
    Args:
        project_id (int): Project identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_view(session, user, project_id)
    response = learning_summary(session, project_id)
    return response


@router.get('/scoring-weights', response_model=ScoringWeightVersionList)
def get_scoring_weights(
    project_id: int,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> ScoringWeightVersionList:
    """Get scoring weights.
    Args:
        project_id (int): Project identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_view(session, user, project_id)
    response = active_weights(session)
    return response


@router.get('/scoring-adjustments', response_model=ScoringWeightAdjustmentList)
def get_scoring_adjustments(
    project_id: int,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> ScoringWeightAdjustmentList:
    """Get scoring adjustments.
    Args:
        project_id (int): Project identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_view(session, user, project_id)
    response = list_adjustments(session, project_id)
    return response


@router.post('/scoring-adjustments', response_model=ScoringWeightAdjustmentItem)
def post_scoring_adjustment(
    project_id: int,
    request: ScoringWeightAdjustmentCreate,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> ScoringWeightAdjustmentItem:
    """Post scoring adjustment.
    Args:
        project_id (int): Project identifier.
        request (ScoringWeightAdjustmentCreate): Adjustment payload.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_admin(session, user, project_id)
    response = create_adjustment(session, project_id, request)
    return response


@router.patch('/scoring-adjustments/{adjustment_id}', response_model=ScoringWeightAdjustmentItem)
def patch_scoring_adjustment(
    project_id: int,
    adjustment_id: int,
    request: ScoringWeightAdjustmentUpdate,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> ScoringWeightAdjustmentItem:
    """Patch scoring adjustment.
    Args:
        project_id (int): Project identifier.
        adjustment_id (int): Adjustment identifier.
        request (ScoringWeightAdjustmentUpdate): Update payload.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_admin(session, user, project_id)
    response = update_adjustment(session, project_id, adjustment_id, request, user_identifier(user))
    return response


@router.post('/agent-events', response_model=AgentFeedbackItem)
def post_agent_event(
    project_id: int,
    request: AgentFeedbackCreate,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> AgentFeedbackItem:
    """Post agent event.
    Args:
        project_id (int): Project identifier.
        request (AgentFeedbackCreate): Event payload.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_edit(session, user, project_id)
    response = create_agent_event(session, project_id, request, user_identifier(user))
    return response


@router.get('/confidence', response_model=ConfidenceResponse)
def get_confidence_score(
    project_id: int,
    country_id: int | None = None,
    channel_id: int | None = None,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> ConfidenceResponse:
    """Get confidence score.
    Args:
        project_id (int): Project identifier.
        country_id (int | None): Country identifier.
        channel_id (int | None): Channel identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_view(session, user, project_id)
    response = calibrated_confidence(session, project_id, country_id, channel_id)
    return response


@router.get('/similar-campaigns', response_model=CampaignSnapshotList)
def get_similar_campaigns(
    project_id: int,
    country_id: int | None = None,
    channel_id: int | None = None,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> CampaignSnapshotList:
    """Get similar campaigns.
    Args:
        project_id (int): Project identifier.
        country_id (int | None): Country identifier.
        channel_id (int | None): Channel identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_view(session, user, project_id)
    response = similar_campaigns(session, project_id, country_id, channel_id)
    return response
