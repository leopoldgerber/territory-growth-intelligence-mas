# Stage 13 - Saved Insights, Summaries, and Reports

Stage 13 turns generated analytical artifacts into reusable history and a future RAG-ready knowledge base.

## Backend

- Added `saved_summaries` table with source metadata, tags, confidence, data quality, `rag_ready`, and `embedding_status`.
- Added summary storage service with RAG-ready validation.
- Added summary generation from:
  - MAS runs;
  - country reports;
  - budget strategies.
- Added history service for reports, MAS runs, insights, recommendations, and summaries.
- Added `/api/history/*` endpoints:
  - `GET /api/history/reports`
  - `GET /api/history/agent-runs`
  - `GET /api/history/insights`
  - `GET /api/history/recommendations`
  - `GET /api/history/summaries`
  - `POST /api/history/summaries`
  - `PATCH /api/history/summaries/{summary_id}`

## Frontend

- Added Knowledge History screen.
- Added tabs for reports, MAS runs, insights, recommendations, and summaries.
- Added detail panel for selected history item.
- Added RAG-ready toggle for saved summaries.

## Data Quality

Summaries with failed data quality can be stored as historical artifacts, but they are not automatically marked as RAG-ready.

## Run Mode

This stage adds a database migration and frontend code, so use:

```bash
make up-build
```
