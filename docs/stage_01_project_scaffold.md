# Stage 01 Project Scaffold

This stage creates the minimal foundation for the future Territory Growth Intelligence MAS application.

## Goal

The working chain is:

```text
React frontend
  -> FastAPI backend
  -> PostgreSQL
```

The stage does not implement report uploads, MAS agents, analytics, dashboards, ingestion, or production database schemas.

## Backend

The backend lives in `backend/` and exposes:

```text
GET /api/health
```

The endpoint checks:

- backend process is alive;
- PostgreSQL connection can execute `SELECT 1`;
- application name and environment are loaded from env.

## Frontend

The frontend lives in `frontend/` and displays:

- project name;
- short scaffold description;
- backend status;
- database status;
- refresh button.

## PostgreSQL

PostgreSQL is launched by Docker Compose with:

- persistent `postgres_data` volume;
- database, user, and password from env;
- container healthcheck through `pg_isready`.

## Run

```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
docker compose up --build
```

## Done Criteria

- FastAPI starts.
- `/docs` is available.
- `/api/health` returns backend and database status.
- React starts.
- React calls `/api/health`.
- PostgreSQL starts through Docker Compose.
- All services run with one Docker Compose command.
