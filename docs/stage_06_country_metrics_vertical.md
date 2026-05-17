# Stage 6 - Country Metrics Vertical

Stage 6 adds persisted analytical country metrics.

## Database

New tables:

- `metric_country_daily`
- `metric_country_period`

Both tables store versioned calculations with `calculation_version`.

## Backend

New API endpoints:

- `POST /api/countries/{country_id}/metrics/recalculate`
- `GET /api/countries/{country_id}/metrics`
- `GET /api/countries/{country_id}/metrics/daily`

Implemented formulas:

- active competitors;
- leader and leader share;
- top-3 share;
- market concentration HHI;
- weighted bounce rate;
- no-bounce share;
- weighted pages per visit;
- weighted visit duration;
- engagement score v1;
- market volatility score v1.

Metrics calculation is blocked when the latest dataset has failed quality checks.

## Frontend

Country Overview now shows:

- leader share;
- top-3 share;
- HHI;
- engagement score;
- volatility score;
- active competitors;
- bounce/no-bounce shares;
- daily metric mini charts.
