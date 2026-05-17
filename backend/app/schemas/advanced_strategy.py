from datetime import date

from pydantic import BaseModel, Field

from app.schemas.country import CountryItem, PeriodInfo


class AdvancedAssumptions(BaseModel):
    visit_to_lead_rate: float = 0.03
    lead_to_client_rate: float = 0.15
    average_order_value: float = 500
    lifetime_value: float = 2500
    gross_margin: float = 0.65
    target_cac: float = 400
    traffic_capture_rate: float = 0.02


class AdvancedStrategyRequest(BaseModel):
    country_id: int
    date_from: date
    date_to: date
    forecast_start: date | None = None
    forecast_end: date | None = None
    budget_amount: float = Field(gt=0)
    currency_code: str = 'EUR'
    campaign_goal: str = 'growth'
    risk_appetite: str = 'medium'
    scenario_mode: str = 'all'
    assumptions: AdvancedAssumptions | None = None
    calculation_version: str = 'v2'


class AdvancedScoreValues(BaseModel):
    advanced_score_id: int | None = None
    competitor_threat_score: float | None = None
    market_maturity_score: float | None = None
    paid_dependency_score: float | None = None
    seo_opportunity_score: float | None = None
    audience_fit_score: float | None = None
    roi_potential_score: float | None = None
    growth_feasibility_score: float | None = None
    strategic_priority_score: float | None = None


class GrowthScenarioItem(BaseModel):
    growth_scenario_id: int | None = None
    scenario_name: str
    budget_amount: float
    currency_code: str
    expected_traffic_capture: float
    expected_leads: float
    expected_clients: float
    expected_revenue: float
    expected_gross_profit: float
    estimated_cac: float | None = None
    estimated_roi: float | None = None
    payback_period_days: int | None = None
    confidence_score: float


class AdvancedAllocationItem(BaseModel):
    advanced_allocation_id: int | None = None
    growth_scenario_id: int | None = None
    allocation_category: str
    budget_share: float
    budget_amount: float
    expected_traffic: float
    expected_leads: float
    expected_clients: float
    expected_revenue: float
    estimated_cac: float | None = None
    rationale: str
    risk_level: str
    success_metric: str


class SensitivityItem(BaseModel):
    factor_name: str
    base_value: float
    low_value: float
    high_value: float
    low_clients: float
    high_clients: float
    low_roi: float | None = None
    high_roi: float | None = None


class AdvancedStrategyResponse(BaseModel):
    country: CountryItem
    period: PeriodInfo
    forecast_period: dict[str, date | None]
    advanced_scores: AdvancedScoreValues
    recommended_strategy_type: str
    scenarios: list[GrowthScenarioItem]
    recommended_allocation: list[AdvancedAllocationItem]
    sensitivity: list[SensitivityItem]
    recommendations: list[str]
    risks: list[str]
    explanation: str
    assumptions: AdvancedAssumptions
    warnings: list[str]


class GrowthScenarioList(BaseModel):
    items: list[GrowthScenarioItem]
    total: int


class GrowthScenarioDetail(BaseModel):
    scenario: GrowthScenarioItem
    allocation: list[AdvancedAllocationItem]
    assumptions: dict[str, object] | None = None
    scenario_details: dict[str, object] | None = None


class AdvancedScoreResponse(BaseModel):
    project_id: int
    country_id: int
    period: PeriodInfo
    scores: AdvancedScoreValues
    recommended_strategy_type: str
    explanation: str
    score_breakdown: dict[str, object]
