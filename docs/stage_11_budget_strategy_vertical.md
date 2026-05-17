# Stage 11 - Budget Strategy Vertical

Stage 11 adds the first rule-based budget strategy module.

## Backend

- `POST /api/strategy/budget`
- `GET /api/strategy/budget`
- `GET /api/strategy/budget/{strategy_id}`
- `POST /api/strategy/budget/{strategy_id}/archive`

The strategy service combines country metrics, opportunity score, channel analysis, campaign goal, risk appetite, and assumptions.

## Storage

The migration `20260508_0008_create_budget_strategy_tables.py` creates:

- `budget_strategy_runs`
- `budget_strategy_allocations`

## Strategy Output

The API returns:

- recommended strategy type;
- confidence score;
- channel allocation;
- expected traffic;
- expected leads;
- expected clients;
- recommendations;
- risks;
- saved strategy history.

## Frontend

The React app now includes `Budget Strategy` with:

- strategy form;
- country and period selectors;
- budget, currency, goal, and risk appetite inputs;
- allocation chart;
- allocation table;
- expected effect cards;
- recommendations and risks;
- strategy history table.

## Quality Rules

Budget strategy generation blocks when opportunity scoring blocks because of failed data quality. With warnings, strategy is generated with lower confidence and explicit risk text.
