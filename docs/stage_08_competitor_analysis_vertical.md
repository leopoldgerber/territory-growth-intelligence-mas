# Stage 8 - Competitor Analysis Vertical

Stage 8 adds a competitor-centric analytical path on top of the uploaded country facts.

## Backend

- `GET /api/competitors`
- `GET /api/competitors/{domain_id}/available-period`
- `GET /api/competitors/{domain_id}/summary`
- `GET /api/competitors/{domain_id}/countries`
- `GET /api/competitors/{domain_id}/signals`

The summary endpoint builds competitor traffic totals, top countries, desktop/mobile split, bounce/no-bounce split, daily trend, country movement signals, and a generated narrative.

## Storage

The migration `20260508_0005_create_competitor_metric_table.py` creates `metric_competitor_country_period` for period-level competitor-country metrics and signal flags.

## Frontend

The React app now includes `Competitor Overview` with:

- competitor selector;
- date range selector;
- summary cards;
- traffic trend;
- country ranking table;
- signal blocks;
- generated narrative.

## Quality Rules

Competitor analysis blocks execution when the latest ingestion run has failed quality checks. Warning quality status is shown as a banner while still allowing the analysis to render.
