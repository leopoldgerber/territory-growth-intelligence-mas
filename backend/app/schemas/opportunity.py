from datetime import date

from pydantic import BaseModel

from app.schemas.country import CountryItem, PeriodInfo


class OpportunityScoreValues(BaseModel):
    opportunity_score: float
    recommended_priority: str
    market_type: str


class OpportunityComponents(BaseModel):
    traffic_score: float | None = None
    competition_score: float | None = None
    quality_score: float | None = None
    channel_gap_score: float | None = None
    volatility_score: float | None = None
    localization_potential_score: float | None = None
    entry_difficulty_score: float | None = None


class OpportunityCalculation(BaseModel):
    calculation_version: str
    calculated_at: str | None = None


class OpportunityScoreResponse(BaseModel):
    country: CountryItem
    period: PeriodInfo
    score: OpportunityScoreValues
    components: OpportunityComponents
    strengths: list[str]
    risks: list[str]
    explanation: str
    data_quality_status: str
    calculation: OpportunityCalculation


class OpportunityCountryItem(BaseModel):
    country_id: int
    country_name_en: str
    country_name_ru: str | None = None
    region_name_en: str | None = None
    period_start: date
    period_end: date
    opportunity_score: float
    recommended_priority: str
    market_type: str
    traffic_score: float | None = None
    competition_score: float | None = None
    quality_score: float | None = None
    channel_gap_score: float | None = None
    entry_difficulty_score: float | None = None


class OpportunityCountryList(BaseModel):
    items: list[OpportunityCountryItem]
    total: int


class OpportunityRecalculateRequest(BaseModel):
    date_from: date
    date_to: date
    calculation_version: str = 'v1'


class OpportunityRecalculateResponse(BaseModel):
    country_id: int
    status: str
    opportunity_score: float
    recommended_priority: str
    market_type: str
