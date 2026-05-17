# Stage 10 - Opportunity Score Vertical

Stage 10 adds country-level opportunity scoring.

## Backend

- `GET /api/countries/{country_id}/opportunity-score`
- `POST /api/countries/{country_id}/opportunity-score/recalculate`
- `GET /api/opportunities/countries`

The scoring service combines country metrics, channel metrics, competition signals, data quality, volatility, localization potential, and entry difficulty.

## Storage

The migration `20260508_0007_create_opportunity_scores.py` creates `country_opportunity_scores`.

Stored fields include:

- final opportunity score;
- traffic, competition, quality, channel gap, volatility, localization, and entry difficulty components;
- recommended priority;
- market type;
- strengths;
- risks;
- explanation;
- score breakdown;
- data quality status.

## Frontend

The React app now includes:

- an Opportunity Score card inside Country Overview;
- component breakdown;
- strengths and risks;
- rule-based explanation;
- country opportunity ranking table.

## Quality Rules

Opportunity scoring blocks execution when latest quality status is `failed`. With `warning`, the score is still calculated and the warning is included as a risk.
