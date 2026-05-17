from redis import Redis

from app.core.config import Settings
from app.db.session import check_database, check_migrations


def redis_ok(settings: Settings) -> bool:
    """Check redis connection.
    Args:
        settings (Settings): Application settings."""
    client = Redis.from_url(settings.redis_url)
    is_ok = bool(client.ping())
    return is_ok


def worker_queue_ok(settings: Settings) -> bool:
    """Check worker queue.
    Args:
        settings (Settings): Application settings."""
    if not settings.worker_ping_enabled:
        return True
    client = Redis.from_url(settings.redis_url)
    queue_size = int(client.llen('celery'))
    return queue_size >= 0


def health_payload(settings: Settings) -> dict[str, str]:
    """Build health payload.
    Args:
        settings (Settings): Application settings."""
    database_status = 'ok'
    redis_status = 'ok'
    migrations_status = 'ok'
    queue_status = 'ok'
    system_status = 'ok'
    try:
        check_database()
    except Exception:
        database_status = 'error'
        system_status = 'degraded'
    try:
        redis_ok(settings)
    except Exception:
        redis_status = 'error'
        system_status = 'degraded'
    try:
        if not check_migrations():
            migrations_status = 'missing'
            system_status = 'degraded'
    except Exception:
        migrations_status = 'error'
        system_status = 'degraded'
    try:
        if not worker_queue_ok(settings):
            queue_status = 'warning'
            system_status = 'degraded'
    except Exception:
        queue_status = 'error'
        system_status = 'degraded'
    payload = {
        'status': system_status,
        'backend': 'ok',
        'database': database_status,
        'redis': redis_status,
        'migrations': migrations_status,
        'queue': queue_status,
        'app_name': settings.app_name,
        'environment': settings.app_env,
    }
    return payload


def build_health(settings: Settings) -> dict[str, str]:
    """Build health response.
    Args:
        settings (Settings): Application settings."""
    payload = health_payload(settings)
    return payload


def build_live(settings: Settings) -> dict[str, str]:
    """Build live response.
    Args:
        settings (Settings): Application settings."""
    payload = {
        'status': 'ok',
        'backend': 'ok',
        'app_name': settings.app_name,
        'environment': settings.app_env,
    }
    return payload


def build_ready(settings: Settings) -> dict[str, str]:
    """Build ready response.
    Args:
        settings (Settings): Application settings."""
    payload = health_payload(settings)
    return payload
