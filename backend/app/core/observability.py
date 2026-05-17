import logging
import time
import uuid

import sentry_sdk
from fastapi import Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from sentry_sdk.integrations.fastapi import FastApiIntegration

from app.core.config import Settings
from app.core.logging import set_log_context


REQUEST_COUNT = Counter('tgi_http_requests_total', 'Total HTTP requests', ['method', 'path', 'status'])
REQUEST_DURATION = Histogram('tgi_http_request_duration_seconds', 'HTTP request duration', ['method', 'path'])


def setup_sentry(settings: Settings) -> None:
    """Setup sentry.
    Args:
        settings (Settings): Application settings."""
    if settings.sentry_dsn == '':
        return
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.sentry_environment,
        integrations=[FastApiIntegration()],
        send_default_pii=False,
    )


async def request_middleware(request: Request, call_next: object) -> Response:
    """Process request middleware.
    Args:
        request (Request): Request object.
        call_next (object): Next app callable."""
    started_at = time.perf_counter()
    request_id = request.headers.get('x-request-id') or str(uuid.uuid4())
    project_header = request.headers.get('x-project-id')
    project_id = int(project_header) if project_header and project_header.isdigit() else None
    set_log_context(request_id=request_id, project_id=project_id)
    logger = logging.getLogger('territory_growth_api.request')
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        logger.exception(
            'request_failed',
            extra={'duration_ms': duration_ms},
        )
        REQUEST_COUNT.labels(request.method, request.url.path, '500').inc()
        REQUEST_DURATION.labels(request.method, request.url.path).observe(time.perf_counter() - started_at)
        raise
    duration_seconds = time.perf_counter() - started_at
    duration_ms = round(duration_seconds * 1000, 2)
    response.headers['x-request-id'] = request_id
    REQUEST_COUNT.labels(request.method, request.url.path, str(response.status_code)).inc()
    REQUEST_DURATION.labels(request.method, request.url.path).observe(duration_seconds)
    logger.info(
        'request_completed',
        extra={'duration_ms': duration_ms},
    )
    return response


def metrics_response() -> Response:
    """Build metrics response.
    Args:
        None (None): No arguments are required."""
    content = generate_latest()
    response = Response(content=content, media_type=CONTENT_TYPE_LATEST)
    return response
