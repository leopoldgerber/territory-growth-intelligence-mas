from fastapi import APIRouter

from app.api.routes.alerts import router as alerts_router
from app.api.routes.auth import router as auth_router
from app.api.routes.channels import router as channels_router
from app.api.routes.countries import router as countries_router
from app.api.routes.competitors import router as competitors_router
from app.api.routes.data import router as data_router
from app.api.routes.feedback import router as feedback_router
from app.api.routes.health import router as health_router
from app.api.routes.history import router as history_router
from app.api.routes.jobs import router as jobs_router
from app.api.routes.marketing import router as marketing_router
from app.api.routes.mas import router as mas_router
from app.api.routes.opportunities import router as opportunities_router
from app.api.routes.projects import router as projects_router
from app.api.routes.reports import router as reports_router
from app.api.routes.strategy import router as strategy_router
from app.api.routes.updates import router as updates_router
from app.api.routes.workflow import router as workflow_router


api_router = APIRouter(prefix='/api')
api_router.include_router(alerts_router)
api_router.include_router(auth_router)
api_router.include_router(channels_router)
api_router.include_router(countries_router)
api_router.include_router(competitors_router)
api_router.include_router(data_router)
api_router.include_router(feedback_router)
api_router.include_router(health_router)
api_router.include_router(history_router)
api_router.include_router(jobs_router)
api_router.include_router(marketing_router)
api_router.include_router(mas_router)
api_router.include_router(opportunities_router)
api_router.include_router(projects_router)
api_router.include_router(reports_router)
api_router.include_router(strategy_router)
api_router.include_router(updates_router)
api_router.include_router(workflow_router)
