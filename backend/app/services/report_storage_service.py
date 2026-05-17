import json
from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session


def create_report(
    session: Session,
    report_type: str,
    title: str,
    country_id: int,
    region_id: int | None,
    period_start: date,
    period_end: date,
    report_markdown: str,
    report_json: dict[str, object],
    input_params: dict[str, object],
    data_quality_status: str,
    calculation_version: str,
    generator_version: str,
) -> int:
    """Create report snapshot.
    Args:
        session (Session): Database session.
        report_type (str): Report type.
        title (str): Report title.
        country_id (int): Country identifier.
        region_id (int | None): Region identifier.
        period_start (date): Period start date.
        period_end (date): Period end date.
        report_markdown (str): Markdown report.
        report_json (dict[str, object]): Structured report.
        input_params (dict[str, object]): Input parameters.
        data_quality_status (str): Data quality status.
        calculation_version (str): Calculation version.
        generator_version (str): Generator version."""
    result = session.execute(
        text(
            """
            INSERT INTO report_snapshots (
                report_type, title, country_id, region_id, period_start, period_end, report_status,
                report_markdown, report_json, input_params, data_quality_status, calculation_version, generator_version
            )
            VALUES (
                :report_type, :title, :country_id, :region_id, :period_start, :period_end, 'generated',
                :report_markdown, CAST(:report_json AS jsonb), CAST(:input_params AS jsonb),
                :data_quality_status, :calculation_version, :generator_version
            )
            ON CONFLICT (country_id, period_start, period_end, report_type, calculation_version) DO UPDATE
            SET title = EXCLUDED.title,
                report_status = EXCLUDED.report_status,
                report_markdown = EXCLUDED.report_markdown,
                report_json = EXCLUDED.report_json,
                input_params = EXCLUDED.input_params,
                data_quality_status = EXCLUDED.data_quality_status,
                generator_version = EXCLUDED.generator_version,
                updated_at = now()
            RETURNING report_id
            """,
        ),
        {
            'report_type': report_type,
            'title': title,
            'country_id': country_id,
            'region_id': region_id,
            'period_start': period_start,
            'period_end': period_end,
            'report_markdown': report_markdown,
            'report_json': json.dumps(report_json, default=str),
            'input_params': json.dumps(input_params, default=str),
            'data_quality_status': data_quality_status,
            'calculation_version': calculation_version,
            'generator_version': generator_version,
        },
    )
    report_id = int(result.scalar_one())
    return report_id


def get_report(session: Session, report_id: int) -> dict[str, object] | None:
    """Get report snapshot.
    Args:
        session (Session): Database session.
        report_id (int): Report identifier."""
    result = session.execute(
        text(
            """
            SELECT
                reports.report_id,
                reports.report_type,
                reports.title,
                reports.report_status AS status,
                reports.report_status,
                reports.report_markdown,
                reports.report_json,
                reports.data_quality_status,
                reports.created_at::text AS created_at,
                countries.country_id,
                countries.country_name_en,
                countries.country_name_ru,
                countries.location_name_ru,
                countries.is_active AS has_data,
                reports.period_start AS date_from,
                reports.period_end AS date_to
            FROM report_snapshots AS reports
            LEFT JOIN dim_country AS countries ON countries.country_id = reports.country_id
            WHERE reports.report_id = :report_id
            """,
        ),
        {'report_id': report_id},
    )
    row = result.first()
    if row is None:
        return None
    data = dict(row._mapping)
    return data


def find_report(
    session: Session,
    report_type: str,
    country_id: int,
    period_start: date,
    period_end: date,
    calculation_version: str,
) -> dict[str, object] | None:
    """Find report snapshot.
    Args:
        session (Session): Database session.
        report_type (str): Report type.
        country_id (int): Country identifier.
        period_start (date): Period start date.
        period_end (date): Period end date.
        calculation_version (str): Calculation version."""
    result = session.execute(
        text(
            """
            SELECT report_id
            FROM report_snapshots
            WHERE report_type = :report_type
              AND country_id = :country_id
              AND period_start = :period_start
              AND period_end = :period_end
              AND calculation_version = :calculation_version
              AND report_status <> 'archived'
            ORDER BY created_at DESC, report_id DESC
            LIMIT 1
            """,
        ),
        {
            'report_type': report_type,
            'country_id': country_id,
            'period_start': period_start,
            'period_end': period_end,
            'calculation_version': calculation_version,
        },
    )
    report_id = result.scalar_one_or_none()
    report = get_report(session, int(report_id)) if report_id is not None else None
    return report


def list_reports(
    session: Session,
    report_type: str | None,
    country_id: int | None,
    limit: int,
    offset: int,
    project_id: int | None = None,
) -> dict[str, object]:
    """List report snapshots.
    Args:
        session (Session): Database session.
        report_type (str | None): Report type.
        country_id (int | None): Country identifier.
        limit (int): Result limit.
        offset (int): Result offset.
        project_id (int | None): Project identifier."""
    filters = ["reports.report_status <> 'archived'"]
    params: dict[str, object] = {'limit': limit, 'offset': offset}
    if report_type:
        filters.append('reports.report_type = :report_type')
        params['report_type'] = report_type
    if country_id:
        filters.append('reports.country_id = :country_id')
        params['country_id'] = country_id
    if project_id is not None:
        filters.append('reports.project_id = :project_id')
        params['project_id'] = project_id
    where_clause = ' AND '.join(filters)
    result = session.execute(
        text(
            f"""
            SELECT
                reports.report_id,
                reports.project_id,
                reports.report_type,
                reports.title,
                reports.report_status,
                countries.country_name_en,
                reports.period_start,
                reports.period_end,
                reports.data_quality_status,
                reports.created_at::text AS created_at,
                COUNT(*) OVER() AS total
            FROM report_snapshots AS reports
            LEFT JOIN dim_country AS countries ON countries.country_id = reports.country_id
            WHERE {where_clause}
            ORDER BY reports.created_at DESC, reports.report_id DESC
            LIMIT :limit OFFSET :offset
            """,
        ),
        params,
    )
    rows = [dict(row._mapping) for row in result]
    total = int(rows[0]['total']) if rows else 0
    for row in rows:
        row.pop('total', None)
    return {'items': rows, 'total': total}


def archive_report(session: Session, report_id: int) -> int:
    """Archive report snapshot.
    Args:
        session (Session): Database session.
        report_id (int): Report identifier."""
    session.execute(
        text(
            """
            UPDATE report_snapshots
            SET report_status = 'archived', updated_at = now()
            WHERE report_id = :report_id
            """,
        ),
        {'report_id': report_id},
    )
    session.commit()
    return report_id
