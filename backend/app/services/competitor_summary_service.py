from datetime import date

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.competitor import (
    CompetitorItem,
    CompetitorSummary,
    CompetitorSummaryMetrics,
)
from app.services.competitor_country_service import build_countries, country_rows, save_country_metrics
from app.services.competitor_narrative_service import build_summary
from app.services.competitor_query_service import get_competitor
from app.services.competitor_signal_service import build_signals
from app.services.country_query_service import domain_period_quality, float_value, optional_float, ratio_value


def quality_warning(session: Session, domain_id: int, date_from: date, date_to: date) -> str | None:
    """Build quality warning.
    Args:
        session (Session): Database session.
        domain_id (int): Domain identifier.
        date_from (date): Period start date.
        date_to (date): Period end date."""
    status = domain_period_quality(session, domain_id, date_from, date_to)
    if status == 'failed':
        raise HTTPException(status_code=409, detail='Competitor analysis cannot run on failed quality data.')
    if status == 'warning':
        return 'Competitor analysis is based on data with quality warnings.'
    if status == 'unknown':
        return 'No quality context found for selected competitor and period.'
    return None


def trend_rows(session: Session, domain_id: int, date_from: date, date_to: date) -> list[dict[str, object]]:
    """Build trend rows.
    Args:
        session (Session): Database session.
        domain_id (int): Domain identifier.
        date_from (date): Period start date.
        date_to (date): Period end date."""
    result = session.execute(
        text(
            """
            SELECT
                date,
                SUM(traffic) AS traffic,
                SUM(desktop_traffic) AS desktop_traffic,
                SUM(mobile_traffic) AS mobile_traffic,
                SUM(traffic_no_bounce) AS traffic_no_bounce,
                SUM(traffic_bounce) AS traffic_bounce
            FROM fact_domain_country_daily
            WHERE domain_id = :domain_id
              AND date BETWEEN :date_from AND :date_to
            GROUP BY date
            ORDER BY date
            """,
        ),
        {'domain_id': domain_id, 'date_from': date_from, 'date_to': date_to},
    )
    rows = [
        {
            'date': row.date,
            'traffic': float_value(row.traffic),
            'desktop_traffic': optional_float(row.desktop_traffic),
            'mobile_traffic': optional_float(row.mobile_traffic),
            'traffic_no_bounce': optional_float(row.traffic_no_bounce),
            'traffic_bounce': optional_float(row.traffic_bounce),
        }
        for row in result
    ]
    return rows


def summary_metrics(items: list[dict[str, object]]) -> CompetitorSummaryMetrics:
    """Build summary metrics.
    Args:
        items (list[dict[str, object]]): Country items."""
    total_traffic = sum(float_value(item.get('traffic')) for item in items)
    top_item = items[0] if items else {}
    desktop_traffic = sum(float_value(item.get('desktop_share')) * float_value(item.get('traffic')) for item in items)
    mobile_traffic = sum(float_value(item.get('mobile_share')) * float_value(item.get('traffic')) for item in items)
    no_bounce = sum(float_value(item.get('no_bounce_share')) * float_value(item.get('traffic')) for item in items)
    bounce = total_traffic - no_bounce if total_traffic else 0
    metrics = CompetitorSummaryMetrics(
        total_traffic=total_traffic,
        active_countries_count=len(items),
        top_country=top_item.get('country_name_en'),
        top_country_traffic=optional_float(top_item.get('traffic')),
        top_country_share=optional_float(top_item.get('traffic_share_in_domain')),
        desktop_traffic=desktop_traffic,
        mobile_traffic=mobile_traffic,
        desktop_share=ratio_value(desktop_traffic, desktop_traffic + mobile_traffic),
        mobile_share=ratio_value(mobile_traffic, desktop_traffic + mobile_traffic),
        traffic_no_bounce=no_bounce,
        traffic_bounce=bounce,
        no_bounce_share=ratio_value(no_bounce, total_traffic),
        bounce_share=ratio_value(bounce, total_traffic),
        avg_bounce_rate=ratio_value(bounce, total_traffic),
    )
    return metrics


def build_competitor_summary(
    session: Session,
    domain_id: int,
    date_from: date,
    date_to: date,
    limit_countries: int,
) -> CompetitorSummary:
    """Build competitor summary.
    Args:
        session (Session): Database session.
        domain_id (int): Domain identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        limit_countries (int): Country limit."""
    warning = quality_warning(session, domain_id, date_from, date_to)
    competitor_data = get_competitor(session, domain_id)
    if competitor_data is None:
        raise HTTPException(status_code=404, detail='Competitor not found.')
    competitor = CompetitorItem(**competitor_data)
    rows = country_rows(session, domain_id, date_from, date_to)
    if not rows:
        raise HTTPException(status_code=404, detail='NO_DATA_FOR_COMPETITOR')
    items = build_countries(rows, date_from, date_to)
    save_country_metrics(session, domain_id, competitor.company_id, date_from, date_to, items)
    metrics = summary_metrics(items)
    signals = build_signals(items)
    result = CompetitorSummary(
        competitor=competitor,
        period={'date_from': date_from, 'date_to': date_to, 'days_count': (date_to - date_from).days + 1},
        summary=metrics,
        top_countries=items[:limit_countries],
        signals=signals,
        daily_trend=trend_rows(session, domain_id, date_from, date_to),
        generated_summary=build_summary(competitor, metrics),
        quality_warning=warning,
    )
    return result
