# Stage 7 - First Country Report Vertical

Stage 7 adds saved rule-based country reports.

## Database

New table:

- `report_snapshots`

The table stores Markdown, structured JSON, input parameters, data quality status, calculation version, and generator version.

## Backend

New API endpoints:

- `POST /api/reports/country`
- `GET /api/reports/{report_id}`
- `GET /api/reports`
- `DELETE /api/reports/{report_id}`

The report generator combines:

- country summary;
- country metrics;
- top competitors;
- basic channel summary;
- rule-based risks;
- initial recommendations.

Generation is blocked when data quality status is failed.

## Frontend

Country Overview now includes:

- Generate Country Report button;
- Report Viewer;
- Reports History table.

The report viewer displays saved Markdown and data quality status.
