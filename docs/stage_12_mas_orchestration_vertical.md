# Stage 12 - MAS Orchestration Vertical

Stage 12 adds a synchronous rule-based MAS layer over the existing analytical verticals.

## Backend

- Added persistence tables for agent runs, steps, evidence, insights, and recommendations.
- Added `/api/mas/analyze` to run a complete strategy analysis.
- Added `/api/mas/runs`, `/api/mas/runs/{id}`, `/api/mas/runs/{id}/steps`, and `/api/mas/runs/{id}/evidence`.
- Added a tool registry over existing services:
  - country summary
  - country metrics
  - top competitors
  - channel summary
  - journey sources
  - opportunity score
  - budget strategy
  - country report
- Added rule-based agents:
  - Planner Agent
  - Country Analyst Agent
  - Competitor Analyst Agent
  - Channel Strategist Agent
  - Budget Strategist Agent
  - Report Writer Agent

## Frontend

- Added Strategy Assistant UI.
- Added run form with country, period, request, budget, currency, and goal controls.
- Added run status, steps timeline, final answer, evidence panel, recommendations, and run history.

## Current Behavior

The v1 orchestration is synchronous and deterministic. It does not use LLMs, RAG, or background workers. If budget is omitted, MAS runs market, competitor, channel, opportunity, and report steps without budget allocation.

## Run Mode

Because this stage adds database tables and frontend code, use:

```bash
make up-build
```

after pulling or applying these changes.
