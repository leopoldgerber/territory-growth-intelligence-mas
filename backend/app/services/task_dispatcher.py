from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.services.job_service import set_task_id
from app.worker.celery_app import celery_app


def enqueue_task(session: Session, job_id: str, task_name: str, args: list[object]) -> str:
    """Enqueue Celery task.
    Args:
        session (Session): Database session.
        job_id (str): Job identifier.
        task_name (str): Task name.
        args (list[object]): Task arguments."""
    try:
        async_result = celery_app.send_task(task_name, args=args)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f'JOB_QUEUE_UNAVAILABLE: {exc}') from exc
    set_task_id(session, job_id, str(async_result.id))
    return job_id
