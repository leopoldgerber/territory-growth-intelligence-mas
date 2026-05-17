from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.country_query_service import float_value, optional_float, ratio_value


SORT_COLUMNS = {
    'traffic': 'traffic',
    'share': 'traffic_share',
    'bounce_rate': 'bounce_rate',
    'no_bounce': 'traffic_no_bounce',
}


def competitor_rows(
    session: Session,
    country_id: int,
    date_from: date,
    date_to: date,
) -> list[dict[str, object]]:
    """Get competitor rows.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date."""
    result = session.execute(
        text(
            """
            SELECT
                facts.domain_id,
                domains.domain,
                facts.company_id,
                companies.company_name,
                SUM(facts.traffic) AS traffic,
                SUM(facts.desktop_traffic) AS desktop_traffic,
                SUM(facts.mobile_traffic) AS mobile_traffic,
                SUM(facts.traffic_no_bounce) AS traffic_no_bounce,
                SUM(facts.traffic_bounce) AS traffic_bounce,
                AVG(facts.bounce_rate) AS bounce_rate,
                SUM(facts.pages_per_visit * facts.traffic) / NULLIF(SUM(facts.traffic), 0) AS avg_pages_per_visit,
                SUM(facts.avg_visit_duration_seconds * facts.traffic) / NULLIF(SUM(facts.traffic), 0)
                    AS avg_visit_duration_seconds
            FROM fact_domain_country_daily AS facts
            JOIN dim_domain AS domains ON domains.domain_id = facts.domain_id
            LEFT JOIN dim_company AS companies ON companies.company_id = facts.company_id
            WHERE facts.country_id = :country_id
              AND facts.date BETWEEN :date_from AND :date_to
            GROUP BY facts.domain_id, domains.domain, facts.company_id, companies.company_name
            HAVING SUM(facts.traffic) > 0
            """,
        ),
        {'country_id': country_id, 'date_from': date_from, 'date_to': date_to},
    )
    rows = [dict(row._mapping) for row in result]
    return rows


def build_competitors(rows: list[dict[str, object]], total_traffic: float) -> list[dict[str, object]]:
    """Build competitor items.
    Args:
        rows (list[dict[str, object]]): Competitor rows.
        total_traffic (float): Total traffic."""
    competitors = []
    sorted_rows = sorted(rows, key=lambda row: float_value(row.get('traffic')), reverse=True)
    for index, row in enumerate(sorted_rows, start=1):
        traffic = float_value(row.get('traffic'))
        desktop_traffic = optional_float(row.get('desktop_traffic'))
        mobile_traffic = optional_float(row.get('mobile_traffic'))
        traffic_no_bounce = optional_float(row.get('traffic_no_bounce'))
        traffic_bounce = optional_float(row.get('traffic_bounce'))
        device_total = float_value(desktop_traffic) + float_value(mobile_traffic)
        competitor = {
            'rank': index,
            'domain_id': int(row['domain_id']),
            'domain': row['domain'],
            'company_id': row.get('company_id'),
            'company_name': row.get('company_name'),
            'traffic': traffic,
            'traffic_share': ratio_value(traffic, total_traffic),
            'desktop_traffic': desktop_traffic,
            'mobile_traffic': mobile_traffic,
            'desktop_share': ratio_value(desktop_traffic, device_total),
            'mobile_share': ratio_value(mobile_traffic, device_total),
            'bounce_rate': optional_float(row.get('bounce_rate')),
            'traffic_no_bounce': traffic_no_bounce,
            'traffic_bounce': traffic_bounce,
            'no_bounce_share': ratio_value(traffic_no_bounce, traffic),
        }
        competitors.append(competitor)
    return competitors


def list_competitors(
    session: Session,
    country_id: int,
    date_from: date,
    date_to: date,
    limit: int,
    sort_by: str,
    sort_order: str,
) -> dict[str, object]:
    """List competitors.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        limit (int): Result limit.
        sort_by (str): Sort column.
        sort_order (str): Sort order."""
    rows = competitor_rows(session, country_id, date_from, date_to)
    total_traffic = sum(float_value(row.get('traffic')) for row in rows)
    competitors = build_competitors(rows, total_traffic)
    sort_column = SORT_COLUMNS.get(sort_by, 'traffic')
    reverse_order = sort_order != 'asc'
    sorted_competitors = sorted(
        competitors,
        key=lambda competitor: competitor.get(sort_column) or 0,
        reverse=reverse_order,
    )
    for index, competitor in enumerate(sorted_competitors, start=1):
        competitor['rank'] = index
    return {'items': sorted_competitors[:limit], 'total': len(sorted_competitors)}
