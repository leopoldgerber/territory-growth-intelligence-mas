from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.channel import (
    ChannelMetric,
    ChannelPeriod,
    ChannelScope,
    ChannelSummaryMetrics,
    ChannelSummaryResponse,
    ChannelTrendItem,
    DominantChannel,
)
from app.services.channel_estimator_service import estimate_channels
from app.services.channel_scope_service import resolve_scope
from app.services.country_query_service import channel_scope_quality, float_value, ratio_value


def quality_warning(
    session: Session,
    country_id: int | None,
    domain_id: int | None,
    date_from: date,
    date_to: date,
) -> str | None:
    """Build quality warning.
    Args:
        session (Session): Database session.
        country_id (int | None): Country identifier.
        domain_id (int | None): Domain identifier.
        date_from (date): Period start date.
        date_to (date): Period end date."""
    status = channel_scope_quality(session, country_id, domain_id, date_from, date_to)
    if status == 'failed':
        raise HTTPException(status_code=409, detail='Channel analysis cannot run on failed quality data.')
    if status == 'warning':
        return 'Channel analysis is based on data with quality warnings.'
    if status == 'unknown':
        return 'No quality context found for selected channel scope.'
    return None


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


def direct_channels(
    session: Session,
    scope: ChannelScope,
    date_from: date,
    date_to: date,
) -> list[dict[str, object]]:
    """Get direct channel rows.
    Args:
        session (Session): Database session.
        scope (ChannelScope): Channel scope.
        date_from (date): Period start date.
        date_to (date): Period end date."""
    filters = ['facts.date BETWEEN :date_from AND :date_to']
    params: dict[str, object] = {'date_from': date_from, 'date_to': date_to}
    if scope.domain_id is not None:
        filters.append('facts.domain_id = :domain_id')
        params['domain_id'] = scope.domain_id
    where_clause = ' AND '.join(filters)
    result = session.execute(
        text(
            f"""
            SELECT
                facts.channel_id,
                channels.channel_code,
                channels.channel_name,
                SUM(facts.traffic) AS traffic
            FROM fact_domain_channel_daily AS facts
            JOIN dim_channel AS channels ON channels.channel_id = facts.channel_id
            WHERE {where_clause}
            GROUP BY facts.channel_id, channels.channel_code, channels.channel_name
            ORDER BY traffic DESC NULLS LAST
            """,
        ),
        params,
    )
    rows = [dict(row._mapping) for row in result]
    return rows


def daily_channels(
    session: Session,
    scope: ChannelScope,
    date_from: date,
    date_to: date,
) -> list[dict[str, object]]:
    """Get daily channel rows.
    Args:
        session (Session): Database session.
        scope (ChannelScope): Channel scope.
        date_from (date): Period start date.
        date_to (date): Period end date."""
    filters = ['facts.date BETWEEN :date_from AND :date_to']
    params: dict[str, object] = {'date_from': date_from, 'date_to': date_to}
    if scope.domain_id is not None:
        filters.append('facts.domain_id = :domain_id')
        params['domain_id'] = scope.domain_id
    where_clause = ' AND '.join(filters)
    result = session.execute(
        text(
            f"""
            SELECT
                facts.date,
                facts.channel_id,
                channels.channel_code,
                channels.channel_name,
                SUM(facts.traffic) AS traffic
            FROM fact_domain_channel_daily AS facts
            JOIN dim_channel AS channels ON channels.channel_id = facts.channel_id
            WHERE {where_clause}
            GROUP BY facts.date, facts.channel_id, channels.channel_code, channels.channel_name
            ORDER BY facts.date, channels.channel_code
            """,
        ),
        params,
    )
    rows = [dict(row._mapping) for row in result]
    return rows


def scoped_channels(
    session: Session,
    scope: ChannelScope,
    date_from: date,
    date_to: date,
) -> list[dict[str, object]]:
    """Get scoped channel rows.
    Args:
        session (Session): Database session.
        scope (ChannelScope): Channel scope.
        date_from (date): Period start date.
        date_to (date): Period end date."""
    if scope.country_id is not None:
        rows = estimate_channels(session, scope.country_id, scope.domain_id, date_from, date_to)
        return rows
    rows = direct_channels(session, scope, date_from, date_to)
    return rows


def channel_growth(
    session: Session,
    scope: ChannelScope,
    date_from: date,
    date_to: date,
) -> dict[int, float | None]:
    """Calculate channel growth.
    Args:
        session (Session): Database session.
        scope (ChannelScope): Channel scope.
        date_from (date): Period start date.
        date_to (date): Period end date."""
    if scope.country_id is not None:
        return {}
    first_start, first_end, last_start, last_end = growth_windows(date_from, date_to)
    filters = ['facts.date BETWEEN :date_from AND :date_to']
    params: dict[str, object] = {
        'date_from': date_from,
        'date_to': date_to,
        'first_start': first_start,
        'first_end': first_end,
        'last_start': last_start,
        'last_end': last_end,
    }
    if scope.domain_id is not None:
        filters.append('facts.domain_id = :domain_id')
        params['domain_id'] = scope.domain_id
    where_clause = ' AND '.join(filters)
    result = session.execute(
        text(
            f"""
            SELECT
                channel_id,
                SUM(traffic) FILTER (WHERE date BETWEEN :first_start AND :first_end) AS first_traffic,
                SUM(traffic) FILTER (WHERE date BETWEEN :last_start AND :last_end) AS last_traffic
            FROM fact_domain_channel_daily AS facts
            WHERE {where_clause}
            GROUP BY channel_id
            """,
        ),
        params,
    )
    growth_map = {}
    for row in result:
        first_traffic = float_value(row.first_traffic)
        last_traffic = float_value(row.last_traffic)
        growth_map[int(row.channel_id)] = ratio_value(last_traffic - first_traffic, first_traffic) if first_traffic else None
    return growth_map


def stability_map(
    session: Session,
    scope: ChannelScope,
    date_from: date,
    date_to: date,
) -> dict[int, float | None]:
    """Calculate stability map.
    Args:
        session (Session): Database session.
        scope (ChannelScope): Channel scope.
        date_from (date): Period start date.
        date_to (date): Period end date."""
    if scope.country_id is not None:
        return {}
    days_count = (date_to - date_from).days + 1
    filters = ['facts.date BETWEEN :date_from AND :date_to']
    params: dict[str, object] = {'date_from': date_from, 'date_to': date_to}
    if scope.domain_id is not None:
        filters.append('facts.domain_id = :domain_id')
        params['domain_id'] = scope.domain_id
    where_clause = ' AND '.join(filters)
    result = session.execute(
        text(
            f"""
            SELECT channel_id, COUNT(DISTINCT date) FILTER (WHERE traffic > 0) AS active_days
            FROM fact_domain_channel_daily AS facts
            WHERE {where_clause}
            GROUP BY channel_id
            """,
        ),
        params,
    )
    values = {int(row.channel_id): ratio_value(float_value(row.active_days), days_count) for row in result}
    return values


def channel_profile(share_map: dict[str, float | None], dependency_score: float | None) -> str:
    """Build channel profile.
    Args:
        share_map (dict[str, float | None]): Share by channel code.
        dependency_score (float | None): Dependency score."""
    if (share_map.get('search') or 0) >= 0.5:
        return 'search-heavy'
    if (share_map.get('paid') or 0) >= 0.4:
        return 'paid-heavy'
    if (share_map.get('direct') or 0) >= 0.5:
        return 'direct-heavy'
    if (share_map.get('referral') or 0) >= 0.35:
        return 'referral-heavy'
    if (share_map.get('social') or 0) >= 0.3:
        return 'social-heavy'
    if dependency_score is not None and dependency_score < 0.35:
        return 'diversified'
    return 'mixed'


def channel_hint(metric: ChannelMetric) -> str:
    """Build channel hint.
    Args:
        metric (ChannelMetric): Channel metric."""
    if metric.is_dominant_channel:
        return f'{metric.channel_name} is the dominant acquisition channel.'
    if metric.growth_rate is not None and metric.growth_rate >= 0.2:
        return f'{metric.channel_name} is growing and may deserve a closer campaign review.'
    if metric.stability_score is not None and metric.stability_score >= 0.8:
        return f'{metric.channel_name} is stable across the selected period.'
    return f'{metric.channel_name} is a secondary channel in this selection.'


def build_metrics(
    rows: list[dict[str, object]],
    growth_map: dict[int, float | None],
    stability_values: dict[int, float | None],
) -> list[ChannelMetric]:
    """Build channel metrics.
    Args:
        rows (list[dict[str, object]]): Channel rows.
        growth_map (dict[int, float | None]): Growth values.
        stability_values (dict[int, float | None]): Stability values."""
    total_traffic = sum(float_value(row.get('traffic')) for row in rows)
    dominant_id = int(rows[0]['channel_id']) if rows else None
    metrics = []
    for row in rows:
        channel_id = int(row['channel_id'])
        traffic = float_value(row.get('traffic'))
        traffic_share = ratio_value(traffic, total_traffic)
        role = 'dominant' if channel_id == dominant_id else 'secondary' if traffic_share and traffic_share >= 0.1 else 'weak'
        metric = ChannelMetric(
            channel_id=channel_id,
            channel_code=str(row['channel_code']),
            channel_name=str(row['channel_name']),
            traffic=traffic,
            traffic_share=traffic_share,
            growth_rate=growth_map.get(channel_id),
            stability_score=stability_values.get(channel_id),
            is_dominant_channel=channel_id == dominant_id,
            dependency_score=traffic_share,
            role=role,
            interpretation='',
        )
        metric.interpretation = channel_hint(metric)
        metrics.append(metric)
    return metrics


def summary_values(metrics: list[ChannelMetric]) -> ChannelSummaryMetrics:
    """Build summary values.
    Args:
        metrics (list[ChannelMetric]): Channel metrics."""
    total_traffic = sum(metric.traffic for metric in metrics)
    dominant = next((metric for metric in metrics if metric.is_dominant_channel), None)
    dependency_score = dominant.traffic_share if dominant else None
    share_map = {metric.channel_code: metric.traffic_share for metric in metrics}
    summary = ChannelSummaryMetrics(
        total_channel_traffic=total_traffic,
        dominant_channel=DominantChannel(
            channel_id=dominant.channel_id,
            channel_code=dominant.channel_code,
            channel_name=dominant.channel_name,
            traffic=dominant.traffic,
            traffic_share=dominant.traffic_share,
        )
        if dominant
        else None,
        channel_dependency_score=dependency_score,
        channel_diversification_score=None if dependency_score is None else 1 - dependency_score,
        channel_profile=channel_profile(share_map, dependency_score),
    )
    return summary


def warning_list(session: Session, scope: ChannelScope, date_from: date, date_to: date) -> list[str]:
    """Build warning list.
    Args:
        session (Session): Database session.
        scope (ChannelScope): Channel scope.
        date_from (date): Period start date.
        date_to (date): Period end date."""
    warnings = []
    warning = quality_warning(session, scope.country_id, scope.domain_id, date_from, date_to)
    if warning:
        warnings.append(warning)
    if scope.country_id is not None:
        warnings.append(
            'Country-level channel analysis is estimated from domain-level channel mix weighted by competitor presence in the selected country.',
        )
    if (date_to - date_from).days + 1 < 7:
        warnings.append('Selected period is too short for reliable channel stability analysis.')
    return warnings


def save_metrics(
    session: Session,
    scope: ChannelScope,
    date_from: date,
    date_to: date,
    metrics: list[ChannelMetric],
    calculation_version: str,
) -> int:
    """Save channel metrics.
    Args:
        session (Session): Database session.
        scope (ChannelScope): Channel scope.
        date_from (date): Period start date.
        date_to (date): Period end date.
        metrics (list[ChannelMetric]): Channel metrics.
        calculation_version (str): Calculation version."""
    count = 0
    for metric in metrics:
        session.execute(
            text(
                """
                INSERT INTO metric_channel_period (
                    scope_type, country_id, domain_id, company_id, channel_id, period_start, period_end,
                    traffic, traffic_share, growth_rate, stability_score, is_dominant_channel,
                    dependency_score, calculation_version
                )
                VALUES (
                    :scope_type, :country_id, :domain_id, :company_id, :channel_id, :period_start, :period_end,
                    :traffic, :traffic_share, :growth_rate, :stability_score, :is_dominant_channel,
                    :dependency_score, :calculation_version
                )
                ON CONFLICT (scope_type, country_id, domain_id, channel_id, period_start, period_end, calculation_version)
                DO UPDATE SET
                    traffic = EXCLUDED.traffic,
                    traffic_share = EXCLUDED.traffic_share,
                    growth_rate = EXCLUDED.growth_rate,
                    stability_score = EXCLUDED.stability_score,
                    is_dominant_channel = EXCLUDED.is_dominant_channel,
                    dependency_score = EXCLUDED.dependency_score,
                    calculated_at = now()
                """,
            ),
            {
                'scope_type': scope.scope_type,
                'country_id': scope.country_id,
                'domain_id': scope.domain_id,
                'company_id': scope.company_id,
                'channel_id': metric.channel_id,
                'period_start': date_from,
                'period_end': date_to,
                'traffic': metric.traffic,
                'traffic_share': metric.traffic_share,
                'growth_rate': metric.growth_rate,
                'stability_score': metric.stability_score,
                'is_dominant_channel': metric.is_dominant_channel,
                'dependency_score': metric.dependency_score,
                'calculation_version': calculation_version,
            },
        )
        count += 1
    session.commit()
    return count


def build_summary(
    session: Session,
    country_id: int | None,
    domain_id: int | None,
    date_from: date,
    date_to: date,
    calculation_version: str,
) -> ChannelSummaryResponse:
    """Build channel summary.
    Args:
        session (Session): Database session.
        country_id (int | None): Country identifier.
        domain_id (int | None): Domain identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        calculation_version (str): Calculation version."""
    scope = resolve_scope(session, country_id, domain_id)
    warnings = warning_list(session, scope, date_from, date_to)
    rows = scoped_channels(session, scope, date_from, date_to)
    if not rows:
        raise HTTPException(status_code=404, detail='No channel data available for selected filters.')
    growth = channel_growth(session, scope, date_from, date_to)
    stability = stability_map(session, scope, date_from, date_to)
    metrics = build_metrics(rows, growth, stability)
    summary = summary_values(metrics)
    save_metrics(session, scope, date_from, date_to, metrics, calculation_version)
    response = ChannelSummaryResponse(
        scope=scope,
        period=ChannelPeriod(date_from=date_from, date_to=date_to, days_count=(date_to - date_from).days + 1),
        summary=summary,
        channels=metrics,
        warnings=warnings,
        recommendation_hints=[channel_hint(metric) for metric in metrics[:5]],
    )
    return response


def build_trend(
    session: Session,
    country_id: int | None,
    domain_id: int | None,
    channel_id: int | None,
    date_from: date,
    date_to: date,
) -> list[ChannelTrendItem]:
    """Build channel trend.
    Args:
        session (Session): Database session.
        country_id (int | None): Country identifier.
        domain_id (int | None): Domain identifier.
        channel_id (int | None): Channel identifier.
        date_from (date): Period start date.
        date_to (date): Period end date."""
    scope = resolve_scope(session, country_id, domain_id)
    if scope.country_id is not None:
        rows = scoped_channels(session, scope, date_from, date_to)
        total_traffic = sum(float_value(row.get('traffic')) for row in rows)
        items = [
            ChannelTrendItem(
                date=date_to,
                channel_id=int(row['channel_id']),
                channel_code=str(row['channel_code']),
                channel_name=str(row['channel_name']),
                traffic=float_value(row.get('traffic')),
                traffic_share=ratio_value(float_value(row.get('traffic')), total_traffic),
            )
            for row in rows
            if channel_id is None or int(row['channel_id']) == channel_id
        ]
        return items
    rows = daily_channels(session, scope, date_from, date_to)
    totals: dict[date, float] = {}
    for row in rows:
        totals[row['date']] = totals.get(row['date'], 0) + float_value(row.get('traffic'))
    items = [
        ChannelTrendItem(
            date=row['date'],
            channel_id=int(row['channel_id']),
            channel_code=str(row['channel_code']),
            channel_name=str(row['channel_name']),
            traffic=float_value(row.get('traffic')),
            traffic_share=ratio_value(float_value(row.get('traffic')), totals[row['date']]),
        )
        for row in rows
        if channel_id is None or int(row['channel_id']) == channel_id
    ]
    return items
