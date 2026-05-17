from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.marketing import CpcSummary, KeywordItem, KeywordList, OpportunitySummary
from app.services.marketing_scope_service import project_filter, source_warnings


def paid_keywords(session: Session, project_id: int, limit: int = 50) -> KeywordList:
    """Get paid keywords.
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
                AVG(fact.cpc) AS cpc,
                SUM(fact.estimated_cost) AS estimated_cost,
                AVG(fact.competition) AS competition,
                MIN(fact.currency_code) AS currency_code
            FROM fact_paid_keyword_daily AS fact
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
            cpc=float(row['cpc']) if row.get('cpc') is not None else None,
            estimated_cost=float(row['estimated_cost']) if row.get('estimated_cost') is not None else None,
            competition=float(row['competition']) if row.get('competition') is not None else None,
            currency_code=row.get('currency_code'),
        )
        for row in rows
    ]
    response = KeywordList(
        items=items,
        total=len(items),
        warnings=source_warnings(session, {'paid_keywords': 'fact_paid_keyword_daily'}, project_id),
    )
    return response


def ppc_opportunity(session: Session, project_id: int) -> OpportunitySummary:
    """Get PPC opportunity.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier."""
    result = session.execute(
        text(
            f"""
            SELECT
                COALESCE(SUM(fact.search_volume), 0) AS demand,
                AVG(fact.cpc) AS cpc,
                SUM(fact.estimated_cost) AS estimated_cost,
                AVG(fact.competition) AS competition
            FROM fact_paid_keyword_daily AS fact
            WHERE {project_filter(project_id)}
            """,
        ),
        {'project_id': project_id},
    )
    row = dict(result.first()._mapping)
    demand = float(row.get('demand') or 0)
    cpc = float(row['cpc']) if row.get('cpc') is not None else None
    estimated_cost = float(row['estimated_cost']) if row.get('estimated_cost') is not None else None
    cpc_penalty = min(float(cpc or 0) * 5, 60)
    score = round(max(min(demand / 10000 * 100, 100) - cpc_penalty, 0), 2) if demand else None
    response = OpportunitySummary(
        project_id=project_id,
        opportunity_score=score,
        demand=demand,
        difficulty=float(row['competition']) if row.get('competition') is not None else None,
        estimated_cost=estimated_cost,
        recommendation='Use paid search for validation where CPC pressure is acceptable.' if demand else 'Upload paid keyword data to calculate PPC opportunity.',
        warnings=source_warnings(session, {'paid_keywords': 'fact_paid_keyword_daily'}, project_id),
    )
    return response


def cpc_summary(session: Session, project_id: int) -> CpcSummary:
    """Get CPC summary.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier."""
    result = session.execute(
        text(
            f"""
            SELECT
                AVG(fact.cpc) AS average_cpc,
                MIN(fact.cpc) AS min_cpc,
                MAX(fact.cpc) AS max_cpc,
                COALESCE(SUM(fact.estimated_cost), 0) AS total_estimated_cost,
                ARRAY_AGG(DISTINCT fact.currency_code) AS currency_codes
            FROM fact_paid_keyword_daily AS fact
            WHERE {project_filter(project_id)}
            """,
        ),
        {'project_id': project_id},
    )
    row = dict(result.first()._mapping)
    response = CpcSummary(
        project_id=project_id,
        average_cpc=float(row['average_cpc']) if row.get('average_cpc') is not None else None,
        min_cpc=float(row['min_cpc']) if row.get('min_cpc') is not None else None,
        max_cpc=float(row['max_cpc']) if row.get('max_cpc') is not None else None,
        total_estimated_cost=float(row.get('total_estimated_cost') or 0),
        currency_codes=[str(value) for value in row.get('currency_codes') or [] if value],
        warnings=source_warnings(session, {'paid_keywords': 'fact_paid_keyword_daily'}, project_id),
    )
    return response
