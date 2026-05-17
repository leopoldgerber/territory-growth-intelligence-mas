from datetime import date

from pydantic import BaseModel, Field

from app.schemas.country import CountryItem, PeriodInfo


class BudgetAssumptions(BaseModel):
    traffic_capture_rate: float = 0.02
    visit_to_lead_rate: float = 0.03
    lead_to_client_rate: float = 0.15


class BudgetStrategyRequest(BaseModel):
    country_id: int
    date_from: date
    date_to: date
    budget_amount: float = Field(gt=0)
    currency_code: str = 'EUR'
    campaign_goal: str = 'market_test'
    risk_appetite: str = 'medium'
    assumptions: BudgetAssumptions | None = None
    calculation_version: str = 'v1'


class BudgetInfo(BaseModel):
    amount: float
    currency_code: str


class StrategyInfo(BaseModel):
    recommended_strategy_type: str
    confidence_score: float
    summary: str


class BudgetAllocationItem(BaseModel):
    channel_id: int | None = None
    channel_code: str
    channel_name: str | None = None
    budget_share: float
    budget_amount: float
    priority: str
    risk_level: str
    rationale: str
    expected_traffic: float
    expected_leads: float
    expected_clients: float
    test_hypothesis: str
    success_metric: str


class ExpectedEffect(BaseModel):
    expected_traffic: float
    expected_leads: float
    expected_clients: float


class BudgetStrategyResponse(BaseModel):
    strategy_id: int
    country: CountryItem
    period: PeriodInfo
    budget: BudgetInfo
    strategy: StrategyInfo
    allocation: list[BudgetAllocationItem]
    expected_effect: ExpectedEffect
    risks: list[str]
    recommendations: list[str]
    assumptions: BudgetAssumptions
    data_quality_status: str | None = None


class BudgetStrategyListItem(BaseModel):
    strategy_id: int
    country_id: int
    country_name_en: str
    period_start: date
    period_end: date
    budget_amount: float
    currency_code: str
    campaign_goal: str | None = None
    strategy_status: str | None = None
    recommended_strategy_type: str | None = None
    total_expected_traffic: float | None = None
    confidence_score: float | None = None
    created_at: str | None = None


class BudgetStrategyList(BaseModel):
    items: list[BudgetStrategyListItem]
    total: int
