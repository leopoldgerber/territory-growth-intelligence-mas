from datetime import date

from pydantic import BaseModel

from app.schemas.country import CountryItem
from app.schemas.mas import MASEvidenceItem, MASRecommendationItem, MASRunResponse, MASStepItem
from app.schemas.strategy import BudgetAllocationItem


class WorkflowOptions(BaseModel):
    countries: list[CountryItem]
    campaign_goals: list[str]
    risk_appetites: list[str]
    currencies: list[str]
    latest_data_quality_status: str | None = None


class WorkflowRequest(BaseModel):
    project_id: int | None = None
    country_id: int
    date_from: date
    date_to: date
    budget_amount: float | None = None
    currency_code: str = 'EUR'
    campaign_goal: str = 'market_test'
    risk_appetite: str = 'medium'
    user_query: str | None = None
    save_result: bool = True
    calculation_version: str = 'v1'


class WorkflowResponse(BaseModel):
    project_id: int | None = None
    workflow_run_id: int
    agent_run_id: int | None = None
    report_id: int | None = None
    strategy_id: int | None = None
    summary_id: int | None = None
    status: str
    final_answer: str | None = None
    recommendations: list[MASRecommendationItem] = []
    budget_allocation: list[BudgetAllocationItem] = []
    evidence: list[MASEvidenceItem] = []
    steps: list[MASStepItem] = []
    saved: bool = False
    warnings: list[str] = []


class WorkflowRunItem(BaseModel):
    workflow_run_id: int
    project_id: int | None = None
    workflow_type: str
    status: str
    country_id: int | None = None
    country_name_en: str | None = None
    period_start: date | None = None
    period_end: date | None = None
    budget_amount: float | None = None
    currency_code: str | None = None
    campaign_goal: str | None = None
    risk_appetite: str | None = None
    agent_run_id: int | None = None
    report_id: int | None = None
    strategy_id: int | None = None
    summary_id: int | None = None
    final_answer: str | None = None
    error_message: str | None = None
    created_at: str | None = None


class WorkflowRunList(BaseModel):
    items: list[WorkflowRunItem]
    total: int


class WorkflowRunDetail(WorkflowRunItem):
    input_params: dict[str, object] | None = None
    result_payload: dict[str, object] | None = None
    mas_run: MASRunResponse | None = None
