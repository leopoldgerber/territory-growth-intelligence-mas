from datetime import date

from pydantic import BaseModel


class MASAnalyzeRequest(BaseModel):
    user_query: str
    country_id: int | None = None
    date_from: date | None = None
    date_to: date | None = None
    budget_amount: float | None = None
    currency_code: str = 'EUR'
    campaign_goal: str = 'market_test'
    risk_appetite: str = 'medium'
    calculation_version: str = 'v1'


class MASStepItem(BaseModel):
    agent_step_id: int
    step_order: int
    agent_name: str
    step_type: str | None = None
    step_status: str | None = None
    summary: str | None = None


class MASEvidenceItem(BaseModel):
    evidence_id: int
    evidence_type: str | None = None
    source_name: str | None = None
    source_ref: str | None = None
    metric_name: str | None = None
    metric_value: float | None = None


class MASInsightItem(BaseModel):
    insight_id: int
    agent_name: str | None = None
    insight_type: str | None = None
    title: str
    summary: str | None = None
    severity: str | None = None
    confidence_score: float | None = None


class MASRecommendationItem(BaseModel):
    recommendation_id: int
    recommendation_type: str | None = None
    priority: str | None = None
    title: str
    description: str | None = None
    rationale: str | None = None
    expected_impact: str | None = None
    confidence_score: float | None = None


class MASRunResponse(BaseModel):
    agent_run_id: int
    user_query: str
    run_status: str | None = None
    run_type: str | None = None
    country_id: int | None = None
    period_start: date | None = None
    period_end: date | None = None
    budget_amount: float | None = None
    currency_code: str | None = None
    campaign_goal: str | None = None
    final_answer: str | None = None
    confidence_score: float | None = None
    steps: list[MASStepItem] = []
    evidence: list[MASEvidenceItem] = []
    insights: list[MASInsightItem] = []
    recommendations: list[MASRecommendationItem] = []


class MASRunListItem(BaseModel):
    agent_run_id: int
    user_query: str
    run_status: str | None = None
    run_type: str | None = None
    country_id: int | None = None
    period_start: date | None = None
    period_end: date | None = None
    confidence_score: float | None = None
    created_at: str | None = None


class MASRunList(BaseModel):
    items: list[MASRunListItem]
    total: int
