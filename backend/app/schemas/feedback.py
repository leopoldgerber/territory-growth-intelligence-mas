from datetime import date, datetime

from pydantic import BaseModel, Field


class RecommendationFeedbackCreate(BaseModel):
    recommendation_id: int | None = None
    agent_run_id: int | None = None
    strategy_id: int | None = None
    growth_scenario_id: int | None = None
    campaign_id: int | None = None
    country_id: int | None = None
    channel_id: int | None = None
    feedback_status: str
    decision_reason: str | None = None
    decision_tags: list[str] = Field(default_factory=list)


class RecommendationFeedbackItem(RecommendationFeedbackCreate):
    feedback_id: int
    project_id: int
    decided_by_user_id: int | None = None
    decided_at: datetime | None = None
    created_at: datetime | None = None


class RecommendationFeedbackList(BaseModel):
    items: list[RecommendationFeedbackItem]
    total: int


class CampaignSnapshotCreate(BaseModel):
    campaign_id: int
    country_id: int | None = None
    channel_id: int | None = None
    period_start: date
    period_end: date
    budget_amount: float | None = None
    actual_spend: float | None = None
    impressions: float | None = None
    clicks: float | None = None
    visits: float | None = None
    leads: float | None = None
    clients: float | None = None
    revenue: float | None = None
    gross_profit: float | None = None
    cac: float | None = None
    cpl: float | None = None
    roas: float | None = None
    roi: float | None = None
    currency_code: str = 'EUR'
    data_quality_status: str = 'passed'
    source_type: str = 'manual'


class CampaignSnapshotItem(CampaignSnapshotCreate):
    campaign_result_snapshot_id: int
    project_id: int
    created_at: datetime | None = None


class CampaignSnapshotList(BaseModel):
    items: list[CampaignSnapshotItem]
    total: int


class ForecastComparisonRequest(BaseModel):
    growth_scenario_id: int | None = None
    campaign_result_snapshot_id: int
    recommendation_id: int | None = None
    strategy_id: int | None = None
    metric_names: list[str] = Field(default_factory=lambda: ['traffic', 'leads', 'clients', 'revenue', 'cac', 'roi'])


class ForecastComparisonItem(BaseModel):
    comparison_id: int
    project_id: int
    country_id: int | None = None
    channel_id: int | None = None
    campaign_id: int | None = None
    recommendation_id: int | None = None
    strategy_id: int | None = None
    growth_scenario_id: int | None = None
    campaign_result_snapshot_id: int
    metric_name: str
    forecast_value: float | None = None
    actual_value: float | None = None
    absolute_error: float | None = None
    relative_error: float | None = None
    accuracy_score: float | None = None
    bias_direction: str
    comparison_details: dict[str, object] | None = None
    created_at: datetime | None = None


class ForecastComparisonList(BaseModel):
    items: list[ForecastComparisonItem]
    total: int


class ScoringWeightVersionItem(BaseModel):
    weight_version_id: int
    model_name: str
    version_name: str
    weights: dict[str, object]
    status: str
    created_from_version_id: int | None = None
    created_by_user_id: int | None = None
    created_at: datetime | None = None
    activated_at: datetime | None = None


class ScoringWeightVersionList(BaseModel):
    items: list[ScoringWeightVersionItem]
    total: int


class ScoringWeightAdjustmentCreate(BaseModel):
    model_name: str = 'advanced_strategy'
    current_weight_version_id: int | None = None
    proposed_version_name: str
    proposed_weights: dict[str, object]
    reason: str | None = None
    evidence: dict[str, object] | None = None
    expected_improvement: float | None = None


class ScoringWeightAdjustmentUpdate(BaseModel):
    status: str


class ScoringWeightAdjustmentItem(ScoringWeightAdjustmentCreate):
    weight_adjustment_id: int
    project_id: int
    status: str
    reviewed_by_user_id: int | None = None
    reviewed_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ScoringWeightAdjustmentList(BaseModel):
    items: list[ScoringWeightAdjustmentItem]
    total: int


class AgentFeedbackCreate(BaseModel):
    agent_run_id: int | None = None
    event_type: str
    rating: float | None = None
    comment: str | None = None
    tags: list[str] = Field(default_factory=list)
    event_payload: dict[str, object] | None = None


class AgentFeedbackItem(AgentFeedbackCreate):
    agent_feedback_event_id: int
    project_id: int
    user_id: int | None = None
    created_at: datetime | None = None


class AgentFeedbackList(BaseModel):
    items: list[AgentFeedbackItem]
    total: int


class ConfidenceResponse(BaseModel):
    project_id: int
    country_id: int | None = None
    channel_id: int | None = None
    confidence_score: float
    components: dict[str, float]


class LearningSummary(BaseModel):
    project_id: int
    recommendation_acceptance_rate: float | None = None
    recommendation_counts: dict[str, int]
    average_forecast_accuracy: float | None = None
    accuracy_by_metric: dict[str, float]
    bias_by_metric: dict[str, dict[str, int]]
    overestimated_signals: list[dict[str, object]]
    underestimated_signals: list[dict[str, object]]
    weight_adjustment_proposals: list[ScoringWeightAdjustmentItem]
