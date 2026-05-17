from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.marketing import DataWarning


def project_filter(project_id: int) -> str:
    """Build project filter.
    Args:
        project_id (int): Project identifier."""
    filter_sql = """
    (
        fact.domain_id IN (
            SELECT domain_id
            FROM project_competitors
            WHERE project_id = :project_id AND is_active = TRUE
        )
        OR fact.country_id IN (
            SELECT country_id
            FROM project_target_countries
            WHERE project_id = :project_id
        )
    )
    """
    return filter_sql


def has_rows(session: Session, table_name: str, project_id: int) -> bool:
    """Check data rows.
    Args:
        session (Session): Database session.
        table_name (str): Table name.
        project_id (int): Project identifier."""
    result = session.execute(
        text(
            f"""
            SELECT COUNT(*)
            FROM {table_name} AS fact
            WHERE {project_filter(project_id)}
            """,
        ),
        {'project_id': project_id},
    )
    rows_exist = int(result.scalar_one() or 0) > 0
    return rows_exist


def source_warnings(session: Session, sources: dict[str, str], project_id: int) -> list[DataWarning]:
    """Build source warnings.
    Args:
        session (Session): Database session.
        sources (dict[str, str]): Source table mapping.
        project_id (int): Project identifier."""
    warnings = []
    for source_name, table_name in sources.items():
        if not has_rows(session, table_name, project_id):
            warnings.append(
                DataWarning(
                    source_name=source_name,
                    status='missing',
                    message=f'{source_name} data is not available for this project.',
                ),
            )
    return warnings


def row_dicts(rows: object) -> list[dict[str, object]]:
    """Convert rows.
    Args:
        rows (object): SQL result rows."""
    items = [dict(row._mapping) for row in rows]
    return items
