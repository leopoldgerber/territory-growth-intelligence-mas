from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.marketing import AudienceFit, AudienceSegmentItem, AudienceSummary
from app.services.marketing_scope_service import project_filter, source_warnings


def fit_score(total_share: float | None, segment_count: int) -> float | None:
    """Calculate fit score.
    Args:
        total_share (float | None): Segment traffic share.
        segment_count (int): Segment count."""
    if total_share is None and segment_count == 0:
        return None
    share_score = min(float(total_share or 0) * 100, 100)
    diversity_score = min(segment_count * 8, 100)
    score = round((share_score * 0.7) + (diversity_score * 0.3), 2)
    return score


def segment_items(rows: list[dict[str, object]]) -> list[AudienceSegmentItem]:
    """Build segment items.
    Args:
        rows (list[dict[str, object]]): Query rows."""
    items = [
        AudienceSegmentItem(
            segment_type=str(row.get('segment_type') or ''),
            segment_name=str(row.get('segment_name') or ''),
            segment_value=row.get('segment_value'),
            traffic=float(row.get('traffic') or 0),
            traffic_share=float(row['traffic_share']) if row.get('traffic_share') is not None else None,
        )
        for row in rows
    ]
    return items


def audience_summary(session: Session, project_id: int) -> AudienceSummary:
    """Get audience summary.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier."""
    result = session.execute(
        text(
            f"""
            SELECT
                segment.segment_type,
                segment.segment_name,
                segment.segment_value,
                COALESCE(SUM(fact.traffic), 0) AS traffic,
                AVG(fact.traffic_share) AS traffic_share
            FROM fact_audience_demographics_daily AS fact
            JOIN dim_audience_segment AS segment ON segment.audience_segment_id = fact.audience_segment_id
            WHERE {project_filter(project_id)}
            GROUP BY segment.segment_type, segment.segment_name, segment.segment_value
            ORDER BY traffic DESC
            LIMIT 25
            """,
        ),
        {'project_id': project_id},
    )
    rows = [dict(row._mapping) for row in result]
    items = segment_items(rows)
    total_traffic = sum(item.traffic for item in items)
    total_share = sum(item.traffic_share or 0 for item in items)
    response = AudienceSummary(
        project_id=project_id,
        total_traffic=total_traffic,
        audience_fit_score=fit_score(total_share, len(items)),
        segments=items,
        warnings=source_warnings(session, {'audience': 'fact_audience_demographics_daily'}, project_id),
    )
    return response


def audience_fit(session: Session, project_id: int, country_id: int) -> AudienceFit:
    """Get country audience fit.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        country_id (int): Country identifier."""
    result = session.execute(
        text(
            """
            SELECT
                segment.segment_type,
                segment.segment_name,
                segment.segment_value,
                COALESCE(SUM(fact.traffic), 0) AS traffic,
                AVG(fact.traffic_share) AS traffic_share
            FROM fact_audience_demographics_daily AS fact
            JOIN dim_audience_segment AS segment ON segment.audience_segment_id = fact.audience_segment_id
            WHERE fact.country_id = :country_id
              AND fact.domain_id IN (
                SELECT domain_id
                FROM project_competitors
                WHERE project_id = :project_id AND is_active = TRUE
              )
            GROUP BY segment.segment_type, segment.segment_name, segment.segment_value
            ORDER BY traffic DESC
            LIMIT 15
            """,
        ),
        {'project_id': project_id, 'country_id': country_id},
    )
    rows = [dict(row._mapping) for row in result]
    items = segment_items(rows)
    total_traffic = sum(item.traffic for item in items)
    total_share = sum(item.traffic_share or 0 for item in items)
    response = AudienceFit(
        project_id=project_id,
        country_id=country_id,
        audience_fit_score=fit_score(total_share, len(items)),
        traffic=total_traffic,
        top_segments=items,
        warnings=source_warnings(session, {'audience': 'fact_audience_demographics_daily'}, project_id),
    )
    return response
