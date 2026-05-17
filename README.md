# Territory Growth Intelligence MAS

Stage 22 adds the production-readiness baseline: testing scaffolding, CI, production Docker compose, Nginx reverse proxy, structured logging, health/readiness/metrics endpoints, backup script, and operational docs.

Stage 1 adds the base web application scaffold: FastAPI backend, React frontend, and PostgreSQL through Docker Compose.
Stage 3 adds the first data upload vertical for parser output files.
Stage 4 adds data quality checks after upload.
Stage 5 adds country-level market summary analytics.
Stage 6 persists reusable country metrics.
Stage 7 adds saved rule-based country reports.
Stage 8 adds competitor analysis by country.
Stage 9 adds channel intelligence and journey source analysis.
Stage 10 adds country opportunity scoring.
Stage 11 adds budget strategy generation.
Stage 12 adds synchronous rule-based MAS orchestration.
Stage 13 adds saved insights, summaries, reports, and RAG-ready metadata.

Existing report parser implementations stay in:

- `parse_reports_modules/`
- `parse_reports_agents/`

The web application scaffold is separate from parser implementations and now includes upload, quality, country, report, competitor, opportunity, budget, MAS orchestration, and knowledge history flows.

## Structure

- `backend/` FastAPI API with health, upload, quality, country, report, competitor, opportunity, budget, MAS, and history endpoints.
- `frontend/` React TypeScript UI with system status, strategy assistant, knowledge history, country overview, competitor overview, reports, and data upload screens.
- `docs/` stage documentation.
- `docker-compose.yml` local backend, frontend, and PostgreSQL startup.

## Local Run

```bash
make setup
make up-build
make migrate
```

The backend container applies Alembic migrations automatically before starting FastAPI.

Open:

- Frontend: http://localhost:5173
- Backend docs: http://localhost:8000/docs
- Healthcheck: http://localhost:8000/api/health
- Readiness: http://localhost:8000/api/health/ready
- Liveness: http://localhost:8000/api/health/live
- Metrics: http://localhost:8000/api/health/metrics
- PostgreSQL: localhost:5432

## Health Response

Expected healthy response:

```json
{
  "status": "ok",
  "backend": "ok",
  "database": "ok",
  "app_name": "Territory Growth Intelligence MAS",
  "environment": "local"
}
```

If PostgreSQL is unavailable, backend stays up and reports `status: degraded`.

## Production Baseline

Production compose:

```bash
make prod-up-build
```

The production baseline includes:

- `docker-compose.prod.yml`
- `backend/Dockerfile.prod`
- `frontend/Dockerfile.prod`
- `infra/nginx/default.conf`
- `.github/workflows/ci.yml`
- `scripts/backup_postgres.ps1`

## Testing

Backend:

```bash
make test-backend
```

Frontend after installing dependencies:

```bash
cd frontend
npm install
npm run typecheck
npm run test
```

## Database Migrations

Stage 2 adds Alembic and the first production schema.

Apply migrations manually when containers are running:

```bash
make migrate
```

Inspect migration state:

```bash
make migrate-current
make migrate-history
```

The initial migration creates:

- ingestion/audit tables: `data_sources`, `ingestion_runs`, `source_files`, `data_quality_checks`;
- dimensions: `dim_date`, `dim_company`, `dim_domain`, `dim_region`, `dim_country`, `dim_channel`, `dim_journey_source`;
- daily facts: `fact_domain_country_daily`, `fact_domain_device_daily`, `fact_domain_channel_daily`, `fact_domain_journey_source_daily`.

Seed data includes traffic channels, data sources, and `dim_date` calendar rows for `2020-01-01` through `2030-12-31`.

## Data Upload

Stage 3 accepts parser outputs as `.xlsx` files or `.zip` archives.

API endpoints:

- `POST /api/data/upload`
- `GET /api/data/uploads`
- `GET /api/data/uploads/{run_id}`
- `GET /api/data/uploads/{run_id}/quality-checks`
- `POST /api/data/uploads/{run_id}/quality-checks/run`
- `GET /api/data/quality-summary`
- `GET /api/countries`
- `GET /api/countries/{country_id}/available-period`
- `GET /api/countries/{country_id}/summary`
- `GET /api/countries/{country_id}/competitors`
- `POST /api/countries/{country_id}/metrics/recalculate`
- `GET /api/countries/{country_id}/metrics`
- `GET /api/countries/{country_id}/metrics/daily`
- `POST /api/reports/country`
- `GET /api/reports/{report_id}`
- `GET /api/reports`
- `DELETE /api/reports/{report_id}`
- `GET /api/competitors`
- `GET /api/competitors/{domain_id}/available-period`
- `GET /api/competitors/{domain_id}/summary`
- `GET /api/competitors/{domain_id}/countries`
- `GET /api/competitors/{domain_id}/signals`
- `GET /api/channels/summary`
- `GET /api/channels/trend`
- `GET /api/channels/journey-sources`
- `POST /api/channels/recalculate`
- `GET /api/countries/{country_id}/opportunity-score`
- `POST /api/countries/{country_id}/opportunity-score/recalculate`
- `GET /api/opportunities/countries`
- `POST /api/strategy/budget`
- `GET /api/strategy/budget`
- `GET /api/strategy/budget/{strategy_id}`
- `POST /api/strategy/budget/{strategy_id}/archive`
- `POST /api/mas/analyze`
- `GET /api/mas/runs`
- `GET /api/mas/runs/{agent_run_id}`
- `GET /api/mas/runs/{agent_run_id}/steps`
- `GET /api/mas/runs/{agent_run_id}/evidence`
- `GET /api/history/reports`
- `GET /api/history/agent-runs`
- `GET /api/history/insights`
- `GET /api/history/recommendations`
- `GET /api/history/summaries`
- `POST /api/history/summaries`
- `PATCH /api/history/summaries/{summary_id}`

Expected report filenames:

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

Uploaded files are registered in `ingestion_runs` and `source_files`, validated, then written into dimension and fact tables.
After ingestion, backend runs data quality checks and updates `ingestion_runs.quality_status`.

## Country Overview

Stage 5 reads `fact_domain_country_daily` and returns market analytics by country and period.

The React UI shows:

- total competitor traffic;
- active competitors;
- market leader;
- top-3 concentration;
- device split;
- bounce/no-bounce split;
- daily trend;
- top competitors;
- generated rule-based summary.

## Country Metrics

Stage 6 creates `metric_country_daily` and `metric_country_period`.

Stored metrics include HHI, engagement score, volatility score, leader share, top-3 share, and quality status for the calculation.

## Country Reports

Stage 7 creates `report_snapshots` and generates rule-based Markdown reports from country summary, metrics, competitors, and channel data.

## Competitor Analysis

Stage 8 creates `metric_competitor_country_period` and adds competitor-level analytics by country.

The React UI shows:

- total competitor traffic;
- active countries;
- top country;
- device split;
- bounce/no-bounce split;
- daily trend;
- country ranking;
- movement signals;
- generated rule-based summary.

## Channel Intelligence

Stage 9 creates `metric_channel_period` and `metric_journey_source_period`.

The React UI shows:

- channel scope filters;
- dominant channel;
- channel dependency and diversification;
- channel profile;
- channel share and trend;
- channel metrics table;
- journey source details;
- recommendation hints.

## Opportunity Score

Stage 10 creates `country_opportunity_scores` and calculates country opportunity priority.

The React UI shows:

- opportunity score;
- recommended priority;
- market type;
- score breakdown;
- strengths;
- risks;
- explanation;
- country opportunity ranking.

## Budget Strategy

Stage 11 creates `budget_strategy_runs` and `budget_strategy_allocations`.

The React UI shows:

- budget strategy form;
- recommended strategy type;
- confidence score;
- channel budget allocation;
- expected traffic, leads, and clients;
- recommendations;
- risks;
- saved strategy history.

## MAS Orchestration

Stage 12 creates `agent_runs`, `agent_steps`, `agent_evidence`, `agent_insights`, and `agent_recommendations`.

The React UI shows:

- strategy request form;
- run status;
- agent steps timeline;
- final answer;
- evidence table;
- recommendations;
- run history.

## Knowledge History

Stage 13 creates `saved_summaries` and stores reusable summaries from MAS runs, country reports, and budget strategies.

The React UI shows:

- report history;
- MAS run history;
- insights history;
- recommendations history;
- saved summaries;
- detail panel;
- RAG-ready status and toggle.
