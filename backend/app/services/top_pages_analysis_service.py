from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.marketing import TopPageItem, TopPageList
from app.services.marketing_scope_service import project_filter, source_warnings


def top_pages(session: Session, project_id: int, limit: int = 50) -> TopPageList:
    """Get top pages.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        limit (int): Result limit."""
    result = session.execute(
        text(
            f"""
            SELECT
                page.page_id,
                page.url,
                page.page_type,
                domain.domain,
                fact.country_id,
                SUM(fact.estimated_traffic) AS estimated_traffic,
                SUM(fact.organic_traffic) AS organic_traffic,
                SUM(fact.paid_traffic) AS paid_traffic,
                MAX(fact.keywords_count) AS keywords_count,
                MAX(fact.backlinks_count) AS backlinks_count
            FROM fact_top_page_daily AS fact
            JOIN dim_page AS page ON page.page_id = fact.page_id
            JOIN dim_domain AS domain ON domain.domain_id = fact.domain_id
            WHERE {project_filter(project_id)}
            GROUP BY page.page_id, page.url, page.page_type, domain.domain, fact.country_id
            ORDER BY estimated_traffic DESC NULLS LAST
            LIMIT :limit
            """,
        ),
        {'project_id': project_id, 'limit': limit},
    )
    rows = [dict(row._mapping) for row in result]
    items = [
        TopPageItem(
            page_id=int(row['page_id']),
            url=str(row.get('url') or ''),
            page_type=str(row.get('page_type') or 'unknown'),
            domain=row.get('domain'),
            country_id=row.get('country_id'),
            estimated_traffic=float(row['estimated_traffic']) if row.get('estimated_traffic') is not None else None,
            organic_traffic=float(row['organic_traffic']) if row.get('organic_traffic') is not None else None,
            paid_traffic=float(row['paid_traffic']) if row.get('paid_traffic') is not None else None,
            keywords_count=int(row['keywords_count']) if row.get('keywords_count') is not None else None,
            backlinks_count=int(row['backlinks_count']) if row.get('backlinks_count') is not None else None,
        )
        for row in rows
    ]
    response = TopPageList(
        items=items,
        total=len(items),
        warnings=source_warnings(session, {'top_pages': 'fact_top_page_daily'}, project_id),
    )
    return response
