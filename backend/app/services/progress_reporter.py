from sqlalchemy.orm import Session

from app.services.job_service import add_event, update_job


def report_started(session: Session, job_id: str, step_name: str, message: str) -> str:
    """Report job start.
    Args:
        session (Session): Database session.
        job_id (str): Job identifier.
        step_name (str): Step name.
        message (str): Message."""
    update_job(session, job_id, 'running', 5, step_name)
    add_event(session, job_id, 'started', step_name, message, 5, {})
    session.commit()
    return job_id


def report_progress(session: Session, job_id: str, step_name: str, message: str, progress_percent: float) -> str:
    """Report job progress.
    Args:
        session (Session): Database session.
        job_id (str): Job identifier.
        step_name (str): Step name.
        message (str): Message.
        progress_percent (float): Progress percent."""
    update_job(session, job_id, 'running', progress_percent, step_name)
    add_event(session, job_id, 'progress', step_name, message, progress_percent, {})
    session.commit()
    return job_id


def report_warning(session: Session, job_id: str, step_name: str, message: str) -> str:
    """Report job warning.
    Args:
        session (Session): Database session.
        job_id (str): Job identifier.
        step_name (str): Step name.
        message (str): Message."""
    add_event(session, job_id, 'warning', step_name, message, None, {})
    session.commit()
    return job_id


def report_failed(session: Session, job_id: str, step_name: str, message: str) -> str:
    """Report job failure.
    Args:
        session (Session): Database session.
        job_id (str): Job identifier.
        step_name (str): Step name.
        message (str): Message."""
    update_job(session, job_id, 'failed', 100, step_name, None, message)
    add_event(session, job_id, 'error', step_name, message, 100, {})
    session.commit()
    return job_id


def report_completed(
    session: Session,
    job_id: str,
    step_name: str,
    message: str,
    result_payload: dict[str, object],
    status: str = 'success',
) -> str:
    """Report job completion.
    Args:
        session (Session): Database session.
        job_id (str): Job identifier.
        step_name (str): Step name.
        message (str): Message.
        result_payload (dict[str, object]): Result payload.
        status (str): Final status."""
    update_job(session, job_id, status, 100, step_name, result_payload, None)
    add_event(session, job_id, 'completed', step_name, message, 100, result_payload)
    session.commit()
    return job_id
