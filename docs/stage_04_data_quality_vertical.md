# Stage 4 - Data Quality Vertical

Stage 4 adds quality checks after data upload and ingestion.

## Backend

New API endpoints:

- `GET /api/data/uploads/{run_id}/quality-checks`
- `POST /api/data/uploads/{run_id}/quality-checks/run`
- `GET /api/data/quality-summary`

## Database

The migration `20260507_0002_add_data_quality_columns.py` adds:

- `ingestion_runs.quality_status`
- `data_quality_checks.severity`
- `data_quality_checks.message`
- `data_quality_checks.affected_rows_count`
- `data_quality_checks.sample_rows`
- `data_quality_checks.quality_dimension`

## Quality Checks

The upload pipeline now runs checks automatically after file ingestion.

Implemented quality dimensions:

- schema;
- types;
- dates;
- references;
- duplicates;
- ranges;
- reconciliation placeholder.

Quality status is calculated separately from ingestion status:

- `passed`
- `warning`
- `failed`

Critical failed checks make the upload unsafe for analytics until the data is fixed.
