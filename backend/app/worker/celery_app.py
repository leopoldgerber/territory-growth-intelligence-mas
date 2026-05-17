from celery import Celery

from app.core.config import get_settings


def create_celery() -> Celery:
    """Create Celery application.
    Args:
        None (None): No arguments are required."""
    settings = get_settings()
    celery_app = Celery(
        'territory_growth_jobs',
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
        include=['app.worker.tasks'],
    )
    celery_app.conf.update(
        task_track_started=True,
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        worker_prefetch_multiplier=1,
        beat_schedule={
            'scan-update-schedules-every-minute': {
                'task': 'scan_update_schedules_task',
                'schedule': 60.0,
            },
        },
    )
    return celery_app


celery_app = create_celery()
