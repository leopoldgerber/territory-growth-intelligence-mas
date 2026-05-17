from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.history import (
    HistoryAgentRunItem,
    HistoryInsightItem,
    HistoryRecommendationItem,
    HistoryReportItem,
)


def report_history(
    session: Session,
    report_type: str | None,
    country_id: int | None,
    domain_id: int | None,
    date_from: date | None,
    date_to: date | None,
    search: str | None,
    limit: int,
    offset: int,
) -> dict[str, object]:
    """Get report history.
    Args:
        session (Session): Database session.
        report_type (str | None): Report type.
        country_id (int | None): Country identifier.
        domain_id (int | None): Domain identifier.
        date_from (date | None): Period start filter.
        date_to (date | None): Period end filter.
        search (str | None): Search text.
        limit (int): Result limit.
        offset (int): Result offset."""
    filters = []
    params: dict[str, object] = {'limit': limit, 'offset': offset}
    if report_type:
        filters.append('reports.report_type = :report_type')
        params['report_type'] = report_type
    if country_id is not None:
        filters.append('reports.country_id = :country_id')
        params['country_id'] = country_id
    if domain_id is not None:
        filters.append('reports.domain_id = :domain_id')
        params['domain_id'] = domain_id
    if date_from is not None:
        filters.append('reports.period_end >= :date_from')
        params['date_from'] = date_from
    if date_to is not None:
        filters.append('reports.period_start <= :date_to')
        params['date_to'] = date_to
    if search:
        filters.append('reports.title ILIKE :search')
        params['search'] = f'%{search}%'
    where_clause = f'WHERE {" AND ".join(filters)}' if filters else ''
    result = session.execute(
        text(
            f"""
            SELECT
                reports.report_id,
                reports.report_type,
                reports.title,
                reports.country_id,
                countries.country_name_en,
                reports.period_start,
                reports.period_end,
                reports.data_quality_status,
                reports.report_status,
                reports.created_at::text AS created_at,
                COUNT(*) OVER() AS total
            FROM report_snapshots AS reports
            LEFT JOIN dim_country AS countries ON countries.country_id = reports.country_id
            {where_clause}
            ORDER BY reports.created_at DESC, reports.report_id DESC
            LIMIT :limit OFFSET :offset
            """,
        ),
        params,
    )
    rows = [dict(row._mapping) for row in result]
    total = int(rows[0]['total']) if rows else 0
    items = [HistoryReportItem(**{key: value for key, value in row.items() if key != 'total'}) for row in rows]
    return {'items': items, 'total': total}


def agent_history(
    session: Session,
    country_id: int | None,
    date_from: date | None,
    date_to: date | None,
    search: str | None,
    limit: int,
    offset: int,
) -> dict[str, object]:
    """Get agent history.
    Args:
        session (Session): Database session.
        country_id (int | None): Country identifier.
        date_from (date | None): Period start filter.
        date_to (date | None): Period end filter.
        search (str | None): Search text.
        limit (int): Result limit.
        offset (int): Result offset."""
    filters = []
    params: dict[str, object] = {'limit': limit, 'offset': offset}
    if country_id is not None:
        filters.append('runs.country_id = :country_id')
        params['country_id'] = country_id
    if date_from is not None:
        filters.append('runs.period_end >= :date_from')
        params['date_from'] = date_from
    if date_to is not None:
        filters.append('runs.period_start <= :date_to')
        params['date_to'] = date_to
    if search:
        filters.append('runs.user_query ILIKE :search')
        params['search'] = f'%{search}%'
    where_clause = f'WHERE {" AND ".join(filters)}' if filters else ''
    result = session.execute(
        text(
            f"""
            SELECT
                runs.agent_run_id,
                runs.run_type,
                runs.user_query,
                runs.country_id,
                countries.country_name_en,
                runs.period_start,
                runs.period_end,
                runs.budget_amount,
                runs.currency_code,
                runs.run_status,
                runs.confidence_score,
                runs.created_at::text AS created_at,
                COUNT(*) OVER() AS total
            FROM agent_runs AS runs
            LEFT JOIN dim_country AS countries ON countries.country_id = runs.country_id
            {where_clause}
            ORDER BY runs.created_at DESC, runs.agent_run_id DESC
            LIMIT :limit OFFSET :offset
            """,
        ),
        params,
    )
    rows = [dict(row._mapping) for row in result]
    total = int(rows[0]['total']) if rows else 0
    items = [HistoryAgentRunItem(**{key: value for key, value in row.items() if key != 'total'}) for row in rows]
    return {'items': items, 'total': total}


def insight_history(
    session: Session,
    country_id: int | None,
    insight_type: str | None,
    severity: str | None,
    limit: int,
    offset: int,
) -> dict[str, object]:
    """Get insight history.
    Args:
        session (Session): Database session.
        country_id (int | None): Country identifier.
        insight_type (str | None): Insight type.
        severity (str | None): Severity filter.
        limit (int): Result limit.
        offset (int): Result offset."""
    filters = []
    params: dict[str, object] = {'limit': limit, 'offset': offset}
    if country_id is not None:
        filters.append('runs.country_id = :country_id')
        params['country_id'] = country_id
    if insight_type:
        filters.append('insights.insight_type = :insight_type')
        params['insight_type'] = insight_type
    if severity:
        filters.append('insights.severity = :severity')
        params['severity'] = severity
    where_clause = f'WHERE {" AND ".join(filters)}' if filters else ''
    result = session.execute(
        text(
            f"""
            SELECT
                insights.insight_id,
                insights.agent_run_id,
                insights.insight_type,
                insights.title,
                insights.summary,
                runs.country_id,
                countries.country_name_en,
                insights.severity,
                insights.confidence_score,
                insights.created_at::text AS created_at,
                COUNT(*) OVER() AS total
            FROM agent_insights AS insights
            LEFT JOIN agent_runs AS runs ON runs.agent_run_id = insights.agent_run_id
            LEFT JOIN dim_country AS countries ON countries.country_id = runs.country_id
            {where_clause}
            ORDER BY insights.created_at DESC, insights.insight_id DESC
            LIMIT :limit OFFSET :offset
            """,
        ),
        params,
    )
    rows = [dict(row._mapping) for row in result]
    total = int(rows[0]['total']) if rows else 0
    items = [HistoryInsightItem(**{key: value for key, value in row.items() if key != 'total'}) for row in rows]
    return {'items': items, 'total': total}


def recommendation_history(
    session: Session,
    country_id: int | None,
    recommendation_type: str | None,
    priority: str | None,
    limit: int,
    offset: int,
) -> dict[str, object]:
    """Get recommendation history.
    Args:
        session (Session): Database session.
        country_id (int | None): Country identifier.
        recommendation_type (str | None): Recommendation type.
        priority (str | None): Priority filter.
        limit (int): Result limit.
        offset (int): Result offset."""
    filters = []
    params: dict[str, object] = {'limit': limit, 'offset': offset}
    if country_id is not None:
        filters.append('runs.country_id = :country_id')
        params['country_id'] = country_id
    if recommendation_type:
        filters.append('recommendations.recommendation_type = :recommendation_type')
        params['recommendation_type'] = recommendation_type
    if priority:
        filters.append('recommendations.priority = :priority')
        params['priority'] = priority
    where_clause = f'WHERE {" AND ".join(filters)}' if filters else ''
    result = session.execute(
        text(
            f"""
            SELECT
                recommendations.recommendation_id,
                recommendations.agent_run_id,
                recommendations.recommendation_type,
                recommendations.priority,
                recommendations.title,
                recommendations.description,
                runs.country_id,
                countries.country_name_en,
                recommendations.expected_impact,
                recommendations.confidence_score,
                recommendations.created_at::text AS created_at,
                COUNT(*) OVER() AS total
            FROM agent_recommendations AS recommendations
            LEFT JOIN agent_runs AS runs ON runs.agent_run_id = recommendations.agent_run_id
            LEFT JOIN dim_country AS countries ON countries.country_id = runs.country_id
            {where_clause}
            ORDER BY recommendations.created_at DESC, recommendations.recommendation_id DESC
            LIMIT :limit OFFSET :offset
            """,
        ),
        params,
    )
    rows = [dict(row._mapping) for row in result]
    total = int(rows[0]['total']) if rows else 0
    items = [HistoryRecommendationItem(**{key: value for key, value in row.items() if key != 'total'}) for row in rows]
    return {'items': items, 'total': total}
