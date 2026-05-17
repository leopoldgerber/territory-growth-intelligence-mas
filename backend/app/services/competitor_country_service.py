from datetime import date, timedelta

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.country_query_service import float_value, optional_float, ratio_value


def quality_label(no_bounce_share: float | None, bounce_rate: float | None) -> str:
    """Build quality label.
    Args:
        no_bounce_share (float | None): No-bounce share.
        bounce_rate (float | None): Bounce rate."""
    if no_bounce_share is not None and bounce_rate is not None and no_bounce_share >= 0.7 and bounce_rate <= 0.35:
        return 'strong'
    if no_bounce_share is not None and no_bounce_share >= 0.5:
        return 'medium'
    return 'weak'


def country_role(share: float | None, stability: float | None) -> str:
    """Build country role.
    Args:
        share (float | None): Traffic share.
        stability (float | None): Stability score."""
    if share is not None and stability is not None and share >= 0.1 and stability >= 0.7:
        return 'anchor'
    if (share is not None and 0 < share < 0.03) or (stability is not None and stability < 0.35):
        return 'peripheral'
    return 'normal'


def growth_windows(date_from: date, date_to: date) -> tuple[date, date, date, date]:
    """Build growth windows.
    Args:
        date_from (date): Period start date.
        date_to (date): Period end date."""
    days_count = (date_to - date_from).days + 1
    window_days = max(1, int(days_count * 0.2))
    if days_count < 10:
        window_days = max(1, int(days_count / 2))
    first_end = date_from + timedelta(days=window_days - 1)
    last_start = date_to - timedelta(days=window_days - 1)
    return date_from, first_end, last_start, date_to


def country_rows(session: Session, domain_id: int, date_from: date, date_to: date) -> list[dict[str, object]]:
    """Get country rows.
    Args:
        session (Session): Database session.
        domain_id (int): Domain identifier.
        date_from (date): Period start date.
        date_to (date): Period end date."""
    first_start, first_end, last_start, last_end = growth_windows(date_from, date_to)
    result = session.execute(
        text(
            """
            SELECT
                facts.country_id,
                facts.region_id,
                countries.country_name_en,
                countries.country_name_ru,
                regions.region_name AS region_name_en,
                SUM(facts.traffic) AS traffic,
                SUM(facts.desktop_traffic) AS desktop_traffic,
                SUM(facts.mobile_traffic) AS mobile_traffic,
                SUM(facts.traffic_no_bounce) AS traffic_no_bounce,
                SUM(facts.traffic_bounce) AS traffic_bounce,
                AVG(facts.bounce_rate) AS bounce_rate,
                SUM(facts.pages_per_visit * facts.traffic) / NULLIF(SUM(facts.traffic), 0) AS avg_pages_per_visit,
                SUM(facts.avg_visit_duration_seconds * facts.traffic) / NULLIF(SUM(facts.traffic), 0)
                    AS avg_visit_duration_seconds,
                COUNT(DISTINCT facts.date) FILTER (WHERE facts.traffic > 0) AS days_with_traffic,
                SUM(facts.traffic) FILTER (WHERE facts.date BETWEEN :first_start AND :first_end) AS first_traffic,
                SUM(facts.traffic) FILTER (WHERE facts.date BETWEEN :last_start AND :last_end) AS last_traffic,
                MIN(facts.date) FILTER (WHERE facts.traffic > 0) AS first_seen_date,
                MAX(facts.date) FILTER (WHERE facts.traffic > 0) AS last_seen_date
            FROM fact_domain_country_daily AS facts
            JOIN dim_country AS countries ON countries.country_id = facts.country_id
            LEFT JOIN dim_region AS regions ON regions.region_id = facts.region_id
            WHERE facts.domain_id = :domain_id
              AND facts.date BETWEEN :date_from AND :date_to
            GROUP BY facts.country_id, facts.region_id, countries.country_name_en, countries.country_name_ru, regions.region_name
            HAVING SUM(facts.traffic) > 0
            ORDER BY traffic DESC NULLS LAST
            """,
        ),
        {
            'domain_id': domain_id,
            'date_from': date_from,
            'date_to': date_to,
            'first_start': first_start,
            'first_end': first_end,
            'last_start': last_start,
            'last_end': last_end,
        },
    )
    rows = [dict(row._mapping) for row in result]
    return rows


def build_countries(rows: list[dict[str, object]], date_from: date, date_to: date) -> list[dict[str, object]]:
    """Build country items.
    Args:
        rows (list[dict[str, object]]): Country rows.
        date_from (date): Period start date.
        date_to (date): Period end date."""
    total_traffic = sum(float_value(row.get('traffic')) for row in rows)
    days_count = (date_to - date_from).days + 1
    items = []
    for index, row in enumerate(rows, start=1):
        traffic = float_value(row.get('traffic'))
        first_traffic = float_value(row.get('first_traffic'))
        last_traffic = float_value(row.get('last_traffic'))
        growth_rate = ratio_value(last_traffic - first_traffic, first_traffic) if first_traffic > 0 else None
        stability = ratio_value(float_value(row.get('days_with_traffic')), days_count)
        desktop = float_value(row.get('desktop_traffic'))
        mobile = float_value(row.get('mobile_traffic'))
        no_bounce = float_value(row.get('traffic_no_bounce'))
        bounce = float_value(row.get('traffic_bounce'))
        share = ratio_value(traffic, total_traffic)
        no_bounce_share = ratio_value(no_bounce, traffic)
        bounce_rate = ratio_value(bounce, traffic) or optional_float(row.get('bounce_rate'))
        role = country_role(share, stability)
        signal = None
        if growth_rate is not None and growth_rate >= 0.3:
            signal = 'growing'
        if growth_rate is not None and growth_rate <= -0.3:
            signal = 'declining'
        first_seen = row.get('first_seen_date')
        last_seen = row.get('last_seen_date')
        if first_seen and (first_seen - date_from).days > max(1, int(days_count * 0.5)):
            signal = 'new'
        if last_seen and (last_seen - date_from).days < int(days_count * 0.7):
            signal = 'abandoned'
        items.append(
            {
                'rank': index,
                'country_id': int(row['country_id']),
                'country_name_en': row['country_name_en'],
                'country_name_ru': row.get('country_name_ru'),
                'region_name_en': row.get('region_name_en'),
                'traffic': traffic,
                'traffic_share_in_domain': share,
                'growth_rate': growth_rate,
                'presence_stability_score': stability,
                'desktop_share': ratio_value(desktop, desktop + mobile),
                'mobile_share': ratio_value(mobile, desktop + mobile),
                'bounce_rate': bounce_rate,
                'no_bounce_share': no_bounce_share,
                'country_role': role,
                'quality_label': quality_label(no_bounce_share, bounce_rate),
                'signal': signal,
                'region_id': row.get('region_id'),
            },
        )
    return items


def save_country_metrics(
    session: Session,
    domain_id: int,
    company_id: int | None,
    date_from: date,
    date_to: date,
    items: list[dict[str, object]],
) -> int:
    """Save competitor country metrics.
    Args:
        session (Session): Database session.
        domain_id (int): Domain identifier.
        company_id (int | None): Company identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        items (list[dict[str, object]]): Country items."""
    count = 0
    for item in items:
        session.execute(
            text(
                """
                INSERT INTO metric_competitor_country_period (
                    domain_id, company_id, country_id, region_id, period_start, period_end,
                    total_traffic, traffic_share_in_domain, growth_rate, presence_stability_score,
                    desktop_share, mobile_share, bounce_rate, no_bounce_share, quality_label, country_role,
                    is_new_market_signal, is_abandoned_market_signal, calculation_version
                )
                VALUES (
                    :domain_id, :company_id, :country_id, :region_id, :period_start, :period_end,
                    :total_traffic, :traffic_share_in_domain, :growth_rate, :presence_stability_score,
                    :desktop_share, :mobile_share, :bounce_rate, :no_bounce_share, :quality_label, :country_role,
                    :is_new_market_signal, :is_abandoned_market_signal, 'v1'
                )
                ON CONFLICT (domain_id, country_id, period_start, period_end, calculation_version) DO UPDATE
                SET total_traffic = EXCLUDED.total_traffic,
                    traffic_share_in_domain = EXCLUDED.traffic_share_in_domain,
                    growth_rate = EXCLUDED.growth_rate,
                    presence_stability_score = EXCLUDED.presence_stability_score,
                    desktop_share = EXCLUDED.desktop_share,
                    mobile_share = EXCLUDED.mobile_share,
                    bounce_rate = EXCLUDED.bounce_rate,
                    no_bounce_share = EXCLUDED.no_bounce_share,
                    quality_label = EXCLUDED.quality_label,
                    country_role = EXCLUDED.country_role,
                    is_new_market_signal = EXCLUDED.is_new_market_signal,
                    is_abandoned_market_signal = EXCLUDED.is_abandoned_market_signal,
                    calculated_at = now()
                """,
            ),
            {
                'domain_id': domain_id,
                'company_id': company_id,
                'country_id': item['country_id'],
                'region_id': item.get('region_id'),
                'period_start': date_from,
                'period_end': date_to,
                'total_traffic': item['traffic'],
                'traffic_share_in_domain': item.get('traffic_share_in_domain'),
                'growth_rate': item.get('growth_rate'),
                'presence_stability_score': item.get('presence_stability_score'),
                'desktop_share': item.get('desktop_share'),
                'mobile_share': item.get('mobile_share'),
                'bounce_rate': item.get('bounce_rate'),
                'no_bounce_share': item.get('no_bounce_share'),
                'quality_label': item.get('quality_label'),
                'country_role': item.get('country_role'),
                'is_new_market_signal': item.get('signal') == 'new',
                'is_abandoned_market_signal': item.get('signal') == 'abandoned',
            },
        )
        count += 1
    session.commit()
    return count
