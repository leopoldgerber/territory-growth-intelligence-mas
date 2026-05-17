from datetime import date

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.country import CountryItem, CountryMetricValues, CountryMetricsResponse, MetricCalculation, MetricLeader, PeriodInfo
from app.services.country_competitor_service import build_competitors, competitor_rows
from app.services.country_query_service import float_value, get_country, optional_float, period_quality, ratio_value
from app.services.engagement_score_service import engagement_score
from app.services.market_concentration_service import hhi_score, top_share
from app.services.volatility_service import volatility_score


METRIC_COLUMNS = [
    'total_competitor_traffic',
    'active_competitors_count',
    'leader_domain_id',
    'leader_company_id',
    'leader_traffic',
    'leader_share',
    'top_3_share',
    'market_concentration_hhi',
    'desktop_traffic',
    'mobile_traffic',
    'desktop_share',
    'mobile_share',
    'traffic_no_bounce',
    'traffic_bounce',
    'no_bounce_share',
    'bounce_share',
    'avg_bounce_rate',
    'avg_pages_per_visit',
    'avg_visit_duration_seconds',
    'engagement_score',
    'market_volatility_score',
]


def quality_guard(session: Session, country_id: int, date_from: date, date_to: date) -> str:
    """Check quality status.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date."""
    status = period_quality(session, country_id, date_from, date_to)
    if status == 'failed':
        raise HTTPException(
            status_code=409,
            detail='Metrics cannot be calculated because the latest dataset has failed quality checks.',
        )
    return status


def metric_warning(status: str) -> str | None:
    """Build metric warning.
    Args:
        status (str): Data quality status."""
    if status == 'warning':
        return 'Metrics were calculated from data with quality warnings.'
    if status == 'unknown':
        return 'No quality context found for selected country and period.'
    return None


def region_id(session: Session, country_id: int) -> int | None:
    """Get region identifier.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier."""
    result = session.execute(
        text('SELECT region_id FROM dim_country WHERE country_id = :country_id'),
        {'country_id': country_id},
    )
    value = result.scalar_one_or_none()
    identifier = None if value is None else int(value)
    return identifier


def metric_values(rows: list[dict[str, object]], volatility: float | None) -> dict[str, object]:
    """Build metric values.
    Args:
        rows (list[dict[str, object]]): Competitor rows.
        volatility (float | None): Volatility score."""
    traffic_values = [float_value(row.get('traffic')) for row in rows]
    total_traffic = sum(traffic_values)
    competitors = build_competitors(rows, total_traffic)
    leader = competitors[0] if competitors else {}
    desktop_traffic = sum(float_value(row.get('desktop_traffic')) for row in rows)
    mobile_traffic = sum(float_value(row.get('mobile_traffic')) for row in rows)
    traffic_no_bounce = sum(float_value(row.get('traffic_no_bounce')) for row in rows)
    traffic_bounce = sum(float_value(row.get('traffic_bounce')) for row in rows)
    weighted_pages = ratio_value(
        sum(float_value(row.get('avg_pages_per_visit')) * float_value(row.get('traffic')) for row in rows),
        total_traffic,
    )
    weighted_duration = ratio_value(
        sum(float_value(row.get('avg_visit_duration_seconds')) * float_value(row.get('traffic')) for row in rows),
        total_traffic,
    )
    bounce_rate = ratio_value(traffic_bounce, total_traffic)
    no_bounce_share = ratio_value(traffic_no_bounce, total_traffic)
    values = {
        'total_competitor_traffic': total_traffic,
        'active_competitors_count': len([traffic for traffic in traffic_values if traffic > 0]),
        'leader_domain_id': leader.get('domain_id'),
        'leader_company_id': leader.get('company_id'),
        'leader_traffic': leader.get('traffic'),
        'leader_share': ratio_value(optional_float(leader.get('traffic')), total_traffic),
        'top_3_share': top_share(traffic_values, 3),
        'market_concentration_hhi': hhi_score(traffic_values),
        'desktop_traffic': desktop_traffic,
        'mobile_traffic': mobile_traffic,
        'desktop_share': ratio_value(desktop_traffic, desktop_traffic + mobile_traffic),
        'mobile_share': ratio_value(mobile_traffic, desktop_traffic + mobile_traffic),
        'traffic_no_bounce': traffic_no_bounce,
        'traffic_bounce': traffic_bounce,
        'no_bounce_share': no_bounce_share,
        'bounce_share': ratio_value(traffic_bounce, total_traffic),
        'avg_bounce_rate': bounce_rate,
        'avg_pages_per_visit': weighted_pages,
        'avg_visit_duration_seconds': weighted_duration,
        'engagement_score': engagement_score(no_bounce_share, bounce_rate, weighted_pages, weighted_duration),
        'market_volatility_score': volatility,
    }
    return values


def daily_source(
    session: Session,
    country_id: int,
    date_from: date,
    date_to: date,
) -> dict[date, list[dict[str, object]]]:
    """Build daily source rows.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date."""
    result = session.execute(
        text(
            """
            SELECT
                facts.date,
                facts.domain_id,
                facts.company_id,
                SUM(facts.traffic) AS traffic,
                SUM(facts.desktop_traffic) AS desktop_traffic,
                SUM(facts.mobile_traffic) AS mobile_traffic,
                SUM(facts.traffic_no_bounce) AS traffic_no_bounce,
                SUM(facts.traffic_bounce) AS traffic_bounce,
                SUM(facts.pages_per_visit * facts.traffic) / NULLIF(SUM(facts.traffic), 0) AS avg_pages_per_visit,
                SUM(facts.avg_visit_duration_seconds * facts.traffic) / NULLIF(SUM(facts.traffic), 0)
                    AS avg_visit_duration_seconds
            FROM fact_domain_country_daily AS facts
            WHERE facts.country_id = :country_id
              AND facts.date BETWEEN :date_from AND :date_to
            GROUP BY facts.date, facts.domain_id, facts.company_id
            HAVING SUM(facts.traffic) > 0
            ORDER BY facts.date
            """,
        ),
        {'country_id': country_id, 'date_from': date_from, 'date_to': date_to},
    )
    grouped_rows: dict[date, list[dict[str, object]]] = {}
    for row in result:
        grouped_rows.setdefault(row.date, []).append(dict(row._mapping))
    return grouped_rows


def upsert_daily(
    session: Session,
    country_id: int,
    date_value: date,
    values: dict[str, object],
    quality_status: str,
    calculation_version: str,
) -> int:
    """Upsert daily metrics.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_value (date): Metric date.
        values (dict[str, object]): Metric values.
        quality_status (str): Quality status.
        calculation_version (str): Calculation version."""
    date_id = int(date_value.strftime('%Y%m%d'))
    params = {
        **values,
        'date_id': date_id,
        'date': date_value,
        'country_id': country_id,
        'region_id': region_id(session, country_id),
        'quality_status': quality_status,
        'calculation_version': calculation_version,
    }
    assignments = ', '.join([f'{column} = EXCLUDED.{column}' for column in METRIC_COLUMNS])
    session.execute(
        text(
            f"""
            INSERT INTO metric_country_daily (
                date_id, date, country_id, region_id, {', '.join(METRIC_COLUMNS)}, quality_status, calculation_version
            )
            VALUES (
                :date_id, :date, :country_id, :region_id,
                {', '.join([f':{column}' for column in METRIC_COLUMNS])},
                :quality_status, :calculation_version
            )
            ON CONFLICT (date_id, country_id, calculation_version) DO UPDATE
            SET {assignments}, quality_status = EXCLUDED.quality_status, calculated_at = now()
            """,
        ),
        params,
    )
    return date_id


def upsert_period(
    session: Session,
    country_id: int,
    date_from: date,
    date_to: date,
    values: dict[str, object],
    quality_status: str,
    calculation_version: str,
) -> int:
    """Upsert period metrics.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        values (dict[str, object]): Metric values.
        quality_status (str): Quality status.
        calculation_version (str): Calculation version."""
    params = {
        **values,
        'country_id': country_id,
        'region_id': region_id(session, country_id),
        'period_start': date_from,
        'period_end': date_to,
        'days_count': (date_to - date_from).days + 1,
        'data_quality_status': quality_status,
        'calculation_version': calculation_version,
    }
    assignments = ', '.join([f'{column} = EXCLUDED.{column}' for column in METRIC_COLUMNS])
    result = session.execute(
        text(
            f"""
            INSERT INTO metric_country_period (
                country_id, region_id, period_start, period_end, days_count,
                {', '.join(METRIC_COLUMNS)}, data_quality_status, calculation_version
            )
            VALUES (
                :country_id, :region_id, :period_start, :period_end, :days_count,
                {', '.join([f':{column}' for column in METRIC_COLUMNS])},
                :data_quality_status, :calculation_version
            )
            ON CONFLICT (country_id, period_start, period_end, calculation_version) DO UPDATE
            SET {assignments}, data_quality_status = EXCLUDED.data_quality_status, calculated_at = now()
            RETURNING country_period_metric_id
            """,
        ),
        params,
    )
    metric_id = int(result.scalar_one())
    return metric_id


def recalculate_metrics(
    session: Session,
    country_id: int,
    date_from: date,
    date_to: date,
    calculation_version: str = 'v1',
) -> dict[str, object]:
    """Recalculate country metrics.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        calculation_version (str): Calculation version."""
    quality_status = quality_guard(session, country_id, date_from, date_to)
    grouped_rows = daily_source(session, country_id, date_from, date_to)
    daily_traffic = []
    leader_ids = []
    for date_value, rows in grouped_rows.items():
        daily_values = metric_values(rows, None)
        upsert_daily(session, country_id, date_value, daily_values, quality_status, calculation_version)
        daily_traffic.append(float_value(daily_values.get('total_competitor_traffic')))
        leader_ids.append(daily_values.get('leader_domain_id'))
    period_rows = competitor_rows(session, country_id, date_from, date_to)
    if not period_rows:
        raise HTTPException(status_code=404, detail='NO_DATA_FOR_COUNTRY_PERIOD')
    volatility = volatility_score(daily_traffic, leader_ids)
    period_values = metric_values(period_rows, volatility)
    upsert_period(session, country_id, date_from, date_to, period_values, quality_status, calculation_version)
    session.commit()
    return {'values': period_values, 'quality_status': quality_status}


def row_metrics(row: dict[str, object]) -> CountryMetricValues:
    """Build metric schema.
    Args:
        row (dict[str, object]): Metric row."""
    leader = MetricLeader(
        domain_id=row.get('leader_domain_id'),
        domain=row.get('leader_domain'),
        company_id=row.get('leader_company_id'),
        company_name=row.get('leader_company'),
        traffic=optional_float(row.get('leader_traffic')),
        share=optional_float(row.get('leader_share')),
    )
    metrics = CountryMetricValues(
        total_competitor_traffic=optional_float(row.get('total_competitor_traffic')),
        active_competitors_count=row.get('active_competitors_count'),
        leader=leader,
        leader_share=optional_float(row.get('leader_share')),
        top_3_share=optional_float(row.get('top_3_share')),
        market_concentration_hhi=optional_float(row.get('market_concentration_hhi')),
        desktop_share=optional_float(row.get('desktop_share')),
        mobile_share=optional_float(row.get('mobile_share')),
        bounce_share=optional_float(row.get('bounce_share')),
        no_bounce_share=optional_float(row.get('no_bounce_share')),
        avg_bounce_rate=optional_float(row.get('avg_bounce_rate')),
        avg_pages_per_visit=optional_float(row.get('avg_pages_per_visit')),
        avg_visit_duration_seconds=optional_float(row.get('avg_visit_duration_seconds')),
        engagement_score=optional_float(row.get('engagement_score')),
        market_volatility_score=optional_float(row.get('market_volatility_score')),
    )
    return metrics


def get_metrics(
    session: Session,
    country_id: int,
    date_from: date,
    date_to: date,
    calculation_version: str,
    recalculate_if_missing: bool,
) -> CountryMetricsResponse:
    """Get country metrics.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        calculation_version (str): Calculation version.
        recalculate_if_missing (bool): Recalculate missing metrics flag."""
    result = session.execute(
        text(
            """
            SELECT
                metrics.*,
                domains.domain AS leader_domain,
                companies.company_name AS leader_company,
                metrics.calculated_at::text AS calculated_at
            FROM metric_country_period AS metrics
            LEFT JOIN dim_domain AS domains ON domains.domain_id = metrics.leader_domain_id
            LEFT JOIN dim_company AS companies ON companies.company_id = metrics.leader_company_id
            WHERE metrics.country_id = :country_id
              AND metrics.period_start = :date_from
              AND metrics.period_end = :date_to
              AND metrics.calculation_version = :calculation_version
            """,
        ),
        {
            'country_id': country_id,
            'date_from': date_from,
            'date_to': date_to,
            'calculation_version': calculation_version,
        },
    )
    row = result.first()
    if row is None and recalculate_if_missing:
        recalculate_metrics(session, country_id, date_from, date_to, calculation_version)
        return get_metrics(session, country_id, date_from, date_to, calculation_version, False)
    if row is None:
        raise HTTPException(status_code=404, detail='METRICS_NOT_FOUND')
    country = CountryItem(**get_country(session, country_id))
    row_data = dict(row._mapping)
    response = CountryMetricsResponse(
        country=country,
        period=PeriodInfo(date_from=date_from, date_to=date_to, days_count=(date_to - date_from).days + 1),
        metrics=row_metrics(row_data),
        calculation=MetricCalculation(
            calculation_version=calculation_version,
            calculated_at=row_data.get('calculated_at'),
            data_quality_status=row_data.get('data_quality_status'),
        ),
        warning=metric_warning(str(row_data.get('data_quality_status') or 'unknown')),
    )
    return response


def daily_metrics(
    session: Session,
    country_id: int,
    date_from: date,
    date_to: date,
) -> list[dict[str, object]]:
    """Get daily metrics.
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
                total_competitor_traffic,
                active_competitors_count,
                leader_share,
                top_3_share,
                market_concentration_hhi,
                engagement_score,
                market_volatility_score
            FROM metric_country_daily
            WHERE country_id = :country_id
              AND date BETWEEN :date_from AND :date_to
            ORDER BY date
            """,
        ),
        {'country_id': country_id, 'date_from': date_from, 'date_to': date_to},
    )
    rows = [dict(row._mapping) for row in result]
    return rows
