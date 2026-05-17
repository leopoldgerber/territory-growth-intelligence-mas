from datetime import date

from pydantic import BaseModel


class HistoryReportItem(BaseModel):
    report_id: int
    report_type: str
    title: str
    country_id: int | None = None
    country_name_en: str | None = None
    period_start: date | None = None
    period_end: date | None = None
    data_quality_status: str | None = None
    report_status: str | None = None
    created_at: str | None = None


class HistoryReportList(BaseModel):
    items: list[HistoryReportItem]
    total: int


class HistoryAgentRunItem(BaseModel):
    agent_run_id: int
    run_type: str | None = None
    user_query: str
    country_id: int | None = None
    country_name_en: str | None = None
    period_start: date | None = None
    period_end: date | None = None
    budget_amount: float | None = None
    currency_code: str | None = None
    run_status: str | None = None
    confidence_score: float | None = None
    created_at: str | None = None


class HistoryAgentRunList(BaseModel):
    items: list[HistoryAgentRunItem]
    total: int


class HistoryInsightItem(BaseModel):
    insight_id: int
    agent_run_id: int
    insight_type: str | None = None
    title: str
    summary: str | None = None
    country_id: int | None = None
    country_name_en: str | None = None
    severity: str | None = None
    confidence_score: float | None = None
    created_at: str | None = None


class HistoryInsightList(BaseModel):
    items: list[HistoryInsightItem]
    total: int


class HistoryRecommendationItem(BaseModel):
    recommendation_id: int
    agent_run_id: int
    recommendation_type: str | None = None
    priority: str | None = None
    title: str
    description: str | None = None
    country_id: int | None = None
    country_name_en: str | None = None
    expected_impact: str | None = None
    confidence_score: float | None = None
    created_at: str | None = None


class HistoryRecommendationList(BaseModel):
    items: list[HistoryRecommendationItem]
    total: int


class SavedSummaryCreate(BaseModel):
    summary_type: str
    title: str
    summary_text: str
    summary_json: dict[str, object] | None = None
    country_id: int | None = None
    domain_id: int | None = None
    channel_id: int | None = None
    period_start: date | None = None
    period_end: date | None = None
    source_type: str = 'manual'
    source_id: int = 0
    tags: list[str] = []
    importance_score: float | None = None
    confidence_score: float | None = None
    data_quality_status: str = 'unknown'
    rag_ready: bool = False
    embedding_status: str = 'not_started'


class SavedSummaryUpdate(BaseModel):
    title: str | None = None
    summary_text: str | None = None
    summary_json: dict[str, object] | None = None
    tags: list[str] | None = None
    importance_score: float | None = None
    confidence_score: float | None = None
    data_quality_status: str | None = None
    rag_ready: bool | None = None
    embedding_status: str | None = None


class SavedSummaryItem(BaseModel):
    summary_id: int
    summary_type: str
    title: str
    summary_text: str
    summary_json: dict[str, object] | None = None
    country_id: int | None = None
    country_name_en: str | None = None
    domain_id: int | None = None
    domain: str | None = None
    channel_id: int | None = None
    channel_name: str | None = None
    period_start: date | None = None
    period_end: date | None = None
    source_type: str
    source_id: int
    tags: list[str] = []
    importance_score: float | None = None
    confidence_score: float | None = None
    data_quality_status: str | None = None
    rag_ready: bool
    embedding_status: str
    created_at: str | None = None
    updated_at: str | None = None


class SavedSummaryList(BaseModel):
    items: list[SavedSummaryItem]
    total: int
