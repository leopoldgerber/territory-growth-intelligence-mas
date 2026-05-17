from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.country import CountryItem, CountrySummary, CountrySummaryMetrics, PeriodInfo
from app.services.country_competitor_service import build_competitors, competitor_rows
from app.services.country_query_service import float_value, optional_float, period_quality, ratio_value
from app.services.country_summary_text_service import build_summary


def aggregate_market(
    session: Session,
    country_id: int,
    date_from: date,
    date_to: date,
) -> dict[str, object]:
    """Aggregate market metrics.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date."""
    result = session.execute(
        text(
            """
            SELECT
                SUM(traffic) AS total_traffic,
                COUNT(DISTINCT domain_id) FILTER (WHERE traffic > 0) AS active_competitors,
                SUM(desktop_traffic) AS desktop_traffic,
                SUM(mobile_traffic) AS mobile_traffic,
                SUM(traffic_no_bounce) AS traffic_no_bounce,
                SUM(traffic_bounce) AS traffic_bounce,
                AVG(bounce_rate) AS avg_bounce_rate,
                SUM(pages_per_visit * traffic) / NULLIF(SUM(traffic), 0) AS avg_pages_per_visit,
                SUM(avg_visit_duration_seconds * traffic) / NULLIF(SUM(traffic), 0) AS avg_visit_duration_seconds
            FROM fact_domain_country_daily
            WHERE country_id = :country_id
              AND date BETWEEN :date_from AND :date_to
            """,
        ),
        {'country_id': country_id, 'date_from': date_from, 'date_to': date_to},
    )
    row = result.one()
    metrics = dict(row._mapping)
    return metrics


def trend_rows(
    session: Session,
    country_id: int,
    date_from: date,
    date_to: date,
) -> list[dict[str, object]]:
    """Get trend rows.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
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
            WHERE country_id = :country_id
              AND date BETWEEN :date_from AND :date_to
            GROUP BY date
            ORDER BY date
            """,
        ),
        {'country_id': country_id, 'date_from': date_from, 'date_to': date_to},
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


def quality_warning(session: Session, country_id: int, date_from: date, date_to: date) -> str | None:
    """Build quality warning.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date."""
    status = period_quality(session, country_id, date_from, date_to)
    if status == 'failed':
        return 'Selected data has critical quality errors. Country summary may be unreliable.'
    if status == 'warning':
        return 'Selected data has quality warnings. Use the summary with caution.'
    if status == 'unknown':
        return 'No quality context found for selected country and period.'
    return None


def build_metrics(market: dict[str, object], competitors: list[dict[str, object]]) -> CountrySummaryMetrics:
    """Build summary metrics.
    Args:
        market (dict[str, object]): Market aggregate values.
        competitors (list[dict[str, object]]): Competitor items."""
    total_traffic = float_value(market.get('total_traffic'))
    desktop_traffic = optional_float(market.get('desktop_traffic'))
    mobile_traffic = optional_float(market.get('mobile_traffic'))
    traffic_no_bounce = optional_float(market.get('traffic_no_bounce'))
    traffic_bounce = optional_float(market.get('traffic_bounce'))
    device_total = float_value(desktop_traffic) + float_value(mobile_traffic)
    leader = competitors[0] if competitors else {}
    top_3_traffic = sum(float_value(competitor.get('traffic')) for competitor in competitors[:3])
    metrics = CountrySummaryMetrics(
        total_competitor_traffic=total_traffic,
        active_competitors_count=int(market.get('active_competitors') or 0),
        leader_domain=leader.get('domain'),
        leader_company=leader.get('company_name'),
        leader_traffic=optional_float(leader.get('traffic')),
        leader_share=ratio_value(optional_float(leader.get('traffic')), total_traffic),
        top_3_share=ratio_value(top_3_traffic, total_traffic),
        desktop_traffic=desktop_traffic,
        mobile_traffic=mobile_traffic,
        desktop_share=ratio_value(desktop_traffic, device_total),
        mobile_share=ratio_value(mobile_traffic, device_total),
        traffic_no_bounce=traffic_no_bounce,
        traffic_bounce=traffic_bounce,
        no_bounce_share=ratio_value(traffic_no_bounce, total_traffic),
        bounce_share=ratio_value(traffic_bounce, total_traffic),
        avg_bounce_rate=ratio_value(traffic_bounce, total_traffic) or optional_float(market.get('avg_bounce_rate')),
        avg_pages_per_visit=optional_float(market.get('avg_pages_per_visit')),
        avg_visit_duration_seconds=optional_float(market.get('avg_visit_duration_seconds')),
    )
    return metrics


def build_country_summary(
    session: Session,
    country: dict[str, object],
    date_from: date,
    date_to: date,
    limit_competitors: int,
) -> CountrySummary:
    """Build country summary.
    Args:
        session (Session): Database session.
        country (dict[str, object]): Country metadata.
        date_from (date): Period start date.
        date_to (date): Period end date.
        limit_competitors (int): Top competitors limit."""
    country_item = CountryItem(**country)
    market = aggregate_market(session, country_item.country_id, date_from, date_to)
    rows = competitor_rows(session, country_item.country_id, date_from, date_to)
    total_traffic = float_value(market.get('total_traffic'))
    competitors = build_competitors(rows, total_traffic)
    metrics = build_metrics(market, competitors)
    period = PeriodInfo(date_from=date_from, date_to=date_to, days_count=(date_to - date_from).days + 1)
    summary = CountrySummary(
        country=country_item,
        period=period,
        summary=metrics,
        top_competitors=competitors[:limit_competitors],
        daily_trend=trend_rows(session, country_item.country_id, date_from, date_to),
        generated_summary=build_summary(country_item, metrics),
        quality_warning=quality_warning(session, country_item.country_id, date_from, date_to),
    )
    return summary
