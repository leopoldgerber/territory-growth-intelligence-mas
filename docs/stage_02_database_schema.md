# Stage 02 Database Schema And Migrations

This stage adds Alembic migrations and the first production-ready PostgreSQL schema.

## Scope

Included:

- ingestion and audit tables;
- dimension tables;
- daily fact tables for current report outputs;
- foreign keys, unique constraints, and indexes;
- seed data for channels, data sources, and calendar dates.

Not included:

- Excel or ZIP upload;
- ingestion API;
- analytics calculations;
- dashboard features;
- auth;
- MAS agents.

## Migration

Initial migration:

```text
backend/alembic/versions/20260507_0001_create_initial_core_schema.py
```

It is applied automatically when the backend container starts:

```bash
docker compose up --build
```

Manual commands:

```bash
make migrate
make migrate-current
make migrate-history
make migrate-downgrade
```

## Tables

Ingestion and audit:

- `data_sources`
- `ingestion_runs`
- `source_files`
- `data_quality_checks`

Dimensions:

- `dim_date`
- `dim_company`
- `dim_domain`
- `dim_region`
- `dim_country`
- `dim_channel`
- `dim_journey_source`

Facts:

- `fact_domain_country_daily`
- `fact_domain_device_daily`
- `fact_domain_channel_daily`
- `fact_domain_journey_source_daily`

## Seed Data

The migration seeds:

- 5 channels in `dim_channel`;
- 3 sources in `data_sources`;
- full daily calendar from `2020-01-01` through `2030-12-31` in `dim_date`.

## Verification

After startup:

```bash
make health
make migrate-current
make db-shell
```

Inside PostgreSQL:

```sql
\dt
select count(*) from dim_channel;
select count(*) from data_sources;
select count(*) from dim_date;
```
