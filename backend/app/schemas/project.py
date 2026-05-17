from pydantic import BaseModel


class ProjectItem(BaseModel):
    project_id: int
    project_name: str
    project_slug: str
    description: str | None = None
    own_company_id: int | None = None
    default_currency_code: str
    status: str
    role: str | None = None


class ProjectList(BaseModel):
    items: list[ProjectItem]
    total: int


class ProjectCreate(BaseModel):
    project_name: str
    project_slug: str
    description: str | None = None
    own_company_id: int | None = None
    default_currency_code: str = 'EUR'


class ProjectUpdate(BaseModel):
    project_name: str | None = None
    description: str | None = None
    own_company_id: int | None = None
    default_currency_code: str | None = None
    status: str | None = None


class ProjectMemberItem(BaseModel):
    user_id: int
    email: str
    full_name: str | None = None
    role: str
    status: str


class ProjectMemberList(BaseModel):
    items: list[ProjectMemberItem]
    total: int


class ProjectMemberCreate(BaseModel):
    email: str
    role: str = 'viewer'


class ProjectMemberUpdate(BaseModel):
    role: str | None = None
    status: str | None = None


class ProjectCompetitorItem(BaseModel):
    domain_id: int
    domain: str | None = None
    company_id: int | None = None
    company_name: str | None = None
    competitor_tier: str
    priority: str
    notes: str | None = None
    is_active: bool


class ProjectCompetitorList(BaseModel):
    items: list[ProjectCompetitorItem]
    total: int


class ProjectCompetitorCreate(BaseModel):
    domain_id: int
    company_id: int | None = None
    competitor_tier: str = 'unknown'
    priority: str = 'medium'
    notes: str | None = None


class ProjectCountryItem(BaseModel):
    country_id: int
    country_name_en: str | None = None
    country_name_ru: str | None = None
    region_name_en: str | None = None
    status: str
    strategic_priority: str
    notes: str | None = None


class ProjectCountryList(BaseModel):
    items: list[ProjectCountryItem]
    total: int


class ProjectCountryCreate(BaseModel):
    country_id: int
    status: str = 'watchlist'
    strategic_priority: str = 'medium'
    notes: str | None = None


class ProjectCountryUpdate(BaseModel):
    status: str | None = None
    strategic_priority: str | None = None
    notes: str | None = None
