from datetime import date

from pydantic import BaseModel


class CompetitorItem(BaseModel):
    domain_id: int
    domain: str
    company_id: int | None = None
    company_name: str | None = None
    has_data: bool = False


class CompetitorList(BaseModel):
    items: list[CompetitorItem]
    total: int


class CompetitorPeriod(BaseModel):
    domain_id: int
    domain: str
    date_min: date | None = None
    date_max: date | None = None
    available_days: int = 0


class CompetitorSummaryMetrics(BaseModel):
    total_traffic: float = 0
    active_countries_count: int = 0
    top_country: str | None = None
    top_country_traffic: float | None = None
    top_country_share: float | None = None
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


class CompetitorCountryItem(BaseModel):
    rank: int
    country_id: int
    country_name_en: str
    country_name_ru: str | None = None
    region_name_en: str | None = None
    traffic: float = 0
    traffic_share_in_domain: float | None = None
    growth_rate: float | None = None
    presence_stability_score: float | None = None
    desktop_share: float | None = None
    mobile_share: float | None = None
    bounce_rate: float | None = None
    no_bounce_share: float | None = None
    country_role: str = 'normal'
    quality_label: str = 'medium'
    signal: str | None = None


class CompetitorSignalSet(BaseModel):
    anchor_countries: list[CompetitorCountryItem] = []
    peripheral_countries: list[CompetitorCountryItem] = []
    growing_countries: list[CompetitorCountryItem] = []
    declining_countries: list[CompetitorCountryItem] = []
    new_market_signals: list[CompetitorCountryItem] = []
    abandoned_market_signals: list[CompetitorCountryItem] = []


class CompetitorDailyTrend(BaseModel):
    date: date
    traffic: float = 0
    desktop_traffic: float | None = None
    mobile_traffic: float | None = None
    traffic_no_bounce: float | None = None
    traffic_bounce: float | None = None


class CompetitorSummary(BaseModel):
    competitor: CompetitorItem
    period: dict[str, object]
    summary: CompetitorSummaryMetrics
    top_countries: list[CompetitorCountryItem]
    signals: CompetitorSignalSet
    daily_trend: list[CompetitorDailyTrend]
    generated_summary: str
    quality_warning: str | None = None


class CompetitorCountriesResponse(BaseModel):
    items: list[CompetitorCountryItem]
    total: int
