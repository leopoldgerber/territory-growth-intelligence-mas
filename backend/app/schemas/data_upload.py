from pydantic import BaseModel


class UploadFileResult(BaseModel):
    file_id: int | None = None
    file_name: str
    report_type: str
    status: str
    row_count: int = 0
    errors: list[str] = []
    warnings: list[str] = []


class QualitySummary(BaseModel):
    total_checks: int = 0
    passed: int = 0
    warnings: int = 0
    failed: int = 0


class QualityCheck(BaseModel):
    check_id: int
    file_name: str | None = None
    table_name: str | None = None
    check_name: str
    check_type: str | None = None
    status: str | None = None
    severity: str | None = None
    message: str | None = None
    affected_rows_count: int | None = None
    quality_dimension: str | None = None


class QualityResult(BaseModel):
    run_id: int
    quality_status: str
    summary: QualitySummary
    checks: list[QualityCheck] = []


class QualityRunSummary(BaseModel):
    run_id: int
    started_at: str | None = None
    status: str | None = None
    quality_status: str | None = None
    total_checks: int = 0
    failed: int = 0
    warnings: int = 0


class UploadRunResult(BaseModel):
    run_id: int
    status: str
    quality_status: str = 'not_run'
    quality_summary: QualitySummary | None = None
    row_count: int = 0
    files: list[UploadFileResult] = []
    errors: list[str] = []
    warnings: list[str] = []


class UploadRunSummary(BaseModel):
    run_id: int
    source_name: str | None = None
    run_type: str | None = None
    granularity: str | None = None
    status: str | None = None
    quality_status: str | None = None
    row_count: int = 0
    started_at: str | None = None
    finished_at: str | None = None
    error_message: str | None = None


class UploadRunDetail(UploadRunSummary):
    files: list[UploadFileResult] = []
