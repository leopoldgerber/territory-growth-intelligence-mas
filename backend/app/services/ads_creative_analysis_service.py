from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.marketing import AdCreativeItem, AdCreativeList, AdsSummary
from app.services.marketing_scope_service import project_filter, source_warnings


def ads_creatives(session: Session, project_id: int, limit: int = 50) -> AdCreativeList:
    """Get ad creatives.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        limit (int): Result limit."""
    result = session.execute(
        text(
            f"""
            SELECT
                fact.creative_hash,
                domain.domain,
                fact.country_id,
                MAX(fact.headline) AS headline,
                MAX(fact.description) AS description,
                MAX(fact.cta) AS cta,
                MAX(fact.ad_network) AS ad_network,
                SUM(fact.estimated_spend) AS estimated_spend,
                SUM(fact.estimated_traffic) AS estimated_traffic,
                MIN(fact.first_seen_date) AS first_seen_date,
                MAX(fact.last_seen_date) AS last_seen_date
            FROM fact_ad_creative_daily AS fact
            JOIN dim_domain AS domain ON domain.domain_id = fact.domain_id
            WHERE {project_filter(project_id)}
            GROUP BY fact.creative_hash, domain.domain, fact.country_id
            ORDER BY estimated_spend DESC NULLS LAST, estimated_traffic DESC NULLS LAST
            LIMIT :limit
            """,
        ),
        {'project_id': project_id, 'limit': limit},
    )
    rows = [dict(row._mapping) for row in result]
    items = [
        AdCreativeItem(
            creative_hash=str(row.get('creative_hash') or ''),
            domain=row.get('domain'),
            country_id=row.get('country_id'),
            headline=row.get('headline'),
            description=row.get('description'),
            cta=row.get('cta'),
            ad_network=row.get('ad_network'),
            estimated_spend=float(row['estimated_spend']) if row.get('estimated_spend') is not None else None,
            estimated_traffic=float(row['estimated_traffic']) if row.get('estimated_traffic') is not None else None,
            first_seen_date=row.get('first_seen_date'),
            last_seen_date=row.get('last_seen_date'),
        )
        for row in rows
    ]
    response = AdCreativeList(
        items=items,
        total=len(items),
        warnings=source_warnings(session, {'ads_creatives': 'fact_ad_creative_daily'}, project_id),
    )
    return response


def ads_summary(session: Session, project_id: int) -> AdsSummary:
    """Get ads summary.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier."""
    totals = session.execute(
        text(
            f"""
            SELECT
                COUNT(DISTINCT fact.creative_hash) AS creatives_count,
                COALESCE(SUM(fact.estimated_spend), 0) AS estimated_spend,
                COALESCE(SUM(fact.estimated_traffic), 0) AS estimated_traffic
            FROM fact_ad_creative_daily AS fact
            WHERE {project_filter(project_id)}
            """,
        ),
        {'project_id': project_id},
    ).first()
    ctas = session.execute(
        text(
            f"""
            SELECT fact.cta, COUNT(*) AS count_value
            FROM fact_ad_creative_daily AS fact
            WHERE {project_filter(project_id)} AND fact.cta IS NOT NULL
            GROUP BY fact.cta
            ORDER BY count_value DESC
            LIMIT 10
            """,
        ),
        {'project_id': project_id},
    )
    row = dict(totals._mapping)
    response = AdsSummary(
        project_id=project_id,
        creatives_count=int(row.get('creatives_count') or 0),
        estimated_spend=float(row.get('estimated_spend') or 0),
        estimated_traffic=float(row.get('estimated_traffic') or 0),
        top_ctas=[dict(item._mapping) for item in ctas],
        warnings=source_warnings(session, {'ads_creatives': 'fact_ad_creative_daily'}, project_id),
    )
    return response
