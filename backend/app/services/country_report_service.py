from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.country import CountryItem, PeriodInfo
from app.schemas.report import CountryReportRequest, ReportResponse
from app.services.country_metrics_service import get_metrics
from app.services.country_query_service import get_country, validate_period
from app.services.country_summary_service import build_country_summary
from app.services.report_storage_service import create_report, get_report
from app.services.report_template_service import markdown_report, report_json
from app.services.summary_generation_service import create_report_summary


def channel_summary(session: Session, request: CountryReportRequest) -> list[dict[str, object]]:
    """Build channel summary.
    Args:
        session (Session): Database session.
        request (CountryReportRequest): Report request."""
    if not request.include_channels:
        return []
    result = session.execute(
        text(
            """
            WITH country_domains AS (
                SELECT DISTINCT date, domain_id
                FROM fact_domain_country_daily
                WHERE country_id = :country_id
                  AND date BETWEEN :date_from AND :date_to
            ),
            channel_totals AS (
                SELECT
                    channels.channel_code,
                    channels.channel_name,
                    SUM(facts.traffic) AS traffic
                FROM fact_domain_channel_daily AS facts
                JOIN country_domains
                    ON country_domains.domain_id = facts.domain_id
                   AND country_domains.date = facts.date
                JOIN dim_channel AS channels ON channels.channel_id = facts.channel_id
                GROUP BY channels.channel_code, channels.channel_name
            )
            SELECT
                channel_code,
                channel_name,
                traffic,
                traffic / NULLIF(SUM(traffic) OVER(), 0) AS traffic_share
            FROM channel_totals
            ORDER BY traffic DESC NULLS LAST
            """,
        ),
        {'country_id': request.country_id, 'date_from': request.date_from, 'date_to': request.date_to},
    )
    rows = [dict(row._mapping) for row in result]
    return rows


def response_from_row(row: dict[str, object]) -> ReportResponse:
    """Build report response.
    Args:
        row (dict[str, object]): Report row."""
    country = None
    if row.get('country_id') is not None:
        country = CountryItem(
            country_id=row['country_id'],
            country_name_en=row.get('country_name_en') or '',
            country_name_ru=row.get('country_name_ru'),
            has_data=True,
        )
    period = None
    if row.get('date_from') is not None and row.get('date_to') is not None:
        period = PeriodInfo(
            date_from=row['date_from'],
            date_to=row['date_to'],
            days_count=(row['date_to'] - row['date_from']).days + 1,
        )
    response = ReportResponse(
        report_id=row['report_id'],
        report_type=row['report_type'],
        status=row.get('status') or row.get('report_status') or 'generated',
        title=row['title'],
        country=country,
        period=period,
        data_quality_status=row.get('data_quality_status'),
        report_markdown=row.get('report_markdown'),
        report_json=row.get('report_json'),
        created_at=row.get('created_at'),
    )
    return response


def create_country_report(session: Session, request: CountryReportRequest) -> ReportResponse:
    """Create country report.
    Args:
        session (Session): Database session.
        request (CountryReportRequest): Report request."""
    country = get_country(session, request.country_id)
    if country is None:
        raise HTTPException(status_code=404, detail='Country not found.')
    period_error = validate_period(session, request.country_id, request.date_from, request.date_to)
    if period_error:
        raise HTTPException(status_code=400, detail=period_error)
    summary = build_country_summary(session, country, request.date_from, request.date_to, request.limit_competitors)
    metrics = get_metrics(
        session,
        request.country_id,
        request.date_from,
        request.date_to,
        request.calculation_version,
        True,
    )
    if metrics.calculation.data_quality_status == 'failed':
        raise HTTPException(
            status_code=409,
            detail='Country report cannot be generated because the dataset has failed quality checks.',
        )
    channels = channel_summary(session, request)
    structured_report = report_json(summary, metrics, channels)
    markdown = markdown_report(summary, metrics, channels)
    title = f'Country Report: {summary.country.country_name_en}, {request.date_from} - {request.date_to}'
    report_id = create_report(
        session,
        'country_report',
        title,
        request.country_id,
        country.get('region_id'),
        request.date_from,
        request.date_to,
        markdown,
        structured_report,
        request.model_dump(),
        metrics.calculation.data_quality_status or 'unknown',
        request.calculation_version,
        'rule_based_v1',
    )
    create_report_summary(session, report_id)
    session.commit()
    report = get_report(session, report_id)
    if report is None:
        raise HTTPException(status_code=500, detail='Report was not saved.')
    response = response_from_row(report)
    return response
