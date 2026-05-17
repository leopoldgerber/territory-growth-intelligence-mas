from datetime import date

from pydantic import BaseModel


class DataWarning(BaseModel):
    source_name: str
    status: str
    message: str


class AudienceSegmentItem(BaseModel):
    segment_type: str
    segment_name: str
    segment_value: str | None = None
    traffic: float
    traffic_share: float | None = None


class AudienceSummary(BaseModel):
    project_id: int
    total_traffic: float
    audience_fit_score: float | None = None
    segments: list[AudienceSegmentItem]
    warnings: list[DataWarning]


class AudienceFit(BaseModel):
    project_id: int
    country_id: int
    audience_fit_score: float | None = None
    traffic: float
    top_segments: list[AudienceSegmentItem]
    warnings: list[DataWarning]


class KeywordItem(BaseModel):
    keyword_id: int
    keyword_text: str
    country_id: int | None = None
    country_name_en: str | None = None
    domain: str | None = None
    position: float | None = None
    search_volume: float | None = None
    estimated_traffic: float | None = None
    traffic_share: float | None = None
    keyword_difficulty: float | None = None
    cpc: float | None = None
    estimated_cost: float | None = None
    competition: float | None = None
    currency_code: str | None = None


class KeywordList(BaseModel):
    items: list[KeywordItem]
    total: int
    warnings: list[DataWarning]


class OpportunitySummary(BaseModel):
    project_id: int
    opportunity_score: float | None = None
    demand: float
    difficulty: float | None = None
    estimated_cost: float | None = None
    recommendation: str
    warnings: list[DataWarning]


class TopPageItem(BaseModel):
    page_id: int
    url: str
    page_type: str
    domain: str | None = None
    country_id: int | None = None
    estimated_traffic: float | None = None
    organic_traffic: float | None = None
    paid_traffic: float | None = None
    keywords_count: int | None = None
    backlinks_count: int | None = None


class TopPageList(BaseModel):
    items: list[TopPageItem]
    total: int
    warnings: list[DataWarning]


class CpcSummary(BaseModel):
    project_id: int
    average_cpc: float | None = None
    min_cpc: float | None = None
    max_cpc: float | None = None
    total_estimated_cost: float
    currency_codes: list[str]
    warnings: list[DataWarning]


class AdCreativeItem(BaseModel):
    creative_hash: str
    domain: str | None = None
    country_id: int | None = None
    headline: str | None = None
    description: str | None = None
    cta: str | None = None
    ad_network: str | None = None
    estimated_spend: float | None = None
    estimated_traffic: float | None = None
    first_seen_date: date | None = None
    last_seen_date: date | None = None


class AdCreativeList(BaseModel):
    items: list[AdCreativeItem]
    total: int
    warnings: list[DataWarning]


class AdsSummary(BaseModel):
    project_id: int
    creatives_count: int
    estimated_spend: float
    estimated_traffic: float
    top_ctas: list[dict[str, object]]
    warnings: list[DataWarning]


class ReferringDomainItem(BaseModel):
    referring_domain: str
    domain: str | None = None
    country_id: int | None = None
    source_url: str | None = None
    target_url: str | None = None
    backlinks_count: int | None = None
    authority_score: float | None = None
    estimated_referral_traffic: float | None = None


class ReferringDomainList(BaseModel):
    items: list[ReferringDomainItem]
    total: int
    warnings: list[DataWarning]


class BusinessAssumptionItem(BaseModel):
    assumption_id: int
    project_id: int
    country_id: int | None = None
    currency_code: str
    visit_to_lead_rate: float | None = None
    lead_to_client_rate: float | None = None
    average_order_value: float | None = None
    ltv: float | None = None
    gross_margin: float | None = None
    target_cac: float | None = None
    monthly_budget: float | None = None
    confidence_score: float | None = None
    valid_from: date | None = None
    valid_to: date | None = None
    notes: str | None = None


class BusinessAssumptionList(BaseModel):
    items: list[BusinessAssumptionItem]
    total: int


class BusinessAssumptionCreate(BaseModel):
    country_id: int | None = None
    currency_code: str = 'EUR'
    visit_to_lead_rate: float | None = None
    lead_to_client_rate: float | None = None
    average_order_value: float | None = None
    ltv: float | None = None
    gross_margin: float | None = None
    target_cac: float | None = None
    monthly_budget: float | None = None
    confidence_score: float | None = None
    valid_from: date | None = None
    valid_to: date | None = None
    notes: str | None = None


class BusinessAssumptionUpdate(BaseModel):
    country_id: int | None = None
    currency_code: str | None = None
    visit_to_lead_rate: float | None = None
    lead_to_client_rate: float | None = None
    average_order_value: float | None = None
    ltv: float | None = None
    gross_margin: float | None = None
    target_cac: float | None = None
    monthly_budget: float | None = None
    confidence_score: float | None = None
    valid_from: date | None = None
    valid_to: date | None = None
    notes: str | None = None


class CampaignItem(BaseModel):
    campaign_id: int
    project_id: int
    campaign_name: str
    channel_code: str | None = None
    country_id: int | None = None
    status: str
    currency_code: str
    start_date: date | None = None
    end_date: date | None = None
    notes: str | None = None


class CampaignList(BaseModel):
    items: list[CampaignItem]
    total: int


class CampaignCreate(BaseModel):
    campaign_name: str
    channel_code: str | None = None
    country_id: int | None = None
    status: str = 'active'
    currency_code: str = 'EUR'
    start_date: date | None = None
    end_date: date | None = None
    notes: str | None = None


class CampaignPerformanceItem(BaseModel):
    campaign_performance_id: int
    campaign_id: int
    date: date
    impressions: float | None = None
    clicks: float | None = None
    visits: float | None = None
    spend: float | None = None
    leads: float | None = None
    clients: float | None = None
    revenue: float | None = None
    cac: float | None = None
    roas: float | None = None
    roi: float | None = None


class CampaignPerformanceList(BaseModel):
    items: list[CampaignPerformanceItem]
    total: int
    summary: dict[str, float | None]
