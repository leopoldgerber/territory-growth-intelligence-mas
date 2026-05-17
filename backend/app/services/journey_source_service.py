from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.channel import ChannelScope, JourneySourceItem
from app.services.channel_estimator_service import estimate_sources
from app.services.channel_scope_service import resolve_scope
from app.services.country_query_service import float_value, ratio_value


def direct_sources(
    session: Session,
    scope: ChannelScope,
    channel_id: int | None,
    date_from: date,
    date_to: date,
) -> list[dict[str, object]]:
    """Get direct source rows.
    Args:
        session (Session): Database session.
        scope (ChannelScope): Channel scope.
        channel_id (int | None): Channel identifier.
        date_from (date): Period start date.
        date_to (date): Period end date."""
    filters = ['facts.date BETWEEN :date_from AND :date_to']
    params: dict[str, object] = {'date_from': date_from, 'date_to': date_to}
    if scope.domain_id is not None:
        filters.append('facts.domain_id = :domain_id')
        params['domain_id'] = scope.domain_id
    if channel_id is not None:
        filters.append('facts.channel_id = :channel_id')
        params['channel_id'] = channel_id
    where_clause = ' AND '.join(filters)
    result = session.execute(
        text(
            f"""
            SELECT
                facts.journey_source_id,
                facts.channel_id,
                sources.source_name,
                facts.source_type,
                facts.traffic_type,
                channels.channel_code,
                channels.channel_name,
                SUM(facts.traffic) AS traffic
            FROM fact_domain_journey_source_daily AS facts
            JOIN dim_journey_source AS sources ON sources.journey_source_id = facts.journey_source_id
            LEFT JOIN dim_channel AS channels ON channels.channel_id = facts.channel_id
            WHERE {where_clause}
            GROUP BY
                facts.journey_source_id,
                facts.channel_id,
                sources.source_name,
                facts.source_type,
                facts.traffic_type,
                channels.channel_code,
                channels.channel_name
            ORDER BY traffic DESC NULLS LAST
            """,
        ),
        params,
    )
    rows = [dict(row._mapping) for row in result]
    return rows


def build_sources(
    rows: list[dict[str, object]],
    limit: int,
) -> list[JourneySourceItem]:
    """Build source items.
    Args:
        rows (list[dict[str, object]]): Source rows.
        limit (int): Result limit."""
    total_traffic = sum(float_value(row.get('traffic')) for row in rows)
    items = [
        JourneySourceItem(
            journey_source_id=int(row['journey_source_id']),
            source_name=row.get('source_name'),
            source_type=row.get('source_type'),
            traffic_type=row.get('traffic_type'),
            channel_id=row.get('channel_id'),
            channel_code=row.get('channel_code'),
            channel_name=row.get('channel_name'),
            traffic=float_value(row.get('traffic')),
            traffic_share=ratio_value(float_value(row.get('traffic')), total_traffic),
            growth_rate=None,
            stability_score=None,
        )
        for row in rows[:limit]
    ]
    return items


def save_sources(
    session: Session,
    scope: ChannelScope,
    date_from: date,
    date_to: date,
    items: list[JourneySourceItem],
    calculation_version: str,
) -> int:
    """Save source metrics.
    Args:
        session (Session): Database session.
        scope (ChannelScope): Channel scope.
        date_from (date): Period start date.
        date_to (date): Period end date.
        items (list[JourneySourceItem]): Journey source items.
        calculation_version (str): Calculation version."""
    count = 0
    for item in items:
        session.execute(
            text(
                """
                INSERT INTO metric_journey_source_period (
                    scope_type, country_id, domain_id, company_id, journey_source_id, channel_id,
                    source_name, source_type, traffic_type, period_start, period_end,
                    traffic, traffic_share, growth_rate, stability_score, calculation_version
                )
                VALUES (
                    :scope_type, :country_id, :domain_id, :company_id, :journey_source_id, :channel_id,
                    :source_name, :source_type, :traffic_type, :period_start, :period_end,
                    :traffic, :traffic_share, :growth_rate, :stability_score, :calculation_version
                )
                ON CONFLICT (
                    scope_type, country_id, domain_id, journey_source_id, period_start, period_end, calculation_version
                )
                DO UPDATE SET
                    channel_id = EXCLUDED.channel_id,
                    source_name = EXCLUDED.source_name,
                    source_type = EXCLUDED.source_type,
                    traffic_type = EXCLUDED.traffic_type,
                    traffic = EXCLUDED.traffic,
                    traffic_share = EXCLUDED.traffic_share,
                    growth_rate = EXCLUDED.growth_rate,
                    stability_score = EXCLUDED.stability_score,
                    calculated_at = now()
                """,
            ),
            {
                'scope_type': scope.scope_type,
                'country_id': scope.country_id,
                'domain_id': scope.domain_id,
                'company_id': scope.company_id,
                'journey_source_id': item.journey_source_id,
                'channel_id': item.channel_id,
                'source_name': item.source_name,
                'source_type': item.source_type,
                'traffic_type': item.traffic_type,
                'period_start': date_from,
                'period_end': date_to,
                'traffic': item.traffic,
                'traffic_share': item.traffic_share,
                'growth_rate': item.growth_rate,
                'stability_score': item.stability_score,
                'calculation_version': calculation_version,
            },
        )
        count += 1
    session.commit()
    return count


def build_journey(
    session: Session,
    country_id: int | None,
    domain_id: int | None,
    channel_id: int | None,
    date_from: date,
    date_to: date,
    limit: int,
    calculation_version: str,
) -> tuple[list[JourneySourceItem], list[str]]:
    """Build journey sources.
    Args:
        session (Session): Database session.
        country_id (int | None): Country identifier.
        domain_id (int | None): Domain identifier.
        channel_id (int | None): Channel identifier.
        date_from (date): Period start date.
        date_to (date): Period end date.
        limit (int): Result limit.
        calculation_version (str): Calculation version."""
    scope = resolve_scope(session, country_id, domain_id)
    warnings = []
    if scope.country_id is not None:
        warnings.append('Journey source details are estimated from domain-level source mix.')
        rows = estimate_sources(session, scope.country_id, scope.domain_id, date_from, date_to)
        if channel_id is not None:
            rows = [row for row in rows if row.get('channel_id') == channel_id]
    else:
        rows = direct_sources(session, scope, channel_id, date_from, date_to)
    items = build_sources(rows, limit)
    save_sources(session, scope, date_from, date_to, items, calculation_version)
    return items, warnings
