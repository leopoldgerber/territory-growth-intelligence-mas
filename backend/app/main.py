from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.core.observability import request_middleware, setup_sentry


def create_app() -> FastAPI:
    """Create FastAPI application.
    Args:
        None (None): No arguments are required."""
    settings = get_settings()
    setup_logging(settings)
    setup_sentry(settings)
    app = FastAPI(title=settings.app_name, debug=settings.debug)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    app.middleware('http')(request_middleware)
    app.include_router(api_router)
    return app


app = create_app()
