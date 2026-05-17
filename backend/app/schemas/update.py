from datetime import date

from pydantic import BaseModel


class UpdateScheduleCreate(BaseModel):
    project_id: int | None = None
    schedule_name: str
    source_id: int | None = None
    update_type: str = 'file_import'
    frequency: str = 'weekly'
    cron_expression: str | None = None
    timezone: str = 'UTC'
    is_active: bool = True
    lookback_days: int = 14
    default_granularity: str = 'daily'
    config: dict[str, object] | None = None


class UpdateScheduleUpdate(BaseModel):
    schedule_name: str | None = None
    update_type: str | None = None
    frequency: str | None = None
    cron_expression: str | None = None
    timezone: str | None = None
    is_active: bool | None = None
    lookback_days: int | None = None
    default_granularity: str | None = None
    config: dict[str, object] | None = None


class UpdateScheduleItem(BaseModel):
    schedule_id: int
    project_id: int | None = None
    schedule_name: str
    update_type: str
    frequency: str
    cron_expression: str | None = None
    timezone: str
    is_active: bool
    lookback_days: int
    default_granularity: str
    config: dict[str, object] | None = None
    next_run_at: str | None = None
    last_run_at: str | None = None
    last_run_status: str | None = None
    created_at: str | None = None


class UpdateScheduleList(BaseModel):
    items: list[UpdateScheduleItem]
    total: int


class UpdateRunNowRequest(BaseModel):
    period_start: date | None = None
    period_end: date | None = None
    run_type: str = 'manual'


class UpdateRunQueued(BaseModel):
    update_run_id: int
    job_id: str
    status: str


class UpdateRunItem(BaseModel):
    update_run_id: int
    schedule_id: int | None = None
    project_id: int | None = None
    job_id: str | None = None
    ingestion_run_id: int | None = None
    run_type: str
    status: str
    period_start: date | None = None
    period_end: date | None = None
    started_at: str | None = None
    finished_at: str | None = None
    files_imported_count: int
    rows_loaded_count: int
    quality_status: str
    metrics_recalculated: bool
    scores_recalculated: bool
    alerts_detected_count: int
    error_message: str | None = None
    result_payload: dict[str, object] | None = None
    created_at: str | None = None


class UpdateRunList(BaseModel):
    items: list[UpdateRunItem]
    total: int


class UpdateRunStepItem(BaseModel):
    update_run_step_id: int
    update_run_id: int
    step_order: int
    step_name: str
    step_status: str
    started_at: str | None = None
    finished_at: str | None = None
    message: str | None = None
    details: dict[str, object] | None = None


class UpdateRunStepList(BaseModel):
    items: list[UpdateRunStepItem]
    total: int


class UpdateLatestStatus(BaseModel):
    project_id: int | None = None
    last_successful_update_at: str | None = None
    last_update_status: str | None = None
    latest_data_period: dict[str, date | None]
    quality_status: str
    alerts_detected_count: int
    data_freshness_status: str
