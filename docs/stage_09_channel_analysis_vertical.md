# Stage 9 - Channel Analysis Vertical

Stage 9 adds channel intelligence for global, country, competitor, and country + competitor scopes.

## Backend

- `GET /api/channels/summary`
- `GET /api/channels/trend`
- `GET /api/channels/journey-sources`
- `POST /api/channels/recalculate`

The summary endpoint calculates channel traffic, channel share, dominant channel, dependency score, diversification score, profile, stability, growth, and recommendation hints.

## Storage

The migration `20260508_0006_create_channel_metric_tables.py` creates:

- `metric_channel_period`
- `metric_journey_source_period`

## Country Approximation

Current channel and journey reports are domain-level. Country-level channel analysis is estimated by weighting domain-level channel or source mix by each domain's presence in the selected country.

The UI shows a warning whenever this approximation is used.

## Frontend

The React app now includes `Channel Intelligence` with:

- scope selector;
- optional country and competitor selectors;
- period selector;
- channel summary cards;
- channel share chart;
- channel trend chart;
- channel metrics table;
- journey source table;
- recommendation hints.

## Quality Rules

Channel analysis blocks execution when the latest ingestion run has failed quality checks. Warning quality status is shown as a banner while still allowing analysis to render.
