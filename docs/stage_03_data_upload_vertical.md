# Stage 3 - Data Upload Vertical

Stage 3 adds the first end-to-end data ingestion path for parser output files.

## Backend

New API endpoints:

- `POST /api/data/upload`
- `GET /api/data/uploads`
- `GET /api/data/uploads/{run_id}`

The upload endpoint accepts `.xlsx` and `.zip` files through multipart form data.

Supported form fields:

- `file`
- `source_name`
- `is_synthetic`
- `granularity`
- `period_start`
- `period_end`

## Supported Files

- `traffic_countries_daily.xlsx`
- `trend_by_devices_daily.xlsx`
- `traffic_sources_daily.xlsx`
- `journey_sources_daily.xlsx`
- `calendar_daily.xlsx`
- `domains_list.xlsx`
- `company_list.xlsx`
- `countries_en_list.xlsx`
- `countries_ru_list.xlsx`
- `countries_location_ru_list.xlsx`

## Flow

1. Store uploaded file.
2. Extract ZIP archives safely.
3. Detect report type by filename.
4. Register `ingestion_runs` and `source_files`.
5. Validate readable Excel files and required columns.
6. Upsert dimension rows.
7. Append fact rows with `source_file_id` and `run_id`.
8. Return success, partial, or failed result.
9. Run data quality checks and return quality status.

## Frontend

The React app now includes:

- upload dropzone;
- upload options form;
- result summary;
- processed files table;
- validation messages;
- recent upload history.
