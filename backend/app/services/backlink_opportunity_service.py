from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.marketing import OpportunitySummary, ReferringDomainItem, ReferringDomainList
from app.services.marketing_scope_service import project_filter, source_warnings


def referring_domains(session: Session, project_id: int, limit: int = 50) -> ReferringDomainList:
    """Get referring domains.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        limit (int): Result limit."""
    result = session.execute(
        text(
            f"""
            SELECT
                fact.referring_domain,
                domain.domain,
                fact.country_id,
                MAX(fact.source_url) AS source_url,
                MAX(fact.target_url) AS target_url,
                SUM(fact.backlinks_count) AS backlinks_count,
                AVG(fact.authority_score) AS authority_score,
                SUM(fact.estimated_referral_traffic) AS estimated_referral_traffic
            FROM fact_referring_domain_daily AS fact
            JOIN dim_domain AS domain ON domain.domain_id = fact.domain_id
            WHERE {project_filter(project_id)}
            GROUP BY fact.referring_domain, domain.domain, fact.country_id
            ORDER BY authority_score DESC NULLS LAST, backlinks_count DESC NULLS LAST
            LIMIT :limit
            """,
        ),
        {'project_id': project_id, 'limit': limit},
    )
    rows = [dict(row._mapping) for row in result]
    items = [
        ReferringDomainItem(
            referring_domain=str(row.get('referring_domain') or ''),
            domain=row.get('domain'),
            country_id=row.get('country_id'),
            source_url=row.get('source_url'),
            target_url=row.get('target_url'),
            backlinks_count=int(row['backlinks_count']) if row.get('backlinks_count') is not None else None,
            authority_score=float(row['authority_score']) if row.get('authority_score') is not None else None,
            estimated_referral_traffic=float(row['estimated_referral_traffic']) if row.get('estimated_referral_traffic') is not None else None,
        )
        for row in rows
    ]
    response = ReferringDomainList(
        items=items,
        total=len(items),
        warnings=source_warnings(session, {'backlinks': 'fact_referring_domain_daily'}, project_id),
    )
    return response


def backlink_opportunity(session: Session, project_id: int) -> OpportunitySummary:
    """Get backlink opportunity.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier."""
    result = session.execute(
        text(
            f"""
            SELECT
                COUNT(DISTINCT fact.referring_domain) AS domain_count,
                COALESCE(SUM(fact.backlinks_count), 0) AS backlinks_count,
                AVG(fact.authority_score) AS authority_score,
                COALESCE(SUM(fact.estimated_referral_traffic), 0) AS referral_traffic
            FROM fact_referring_domain_daily AS fact
            WHERE {project_filter(project_id)}
            """,
        ),
        {'project_id': project_id},
    )
    row = dict(result.first()._mapping)
    demand = float(row.get('referral_traffic') or 0)
    authority = float(row['authority_score']) if row.get('authority_score') is not None else None
    score = round(min((float(row.get('domain_count') or 0) * 2) + (authority or 0), 100), 2) if row.get('domain_count') else None
    response = OpportunitySummary(
        project_id=project_id,
        opportunity_score=score,
        demand=demand,
        difficulty=None,
        estimated_cost=None,
        recommendation='Use high-authority referring domains as PR and partnership targets.' if score is not None else 'Upload backlink data to calculate referral opportunity.',
        warnings=source_warnings(session, {'backlinks': 'fact_referring_domain_daily'}, project_id),
    )
    return response
