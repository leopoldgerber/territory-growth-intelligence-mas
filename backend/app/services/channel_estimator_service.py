from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.country_query_service import float_value, ratio_value


def country_weights(session: Session, country_id: int, date_from: date, date_to: date) -> list[dict[str, object]]:
    """Build country weights.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        date_from (date): Period start date.
        date_to (date): Period end date."""
    result = session.execute(
        text(
            """
            WITH domain_traffic AS (
                SELECT domain_id, company_id, SUM(traffic) AS traffic
                FROM fact_domain_country_daily
                WHERE country_id = :country_id
                  AND date BETWEEN :date_from AND :date_to
                GROUP BY domain_id, company_id
            )
            SELECT
                domain_id,
                company_id,
                traffic,
                traffic / NULLIF(SUM(traffic) OVER(), 0) AS domain_weight
            FROM domain_traffic
            WHERE traffic > 0
            """,
        ),
        {'country_id': country_id, 'date_from': date_from, 'date_to': date_to},
    )
    rows = [dict(row._mapping) for row in result]
    return rows


def estimate_channels(
    session: Session,
    country_id: int,
    domain_id: int | None,
    date_from: date,
    date_to: date,
) -> list[dict[str, object]]:
    """Estimate channel rows.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        domain_id (int | None): Domain identifier.
        date_from (date): Period start date.
        date_to (date): Period end date."""
    weights = country_weights(session, country_id, date_from, date_to)
    if domain_id is not None:
        weights = [weight for weight in weights if weight.get('domain_id') == domain_id]
    total_country_traffic = sum(float_value(weight.get('traffic')) for weight in weights)
    if not weights or total_country_traffic == 0:
        return []
    domain_ids = [int(weight['domain_id']) for weight in weights]
    result = session.execute(
        text(
            """
            SELECT
                facts.domain_id,
                facts.channel_id,
                channels.channel_code,
                channels.channel_name,
                SUM(facts.traffic) AS traffic,
                SUM(SUM(facts.traffic)) OVER (PARTITION BY facts.domain_id) AS domain_channel_total
            FROM fact_domain_channel_daily AS facts
            JOIN dim_channel AS channels ON channels.channel_id = facts.channel_id
            WHERE facts.domain_id = ANY(:domain_ids)
              AND facts.date BETWEEN :date_from AND :date_to
            GROUP BY facts.domain_id, facts.channel_id, channels.channel_code, channels.channel_name
            """,
        ),
        {'domain_ids': domain_ids, 'date_from': date_from, 'date_to': date_to},
    )
    weight_map = {int(weight['domain_id']): weight for weight in weights}
    channel_map: dict[int, dict[str, object]] = {}
    for row in result:
        row_domain_id = int(row.domain_id)
        domain_weight = float_value(weight_map[row_domain_id].get('domain_weight'))
        channel_share = ratio_value(float_value(row.traffic), float_value(row.domain_channel_total)) or 0
        estimated_traffic = total_country_traffic * domain_weight * channel_share
        item = channel_map.setdefault(
            int(row.channel_id),
            {
                'channel_id': int(row.channel_id),
                'channel_code': row.channel_code,
                'channel_name': row.channel_name,
                'traffic': 0.0,
            },
        )
        item['traffic'] = float_value(item.get('traffic')) + estimated_traffic
    rows = list(channel_map.values())
    return rows


def estimate_sources(
    session: Session,
    country_id: int,
    domain_id: int | None,
    date_from: date,
    date_to: date,
) -> list[dict[str, object]]:
    """Estimate source rows.
    Args:
        session (Session): Database session.
        country_id (int): Country identifier.
        domain_id (int | None): Domain identifier.
        date_from (date): Period start date.
        date_to (date): Period end date."""
    weights = country_weights(session, country_id, date_from, date_to)
    if domain_id is not None:
        weights = [weight for weight in weights if weight.get('domain_id') == domain_id]
    total_country_traffic = sum(float_value(weight.get('traffic')) for weight in weights)
    if not weights or total_country_traffic == 0:
        return []
    domain_ids = [int(weight['domain_id']) for weight in weights]
    result = session.execute(
        text(
            """
            SELECT
                facts.domain_id,
                facts.journey_source_id,
                facts.channel_id,
                sources.source_name,
                facts.source_type,
                facts.traffic_type,
                channels.channel_code,
                channels.channel_name,
                SUM(facts.traffic) AS traffic,
                SUM(SUM(facts.traffic)) OVER (PARTITION BY facts.domain_id) AS domain_source_total
            FROM fact_domain_journey_source_daily AS facts
            JOIN dim_journey_source AS sources ON sources.journey_source_id = facts.journey_source_id
            LEFT JOIN dim_channel AS channels ON channels.channel_id = facts.channel_id
            WHERE facts.domain_id = ANY(:domain_ids)
              AND facts.date BETWEEN :date_from AND :date_to
            GROUP BY
                facts.domain_id,
                facts.journey_source_id,
                facts.channel_id,
                sources.source_name,
                facts.source_type,
                facts.traffic_type,
                channels.channel_code,
                channels.channel_name
            """,
        ),
        {'domain_ids': domain_ids, 'date_from': date_from, 'date_to': date_to},
    )
    weight_map = {int(weight['domain_id']): weight for weight in weights}
    source_map: dict[int, dict[str, object]] = {}
    for row in result:
        row_domain_id = int(row.domain_id)
        domain_weight = float_value(weight_map[row_domain_id].get('domain_weight'))
        source_share = ratio_value(float_value(row.traffic), float_value(row.domain_source_total)) or 0
        estimated_traffic = total_country_traffic * domain_weight * source_share
        item = source_map.setdefault(
            int(row.journey_source_id),
            {
                'journey_source_id': int(row.journey_source_id),
                'source_name': row.source_name,
                'source_type': row.source_type,
                'traffic_type': row.traffic_type,
                'channel_id': row.channel_id,
                'channel_code': row.channel_code,
                'channel_name': row.channel_name,
                'traffic': 0.0,
            },
        )
        item['traffic'] = float_value(item.get('traffic')) + estimated_traffic
    rows = list(source_map.values())
    return rows
