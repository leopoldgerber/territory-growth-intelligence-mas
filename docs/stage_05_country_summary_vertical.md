# Stage 5 - Country Summary Vertical

Stage 5 adds the first analytics screen: country plus period to market overview.

## Backend

New API endpoints:

- `GET /api/countries`
- `GET /api/countries/{country_id}/available-period`
- `GET /api/countries/{country_id}/summary`
- `GET /api/countries/{country_id}/competitors`

The services aggregate `fact_domain_country_daily` into:

- total competitor traffic;
- active competitors;
- leader and leader share;
- top-3 share;
- desktop and mobile split;
- bounce and no-bounce split;
- daily traffic trend;
- top competitors table;
- rule-based generated summary.

## Frontend

The React app now includes `CountryOverviewPage` with:

- country selector;
- period selector;
- summary cards;
- traffic trend chart;
- device split block;
- bounce/no-bounce block;
- top competitors table;
- generated summary;
- data quality warning.

## Quality Integration

The summary response includes `quality_warning` when the latest upload has `warning` or `failed` quality status.
