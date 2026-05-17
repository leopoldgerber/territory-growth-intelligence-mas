from datetime import date

from pydantic import BaseModel


class CountryItem(BaseModel):
    country_id: int
    country_name_en: str
    country_name_ru: str | None = None
    region_name_en: str | None = None
    region_name_ru: str | None = None
    has_data: bool = False


class CountryList(BaseModel):
    items: list[CountryItem]
    total: int


class CountryPeriod(BaseModel):
    country_id: int
    date_min: date | None = None
    date_max: date | None = None
    available_days: int = 0


class CountrySummaryMetrics(BaseModel):
    total_competitor_traffic: float = 0
    active_competitors_count: int = 0
    leader_domain: str | None = None
    leader_company: str | None = None
    leader_traffic: float | None = None
    leader_share: float | None = None
    top_3_share: float | None = None
    desktop_traffic: float | None = None
    mobile_traffic: float | None = None
    desktop_share: float | None = None
    mobile_share: float | None = None
    traffic_no_bounce: float | None = None
    traffic_bounce: float | None = None
    no_bounce_share: float | None = None
    bounce_share: float | None = None
    avg_bounce_rate: float | None = None
    avg_pages_per_visit: float | None = None
    avg_visit_duration_seconds: float | None = None


class TopCompetitorItem(BaseModel):
    rank: int
    domain_id: int
    domain: str
    company_id: int | None = None
    company_name: str | None = None
    traffic: float = 0
    traffic_share: float | None = None
    desktop_traffic: float | None = None
    mobile_traffic: float | None = None
    desktop_share: float | None = None
    mobile_share: float | None = None
    bounce_rate: float | None = None
    traffic_no_bounce: float | None = None
    traffic_bounce: float | None = None
    no_bounce_share: float | None = None


class DailyTrendItem(BaseModel):
    date: date
    traffic: float = 0
    desktop_traffic: float | None = None
    mobile_traffic: float | None = None
    traffic_no_bounce: float | None = None
    traffic_bounce: float | None = None


class PeriodInfo(BaseModel):
    date_from: date
    date_to: date
    days_count: int


class CountrySummary(BaseModel):
    country: CountryItem
    period: PeriodInfo
    summary: CountrySummaryMetrics
    top_competitors: list[TopCompetitorItem]
    daily_trend: list[DailyTrendItem]
    generated_summary: str
    quality_warning: str | None = None


class CompetitorList(BaseModel):
    items: list[TopCompetitorItem]
    total: int


class MetricLeader(BaseModel):
    domain_id: int | None = None
    domain: str | None = None
    company_id: int | None = None
    company_name: str | None = None
    traffic: float | None = None
    share: float | None = None


class CountryMetricValues(BaseModel):
    total_competitor_traffic: float | None = None
    active_competitors_count: int | None = None
    leader: MetricLeader | None = None
    leader_share: float | None = None
    top_3_share: float | None = None
    market_concentration_hhi: float | None = None
    desktop_share: float | None = None
    mobile_share: float | None = None
    bounce_share: float | None = None
    no_bounce_share: float | None = None
    avg_bounce_rate: float | None = None
    avg_pages_per_visit: float | None = None
    avg_visit_duration_seconds: float | None = None
    engagement_score: float | None = None
    market_volatility_score: float | None = None


class MetricCalculation(BaseModel):
    calculation_version: str
    calculated_at: str | None = None
    data_quality_status: str | None = None


class CountryMetricsResponse(BaseModel):
    country: CountryItem
    period: PeriodInfo
    metrics: CountryMetricValues
    calculation: MetricCalculation
    warning: str | None = None


class CountryMetricRequest(BaseModel):
    date_from: date
    date_to: date
    calculation_version: str = 'v1'


class MetricRecalculateResponse(BaseModel):
    country_id: int
    period_start: date
    period_end: date
    status: str
    metrics: CountryMetricValues
    warning: str | None = None


class DailyMetricItem(BaseModel):
    date: date
    total_competitor_traffic: float | None = None
    active_competitors_count: int | None = None
    leader_share: float | None = None
    top_3_share: float | None = None
    market_concentration_hhi: float | None = None
    engagement_score: float | None = None
    market_volatility_score: float | None = None


class DailyMetricsResponse(BaseModel):
    country_id: int
    items: list[DailyMetricItem]
