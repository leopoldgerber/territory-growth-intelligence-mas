from datetime import date

from pydantic import BaseModel


class AlertCountry(BaseModel):
    country_id: int | None = None
    country_name_en: str | None = None
    country_name_ru: str | None = None


class AlertCompetitor(BaseModel):
    domain_id: int | None = None
    domain: str | None = None
    company_id: int | None = None
    company_name: str | None = None


class AlertChannel(BaseModel):
    channel_id: int | None = None
    channel_code: str | None = None
    channel_name: str | None = None


class AlertItem(BaseModel):
    anomaly_id: int
    event_type: str
    event_category: str | None = None
    event_date: date
    severity: str | None = None
    status: str
    country: AlertCountry | None = None
    competitor: AlertCompetitor | None = None
    channel: AlertChannel | None = None
    title: str
    description: str | None = None
    recommendation_hint: str | None = None
    relative_change: float | None = None
    created_at: str | None = None


class AlertDetail(AlertItem):
    metric_name: str | None = None
    previous_value: float | None = None
    current_value: float | None = None
    absolute_change: float | None = None
    baseline_value: float | None = None
    threshold_value: float | None = None
    evidence: dict[str, object] | None = None
    calculation_version: str | None = None
    data_quality_status: str | None = None
    detected_at: str | None = None
    updated_at: str | None = None


class AlertList(BaseModel):
    items: list[AlertItem]
    total: int


class AlertDetectRequest(BaseModel):
    date_from: date
    date_to: date
    country_id: int | None = None
    domain_id: int | None = None
    calculation_version: str = 'v1'


class AlertDetectResponse(BaseModel):
    status: str
    detected_events: int
    created_events: int
    duplicates_skipped: int


class AlertStatusRequest(BaseModel):
    status: str


class AlertSummary(BaseModel):
    total_new: int
    critical: int
    high: int
    medium: int
    by_category: dict[str, int]
