# Local Setup

## Requirements

- Docker Desktop
- Python 3.12 for local backend checks
- Node.js 22 for local frontend checks

## Startup

```bash
make setup
make up-build
make migrate
```

## Local URLs

- Frontend: `http://localhost:5173`
- Backend docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/api/health`

## Local checks

```bash
make test-backend
make health
make health-ready
```
