from fastapi import APIRouter, Depends, Response
from fastapi.responses import JSONResponse

from app.core.config import Settings, get_settings
from app.core.observability import metrics_response
from app.services.health_service import build_health, build_live, build_ready


router = APIRouter(prefix='/health', tags=['health'])


@router.get('')
def read_health(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    """Read system health.
    Args:
        settings (Settings): Application settings."""
    health_data = build_health(settings)
    return health_data


@router.get('/live')
def read_live(settings: Settings = Depends(get_settings)) -> dict[str, str]:
    """Read live status.
    Args:
        settings (Settings): Application settings."""
    health_data = build_live(settings)
    return health_data


@router.get('/ready')
def read_ready(settings: Settings = Depends(get_settings)) -> dict[str, str] | JSONResponse:
    """Read ready status.
    Args:
        settings (Settings): Application settings."""
    health_data = build_ready(settings)
    if health_data['status'] != 'ok':
        return JSONResponse(status_code=503, content=health_data)
    return health_data


@router.get('/metrics')
def read_metrics(settings: Settings = Depends(get_settings)) -> Response:
    """Read metrics.
    Args:
        settings (Settings): Application settings."""
    if not settings.metrics_enabled:
        return Response(status_code=404)
    response = metrics_response()
    return response
