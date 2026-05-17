from datetime import date

from pydantic import BaseModel

from app.schemas.country import CountryItem, PeriodInfo


class CountryReportRequest(BaseModel):
    country_id: int
    date_from: date
    date_to: date
    limit_competitors: int = 10
    include_channels: bool = True
    include_recommendations: bool = True
    calculation_version: str = 'v1'


class ReportResponse(BaseModel):
    report_id: int
    report_type: str
    status: str
    title: str
    country: CountryItem | None = None
    period: PeriodInfo | None = None
    data_quality_status: str | None = None
    report_markdown: str | None = None
    report_json: dict[str, object] | None = None
    created_at: str | None = None


class ReportListItem(BaseModel):
    report_id: int
    project_id: int | None = None
    report_type: str
    title: str
    report_status: str | None = None
    country_name_en: str | None = None
    period_start: date
    period_end: date
    data_quality_status: str | None = None
    created_at: str | None = None


class ReportList(BaseModel):
    items: list[ReportListItem]
    total: int
