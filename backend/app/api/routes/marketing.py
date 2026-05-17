import pandas as pd
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.schemas.advanced_strategy import (
    AdvancedScoreResponse,
    AdvancedStrategyRequest,
    AdvancedStrategyResponse,
    GrowthScenarioDetail,
    GrowthScenarioList,
)
from app.schemas.marketing import (
    AdCreativeList,
    AdsSummary,
    AudienceFit,
    AudienceSummary,
    BusinessAssumptionCreate,
    BusinessAssumptionItem,
    BusinessAssumptionList,
    BusinessAssumptionUpdate,
    CampaignCreate,
    CampaignItem,
    CampaignList,
    CampaignPerformanceList,
    CpcSummary,
    KeywordList,
    OpportunitySummary,
    ReferringDomainList,
    TopPageList,
)
from app.services.ads_creative_analysis_service import ads_creatives, ads_summary
from app.services.advanced_score_service import calculate_scores, stored_scores
from app.services.advanced_strategy_service import build_strategy, get_scenario, list_scenarios
from app.services.audience_analytics_service import audience_fit, audience_summary
from app.services.backlink_opportunity_service import backlink_opportunity, referring_domains
from app.services.business_impact_service import (
    create_assumption,
    create_campaign,
    list_assumptions,
    list_campaigns,
    list_performance,
    update_assumption,
    upload_performance,
)
from app.services.paid_search_opportunity_service import cpc_summary, paid_keywords, ppc_opportunity
from app.services.permission_service import current_user, require_project_role
from app.services.seo_opportunity_service import organic_keywords, seo_opportunity
from app.services.top_pages_analysis_service import top_pages


router = APIRouter(prefix='/projects/{project_id}', tags=['marketing'])


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


@router.get('/audience/summary', response_model=AudienceSummary)
def get_audience_summary(
    project_id: int,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> AudienceSummary:
    """Get audience summary.
    Args:
        project_id (int): Project identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_view(session, user, project_id)
    response = audience_summary(session, project_id)
    return response


@router.get('/countries/{country_id}/audience-fit', response_model=AudienceFit)
def get_audience_fit(
    project_id: int,
    country_id: int,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> AudienceFit:
    """Get audience fit.
    Args:
        project_id (int): Project identifier.
        country_id (int): Country identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_view(session, user, project_id)
    response = audience_fit(session, project_id, country_id)
    return response


@router.get('/seo/keywords', response_model=KeywordList)
def get_seo_keywords(
    project_id: int,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> KeywordList:
    """Get SEO keywords.
    Args:
        project_id (int): Project identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_view(session, user, project_id)
    response = organic_keywords(session, project_id)
    return response


@router.get('/seo/opportunity', response_model=OpportunitySummary)
def get_seo_opportunity(
    project_id: int,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> OpportunitySummary:
    """Get SEO opportunity.
    Args:
        project_id (int): Project identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_view(session, user, project_id)
    response = seo_opportunity(session, project_id)
    return response


@router.get('/seo/top-pages', response_model=TopPageList)
def get_top_pages(
    project_id: int,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> TopPageList:
    """Get top pages.
    Args:
        project_id (int): Project identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_view(session, user, project_id)
    response = top_pages(session, project_id)
    return response


@router.get('/ppc/keywords', response_model=KeywordList)
def get_ppc_keywords(
    project_id: int,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> KeywordList:
    """Get PPC keywords.
    Args:
        project_id (int): Project identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_view(session, user, project_id)
    response = paid_keywords(session, project_id)
    return response


@router.get('/ppc/opportunity', response_model=OpportunitySummary)
def get_ppc_opportunity(
    project_id: int,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> OpportunitySummary:
    """Get PPC opportunity.
    Args:
        project_id (int): Project identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_view(session, user, project_id)
    response = ppc_opportunity(session, project_id)
    return response


@router.get('/ppc/cpc-summary', response_model=CpcSummary)
def get_cpc_summary(
    project_id: int,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> CpcSummary:
    """Get CPC summary.
    Args:
        project_id (int): Project identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_view(session, user, project_id)
    response = cpc_summary(session, project_id)
    return response


@router.get('/ads/creatives', response_model=AdCreativeList)
def get_ads_creatives(
    project_id: int,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> AdCreativeList:
    """Get ads creatives.
    Args:
        project_id (int): Project identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_view(session, user, project_id)
    response = ads_creatives(session, project_id)
    return response


@router.get('/ads/summary', response_model=AdsSummary)
def get_ads_summary(
    project_id: int,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> AdsSummary:
    """Get ads summary.
    Args:
        project_id (int): Project identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_view(session, user, project_id)
    response = ads_summary(session, project_id)
    return response


@router.get('/backlinks/referring-domains', response_model=ReferringDomainList)
def get_referring_domains(
    project_id: int,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> ReferringDomainList:
    """Get referring domains.
    Args:
        project_id (int): Project identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_view(session, user, project_id)
    response = referring_domains(session, project_id)
    return response


@router.get('/backlinks/opportunity', response_model=OpportunitySummary)
def get_backlink_opportunity(
    project_id: int,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> OpportunitySummary:
    """Get backlink opportunity.
    Args:
        project_id (int): Project identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_view(session, user, project_id)
    response = backlink_opportunity(session, project_id)
    return response


@router.get('/business-assumptions', response_model=BusinessAssumptionList)
def get_business_assumptions(
    project_id: int,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> BusinessAssumptionList:
    """Get assumptions.
    Args:
        project_id (int): Project identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_view(session, user, project_id)
    response = list_assumptions(session, project_id)
    return response


@router.post('/business-assumptions', response_model=BusinessAssumptionItem)
def post_business_assumption(
    project_id: int,
    request: BusinessAssumptionCreate,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> BusinessAssumptionItem:
    """Create assumption.
    Args:
        project_id (int): Project identifier.
        request (BusinessAssumptionCreate): Assumption request.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_edit(session, user, project_id)
    response = create_assumption(session, project_id, request)
    return response


@router.patch('/business-assumptions/{assumption_id}', response_model=BusinessAssumptionItem)
def patch_business_assumption(
    project_id: int,
    assumption_id: int,
    request: BusinessAssumptionUpdate,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> BusinessAssumptionItem:
    """Update assumption.
    Args:
        project_id (int): Project identifier.
        assumption_id (int): Assumption identifier.
        request (BusinessAssumptionUpdate): Assumption update.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_edit(session, user, project_id)
    response = update_assumption(session, project_id, assumption_id, request)
    return response


@router.get('/campaigns', response_model=CampaignList)
def get_campaigns(
    project_id: int,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> CampaignList:
    """Get campaigns.
    Args:
        project_id (int): Project identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_view(session, user, project_id)
    response = list_campaigns(session, project_id)
    return response


@router.post('/campaigns', response_model=CampaignItem)
def post_campaign(
    project_id: int,
    request: CampaignCreate,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> CampaignItem:
    """Create campaign.
    Args:
        project_id (int): Project identifier.
        request (CampaignCreate): Campaign request.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_edit(session, user, project_id)
    response = create_campaign(session, project_id, request)
    return response


@router.get('/campaigns/{campaign_id}/performance', response_model=CampaignPerformanceList)
def get_campaign_performance(
    project_id: int,
    campaign_id: int,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> CampaignPerformanceList:
    """Get campaign performance.
    Args:
        project_id (int): Project identifier.
        campaign_id (int): Campaign identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_view(session, user, project_id)
    response = list_performance(session, project_id, campaign_id)
    return response


@router.post('/campaigns/{campaign_id}/performance/upload', response_model=CampaignPerformanceList)
async def post_campaign_performance(
    project_id: int,
    campaign_id: int,
    file: UploadFile = File(...),
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> CampaignPerformanceList:
    """Upload campaign performance.
    Args:
        project_id (int): Project identifier.
        campaign_id (int): Campaign identifier.
        file (UploadFile): Excel file.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_edit(session, user, project_id)
    data = pd.read_excel(file.file)
    response = upload_performance(session, project_id, campaign_id, data)
    return response


@router.post('/advanced-strategy', response_model=AdvancedStrategyResponse)
def post_advanced_strategy(
    project_id: int,
    request: AdvancedStrategyRequest,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> AdvancedStrategyResponse:
    """Create advanced strategy.
    Args:
        project_id (int): Project identifier.
        request (AdvancedStrategyRequest): Strategy request.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_edit(session, user, project_id)
    response = build_strategy(session, project_id, request)
    return response


@router.get('/advanced-strategy/scenarios', response_model=GrowthScenarioList)
def get_advanced_scenarios(
    project_id: int,
    limit: int = 50,
    offset: int = 0,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> GrowthScenarioList:
    """Get advanced scenarios.
    Args:
        project_id (int): Project identifier.
        limit (int): Result limit.
        offset (int): Result offset.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_view(session, user, project_id)
    response = list_scenarios(session, project_id, limit, offset)
    return response


@router.get('/advanced-strategy/scenarios/{growth_scenario_id}', response_model=GrowthScenarioDetail)
def get_advanced_scenario(
    project_id: int,
    growth_scenario_id: int,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> GrowthScenarioDetail:
    """Get advanced scenario.
    Args:
        project_id (int): Project identifier.
        growth_scenario_id (int): Growth scenario identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_view(session, user, project_id)
    response = get_scenario(session, project_id, growth_scenario_id)
    return response


@router.get('/countries/{country_id}/advanced-scores', response_model=AdvancedScoreResponse | None)
def get_advanced_scores(
    project_id: int,
    country_id: int,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> AdvancedScoreResponse | None:
    """Get advanced scores.
    Args:
        project_id (int): Project identifier.
        country_id (int): Country identifier.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_view(session, user, project_id)
    response = stored_scores(session, project_id, country_id, 'v2')
    return response


@router.post('/countries/{country_id}/advanced-scores/recalculate', response_model=AdvancedScoreResponse)
def post_advanced_scores(
    project_id: int,
    country_id: int,
    request: AdvancedStrategyRequest,
    user: dict[str, object] = Depends(current_user),
    session: Session = Depends(get_session),
) -> AdvancedScoreResponse:
    """Recalculate advanced scores.
    Args:
        project_id (int): Project identifier.
        country_id (int): Country identifier.
        request (AdvancedStrategyRequest): Strategy request.
        user (dict[str, object]): Current user.
        session (Session): Database session."""
    require_edit(session, user, project_id)
    response = calculate_scores(session, project_id, country_id, request.date_from, request.date_to, request.calculation_version)
    return response
