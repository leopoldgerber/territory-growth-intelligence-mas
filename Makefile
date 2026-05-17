COMPOSE=docker compose
COMPOSE_PROD=docker compose -f docker-compose.prod.yml

.PHONY: help setup up up-build down restart build rebuild logs logs-backend logs-frontend logs-postgres logs-worker logs-beat logs-redis ps health health-ready health-live health-metrics migrate migrate-current migrate-history migrate-downgrade shell-backend shell-frontend db-shell clean-volumes test-backend test-frontend test-e2e prod-up prod-up-build prod-down backup-db

help:
	@echo "Available commands:"
	@echo "  make setup          Create .env files from examples when missing"
	@echo "  make up             Start all services"
	@echo "  make up-build       Build and start all services"
	@echo "  make down           Stop services"
	@echo "  make restart        Restart services"
	@echo "  make build          Build images"
	@echo "  make rebuild        Rebuild images without cache and start"
	@echo "  make logs           Follow all logs"
	@echo "  make logs-backend   Follow backend logs"
	@echo "  make logs-frontend  Follow frontend logs"
	@echo "  make logs-postgres  Follow postgres logs"
	@echo "  make logs-worker    Follow worker logs"
	@echo "  make logs-beat      Follow scheduler logs"
	@echo "  make logs-redis     Follow redis logs"
	@echo "  make ps             Show service status"
	@echo "  make health         Call backend healthcheck"
	@echo "  make health-ready   Call backend readiness check"
	@echo "  make health-live    Call backend liveness check"
	@echo "  make health-metrics Call backend metrics endpoint"
	@echo "  make migrate        Apply Alembic migrations"
	@echo "  make migrate-current Show current Alembic revision"
	@echo "  make migrate-history Show Alembic history"
	@echo "  make migrate-downgrade Downgrade one Alembic revision"
	@echo "  make shell-backend  Open backend shell"
	@echo "  make shell-frontend Open frontend shell"
	@echo "  make db-shell       Open PostgreSQL shell"
	@echo "  make clean-volumes  Stop services and remove volumes"
	@echo "  make test-backend   Run backend unittest suite"
	@echo "  make test-frontend  Run frontend unit tests"
	@echo "  make test-e2e       Run frontend Playwright smoke tests"
	@echo "  make prod-up        Start production compose"
	@echo "  make prod-up-build  Build and start production compose"
	@echo "  make prod-down      Stop production compose"
	@echo "  make backup-db      Run PostgreSQL backup script"

setup:
	python -c "from pathlib import Path; import shutil; pairs=[('.env.example','.env'),('backend/.env.example','backend/.env'),('frontend/.env.example','frontend/.env')]; [shutil.copyfile(src, dst) for src, dst in pairs if Path(src).exists() and not Path(dst).exists()]"

up:
	$(COMPOSE) up

up-build:
	$(COMPOSE) up --build

down:
	$(COMPOSE) down

restart:
	$(COMPOSE) restart

build:
	$(COMPOSE) build

rebuild:
	$(COMPOSE) build --no-cache
	$(COMPOSE) up

logs:
	$(COMPOSE) logs -f

logs-backend:
	$(COMPOSE) logs -f backend

logs-frontend:
	$(COMPOSE) logs -f frontend

logs-postgres:
	$(COMPOSE) logs -f postgres

logs-worker:
	$(COMPOSE) logs -f worker

logs-beat:
	$(COMPOSE) logs -f beat

logs-redis:
	$(COMPOSE) logs -f redis

ps:
	$(COMPOSE) ps

health:
	curl http://localhost:8000/api/health

health-ready:
	curl http://localhost:8000/api/health/ready

health-live:
	curl http://localhost:8000/api/health/live

health-metrics:
	curl http://localhost:8000/api/health/metrics

migrate:
	$(COMPOSE) exec backend alembic upgrade head

migrate-current:
	$(COMPOSE) exec backend alembic current

migrate-history:
	$(COMPOSE) exec backend alembic history

migrate-downgrade:
	$(COMPOSE) exec backend alembic downgrade -1

shell-backend:
	$(COMPOSE) exec backend sh

shell-frontend:
	$(COMPOSE) exec frontend sh

db-shell:
	$(COMPOSE) exec postgres psql -U tgi_user -d tgi_db

clean-volumes:
	$(COMPOSE) down -v

test-backend:
	cd backend && python -m unittest discover -v tests

test-frontend:
	cd frontend && npm run test

test-e2e:
	cd frontend && npm run test:e2e

prod-up:
	$(COMPOSE_PROD) up

prod-up-build:
	$(COMPOSE_PROD) up --build

prod-down:
	$(COMPOSE_PROD) down

backup-db:
	powershell -ExecutionPolicy Bypass -File scripts/backup_postgres.ps1
