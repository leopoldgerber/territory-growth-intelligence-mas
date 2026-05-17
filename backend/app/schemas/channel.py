from datetime import date

from pydantic import BaseModel


class ChannelScope(BaseModel):
    scope_type: str
    country_id: int | None = None
    country_name_en: str | None = None
    domain_id: int | None = None
    domain: str | None = None
    company_id: int | None = None
    company_name: str | None = None
    is_estimated: bool = False


class ChannelPeriod(BaseModel):
    date_from: date
    date_to: date
    days_count: int


class DominantChannel(BaseModel):
    channel_id: int | None = None
    channel_code: str | None = None
    channel_name: str | None = None
    traffic: float | None = None
    traffic_share: float | None = None


class ChannelMetric(BaseModel):
    channel_id: int
    channel_code: str
    channel_name: str
    traffic: float = 0
    traffic_share: float | None = None
    growth_rate: float | None = None
    stability_score: float | None = None
    is_dominant_channel: bool = False
    dependency_score: float | None = None
    role: str = 'weak'
    interpretation: str


class ChannelSummaryMetrics(BaseModel):
    total_channel_traffic: float = 0
    dominant_channel: DominantChannel | None = None
    channel_dependency_score: float | None = None
    channel_diversification_score: float | None = None
    channel_profile: str = 'mixed'


class ChannelTrendItem(BaseModel):
    date: date
    channel_id: int
    channel_code: str
    channel_name: str
    traffic: float = 0
    traffic_share: float | None = None


class JourneySourceItem(BaseModel):
    journey_source_id: int
    source_name: str | None = None
    source_type: str | None = None
    traffic_type: str | None = None
    channel_id: int | None = None
    channel_code: str | None = None
    channel_name: str | None = None
    traffic: float = 0
    traffic_share: float | None = None
    growth_rate: float | None = None
    stability_score: float | None = None


class ChannelSummaryResponse(BaseModel):
    scope: ChannelScope
    period: ChannelPeriod
    summary: ChannelSummaryMetrics
    channels: list[ChannelMetric]
    warnings: list[str]
    recommendation_hints: list[str]


class ChannelTrendResponse(BaseModel):
    items: list[ChannelTrendItem]


class JourneySourcesResponse(BaseModel):
    items: list[JourneySourceItem]
    warnings: list[str]


class ChannelRecalculateRequest(BaseModel):
    date_from: date
    date_to: date
    country_id: int | None = None
    domain_id: int | None = None
    calculation_version: str = 'v1'


class ChannelRecalculateResponse(BaseModel):
    status: str
    scope_type: str
    metrics_created: int
    journey_source_metrics_created: int
