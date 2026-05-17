from pydantic import BaseModel


class JobQueuedResponse(BaseModel):
    job_id: str
    status: str
    message: str
    related_entity_type: str | None = None
    related_entity_id: int | None = None


class JobItem(BaseModel):
    job_id: str
    job_type: str
    status: str
    project_id: int | None = None
    user_id: int | None = None
    related_entity_type: str | None = None
    related_entity_id: int | None = None
    progress_percent: float
    current_step: str | None = None
    result_payload: dict[str, object] | None = None
    error_message: str | None = None
    celery_task_id: str | None = None
    created_at: str | None = None
    started_at: str | None = None
    finished_at: str | None = None
    updated_at: str | None = None


class JobList(BaseModel):
    items: list[JobItem]
    total: int


class JobEventItem(BaseModel):
    event_id: int
    job_id: str
    event_type: str
    step_name: str | None = None
    message: str | None = None
    progress_percent: float | None = None
    event_payload: dict[str, object] | None = None
    created_at: str | None = None


class JobEventList(BaseModel):
    items: list[JobEventItem]
    total: int
