from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.marketing import KeywordItem, KeywordList, OpportunitySummary
from app.services.marketing_scope_service import project_filter, source_warnings


def keyword_items(rows: list[dict[str, object]]) -> list[KeywordItem]:
    """Build keyword items.
    Args:
        rows (list[dict[str, object]]): Query rows."""
    items = [
        KeywordItem(
            keyword_id=int(row['keyword_id']),
            keyword_text=str(row.get('keyword_text') or ''),
            country_id=row.get('country_id'),
            country_name_en=row.get('country_name_en'),
            domain=row.get('domain'),
            position=float(row['position']) if row.get('position') is not None else None,
            search_volume=float(row['search_volume']) if row.get('search_volume') is not None else None,
            estimated_traffic=float(row['estimated_traffic']) if row.get('estimated_traffic') is not None else None,
            traffic_share=float(row['traffic_share']) if row.get('traffic_share') is not None else None,
            keyword_difficulty=float(row['keyword_difficulty']) if row.get('keyword_difficulty') is not None else None,
        )
        for row in rows
    ]
    return items


def organic_keywords(session: Session, project_id: int, limit: int = 50) -> KeywordList:
    """Get organic keywords.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        limit (int): Result limit."""
    result = session.execute(
        text(
            f"""
            SELECT
                keyword.keyword_id,
                keyword.keyword_text,
                fact.country_id,
                country.country_name_en,
                domain.domain,
                AVG(fact.position) AS position,
                SUM(fact.search_volume) AS search_volume,
                SUM(fact.estimated_traffic) AS estimated_traffic,
                AVG(fact.traffic_share) AS traffic_share,
                AVG(fact.keyword_difficulty) AS keyword_difficulty
            FROM fact_organic_keyword_daily AS fact
            JOIN dim_keyword AS keyword ON keyword.keyword_id = fact.keyword_id
            JOIN dim_domain AS domain ON domain.domain_id = fact.domain_id
            LEFT JOIN dim_country AS country ON country.country_id = fact.country_id
            WHERE {project_filter(project_id)}
            GROUP BY keyword.keyword_id, keyword.keyword_text, fact.country_id, country.country_name_en, domain.domain
            ORDER BY estimated_traffic DESC NULLS LAST, search_volume DESC NULLS LAST
            LIMIT :limit
            """,
        ),
        {'project_id': project_id, 'limit': limit},
    )
    rows = [dict(row._mapping) for row in result]
    items = keyword_items(rows)
    response = KeywordList(
        items=items,
        total=len(items),
        warnings=source_warnings(session, {'organic_keywords': 'fact_organic_keyword_daily'}, project_id),
    )
    return response


def seo_opportunity(session: Session, project_id: int) -> OpportunitySummary:
    """Get SEO opportunity.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier."""
    result = session.execute(
        text(
            f"""
            SELECT
                COALESCE(SUM(fact.search_volume), 0) AS demand,
                AVG(fact.keyword_difficulty) AS difficulty,
                COALESCE(SUM(fact.estimated_traffic), 0) AS traffic
            FROM fact_organic_keyword_daily AS fact
            WHERE {project_filter(project_id)}
            """,
        ),
        {'project_id': project_id},
    )
    row = dict(result.first()._mapping)
    demand = float(row.get('demand') or 0)
    difficulty = float(row['difficulty']) if row.get('difficulty') is not None else None
    normalized_demand = min(demand / 10000 * 100, 100)
    difficulty_penalty = min(float(difficulty or 0), 100)
    score = round(max(normalized_demand - (difficulty_penalty * 0.35), 0), 2) if demand else None
    response = OpportunitySummary(
        project_id=project_id,
        opportunity_score=score,
        demand=demand,
        difficulty=difficulty,
        estimated_cost=None,
        recommendation='Prioritize high-volume keywords with moderate difficulty.' if demand else 'Upload organic keyword data to calculate SEO opportunity.',
        warnings=source_warnings(session, {'organic_keywords': 'fact_organic_keyword_daily'}, project_id),
    )
    return response
