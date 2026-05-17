import json
import logging
from contextvars import ContextVar
from datetime import datetime, timezone

from app.core.config import Settings


request_id_var: ContextVar[str | None] = ContextVar('request_id', default=None)
job_id_var: ContextVar[str | None] = ContextVar('job_id', default=None)
project_id_var: ContextVar[int | None] = ContextVar('project_id', default=None)
user_id_var: ContextVar[int | None] = ContextVar('user_id', default=None)


class JsonFormatter(logging.Formatter):
    """Format JSON logs.
    Args:
        None (None): No arguments are required."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record.
        Args:
            record (logging.LogRecord): Log record."""
        payload = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'request_id': request_id_var.get(),
            'job_id': job_id_var.get(),
            'project_id': project_id_var.get(),
            'user_id': user_id_var.get(),
        }
        if hasattr(record, 'duration_ms'):
            payload['duration_ms'] = getattr(record, 'duration_ms')
        if record.exc_info is not None:
            payload['exception'] = self.formatException(record.exc_info)
        serialized_value = json.dumps(payload, ensure_ascii=True)
        return serialized_value


def setup_logging(settings: Settings) -> logging.Logger:
    """Setup application logging.
    Args:
        settings (Settings): Application settings."""
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    handler = logging.StreamHandler()
    if settings.log_json:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s %(message)s'))
    root_logger.addHandler(handler)
    logger = logging.getLogger('territory_growth_api')
    return logger


def set_log_context(
    request_id: str | None = None,
    job_id: str | None = None,
    project_id: int | None = None,
    user_id: int | None = None,
) -> None:
    """Set log context.
    Args:
        request_id (str | None): Request identifier.
        job_id (str | None): Job identifier.
        project_id (int | None): Project identifier.
        user_id (int | None): User identifier."""
    request_id_var.set(request_id)
    job_id_var.set(job_id)
    project_id_var.set(project_id)
    user_id_var.set(user_id)
