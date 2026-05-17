from pathlib import Path

from sqlalchemy import text
from sqlalchemy.orm import Session


def create_file(
    session: Session,
    run_id: int,
    file_path: Path,
    report_type: str,
    file_hash_value: str,
    is_synthetic: bool,
) -> int:
    """Create source file.
    Args:
        session (Session): Database session.
        run_id (int): Ingestion run identifier.
        file_path (Path): Source file path.
        report_type (str): Report type.
        file_hash_value (str): File hash value.
        is_synthetic (bool): Synthetic data flag."""
    result = session.execute(
        text(
            """
            INSERT INTO source_files (
                run_id, source_file_name, report_type, file_path, file_hash, file_size_bytes, schema_version, is_synthetic
            )
            VALUES (:run_id, :file_name, :report_type, :file_path, :file_hash, :file_size, 'stage_03', :is_synthetic)
            RETURNING file_id
            """,
        ),
        {
            'run_id': run_id,
            'file_name': file_path.name,
            'report_type': report_type,
            'file_path': str(file_path),
            'file_hash': file_hash_value,
            'file_size': file_path.stat().st_size,
            'is_synthetic': is_synthetic,
        },
    )
    file_id = int(result.scalar_one())
    return file_id


def list_files(session: Session, run_id: int) -> list[dict[str, object]]:
    """List source files.
    Args:
        session (Session): Database session.
        run_id (int): Ingestion run identifier."""
    result = session.execute(
        text(
            """
            SELECT
                file_id,
                source_file_name AS file_name,
                report_type,
                'registered' AS status,
                0 AS row_count
            FROM source_files
            WHERE run_id = :run_id
            ORDER BY file_id
            """,
        ),
        {'run_id': run_id},
    )
    files = [dict(row._mapping) for row in result]
    return files


def add_quality(
    session: Session,
    run_id: int,
    file_id: int | None,
    check_name: str,
    status: str,
    details: str,
    table_name: str | None = None,
    check_type: str | None = None,
    severity: str | None = None,
    message: str | None = None,
    affected_rows_count: int | None = None,
    sample_rows: str | None = None,
    quality_dimension: str | None = None,
) -> int:
    """Add quality check.
    Args:
        session (Session): Database session.
        run_id (int): Ingestion run identifier.
        file_id (int | None): Source file identifier.
        check_name (str): Check name.
        status (str): Check status.
        details (str): Check details.
        table_name (str | None): Target table name.
        check_type (str | None): Check type.
        severity (str | None): Check severity.
        message (str | None): Check message.
        affected_rows_count (int | None): Affected row count.
        sample_rows (str | None): Sample rows JSON.
        quality_dimension (str | None): Quality dimension."""
    result = session.execute(
        text(
            """
            INSERT INTO data_quality_checks (
                run_id, file_id, table_name, check_name, check_type, status, severity, message,
                affected_rows_count, sample_rows, quality_dimension, details
            )
            VALUES (
                :run_id, :file_id, :table_name, :check_name, :check_type, :status, :severity, :message,
                :affected_rows_count, CAST(:sample_rows AS jsonb), :quality_dimension, CAST(:details AS jsonb)
            )
            RETURNING check_id
            """,
        ),
        {
            'run_id': run_id,
            'file_id': file_id,
            'table_name': table_name,
            'check_name': check_name,
            'check_type': check_type or 'upload_validation',
            'status': status,
            'severity': severity,
            'message': message,
            'affected_rows_count': affected_rows_count,
            'sample_rows': sample_rows or '[]',
            'quality_dimension': quality_dimension,
            'details': details,
        },
    )
    check_id = int(result.scalar_one())
    return check_id
