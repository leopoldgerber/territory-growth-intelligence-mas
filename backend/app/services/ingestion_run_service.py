import json
from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session


def map_row(row: object) -> dict[str, object]:
    """Map database row.
    Args:
        row (object): SQLAlchemy row."""
    data = dict(row._mapping)
    return data


def get_source(session: Session, source_name: str) -> int:
    """Get source identifier.
    Args:
        session (Session): Database session.
        source_name (str): Source name."""
    result = session.execute(
        text(
            """
            INSERT INTO data_sources (source_name, source_type, provider, description)
            VALUES (:source_name, 'manual', 'Internal', 'Manual file upload')
            ON CONFLICT (source_name) DO UPDATE SET source_name = EXCLUDED.source_name
            RETURNING source_id
            """,
        ),
        {'source_name': source_name},
    )
    source_id = int(result.scalar_one())
    return source_id


def create_run(
    session: Session,
    source_name: str,
    granularity: str,
    period_start: date | None,
    period_end: date | None,
) -> int:
    """Create ingestion run.
    Args:
        session (Session): Database session.
        source_name (str): Source name.
        granularity (str): Data granularity.
        period_start (date | None): Period start date.
        period_end (date | None): Period end date."""
    source_id = get_source(session, source_name)
    result = session.execute(
        text(
            """
            INSERT INTO ingestion_runs (
                source_id, run_type, granularity, period_start, period_end, status, started_at, metadata
            )
            VALUES (:source_id, 'manual_upload', :granularity, :period_start, :period_end, 'running', now(), :metadata)
            RETURNING run_id
            """,
        ),
        {
            'source_id': source_id,
            'granularity': granularity,
            'period_start': period_start,
            'period_end': period_end,
            'metadata': json.dumps({'source_name': source_name}),
        },
    )
    run_id = int(result.scalar_one())
    return run_id


def finish_run(session: Session, run_id: int, status: str, row_count: int, error_message: str | None) -> int:
    """Finish ingestion run.
    Args:
        session (Session): Database session.
        run_id (int): Ingestion run identifier.
        status (str): Run status.
        row_count (int): Processed row count.
        error_message (str | None): Error message."""
    session.execute(
        text(
            """
            UPDATE ingestion_runs
            SET status = :status, finished_at = now(), row_count = :row_count, error_message = :error_message
            WHERE run_id = :run_id
            """,
        ),
        {'run_id': run_id, 'status': status, 'row_count': row_count, 'error_message': error_message},
    )
    return run_id


def update_quality(session: Session, run_id: int, quality_status: str) -> int:
    """Update quality status.
    Args:
        session (Session): Database session.
        run_id (int): Ingestion run identifier.
        quality_status (str): Quality status."""
    session.execute(
        text(
            """
            UPDATE ingestion_runs
            SET quality_status = :quality_status
            WHERE run_id = :run_id
            """,
        ),
        {'run_id': run_id, 'quality_status': quality_status},
    )
    return run_id


def list_runs(session: Session) -> list[dict[str, object]]:
    """List ingestion runs.
    Args:
        session (Session): Database session."""
    result = session.execute(
        text(
            """
            SELECT
                runs.run_id,
                sources.source_name,
                runs.run_type,
                runs.granularity,
                runs.status,
                runs.quality_status,
                runs.row_count,
                runs.started_at::text AS started_at,
                runs.finished_at::text AS finished_at,
                runs.error_message
            FROM ingestion_runs AS runs
            LEFT JOIN data_sources AS sources ON sources.source_id = runs.source_id
            ORDER BY runs.started_at DESC NULLS LAST, runs.run_id DESC
            LIMIT 50
            """,
        ),
    )
    runs = [map_row(row) for row in result]
    return runs


def get_run(session: Session, run_id: int) -> dict[str, object] | None:
    """Get ingestion run.
    Args:
        session (Session): Database session.
        run_id (int): Ingestion run identifier."""
    result = session.execute(
        text(
            """
            SELECT
                runs.run_id,
                sources.source_name,
                runs.run_type,
                runs.granularity,
                runs.status,
                runs.quality_status,
                runs.row_count,
                runs.started_at::text AS started_at,
                runs.finished_at::text AS finished_at,
                runs.error_message
            FROM ingestion_runs AS runs
            LEFT JOIN data_sources AS sources ON sources.source_id = runs.source_id
            WHERE runs.run_id = :run_id
            """,
        ),
        {'run_id': run_id},
    )
    row = result.first()
    data = map_row(row) if row else None
    return data
