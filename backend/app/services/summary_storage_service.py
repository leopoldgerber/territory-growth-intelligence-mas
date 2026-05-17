import json

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.history import SavedSummaryCreate, SavedSummaryItem, SavedSummaryUpdate


def json_text(value: object) -> str:
    """Convert value to JSON text.
    Args:
        value (object): Source value."""
    serialized_value = json.dumps(value, default=str)
    return serialized_value


def rag_allowed(summary: SavedSummaryCreate) -> bool:
    """Validate RAG readiness.
    Args:
        summary (SavedSummaryCreate): Summary payload."""
    if summary.data_quality_status == 'failed':
        return False
    if len(summary.title.strip()) == 0 or len(summary.summary_text.strip()) < 40:
        return False
    if len(summary.source_type.strip()) == 0 or summary.source_id <= 0:
        return False
    if summary.period_start is None and summary.period_end is None and summary.summary_type != 'manual':
        return False
    if summary.confidence_score is not None and summary.confidence_score < 0.4:
        return False
    return summary.rag_ready


def create_summary(session: Session, summary: SavedSummaryCreate) -> int:
    """Create saved summary.
    Args:
        session (Session): Database session.
        summary (SavedSummaryCreate): Summary payload."""
    result = session.execute(
        text(
            """
            INSERT INTO saved_summaries (
                summary_type, title, summary_text, summary_json, country_id, domain_id, channel_id,
                period_start, period_end, source_type, source_id, tags, importance_score,
                confidence_score, data_quality_status, rag_ready, embedding_status
            )
            VALUES (
                :summary_type, :title, :summary_text, CAST(:summary_json AS jsonb), :country_id, :domain_id,
                :channel_id, :period_start, :period_end, :source_type, :source_id, :tags, :importance_score,
                :confidence_score, :data_quality_status, :rag_ready, :embedding_status
            )
            ON CONFLICT (source_type, source_id, summary_type) DO UPDATE
            SET title = EXCLUDED.title,
                summary_text = EXCLUDED.summary_text,
                summary_json = EXCLUDED.summary_json,
                country_id = EXCLUDED.country_id,
                domain_id = EXCLUDED.domain_id,
                channel_id = EXCLUDED.channel_id,
                period_start = EXCLUDED.period_start,
                period_end = EXCLUDED.period_end,
                tags = EXCLUDED.tags,
                importance_score = EXCLUDED.importance_score,
                confidence_score = EXCLUDED.confidence_score,
                data_quality_status = EXCLUDED.data_quality_status,
                rag_ready = EXCLUDED.rag_ready,
                embedding_status = EXCLUDED.embedding_status,
                updated_at = now()
            RETURNING summary_id
            """,
        ),
        {
            **summary.model_dump(),
            'summary_json': json_text(summary.summary_json or {}),
            'rag_ready': rag_allowed(summary),
        },
    )
    summary_id = int(result.scalar_one())
    session.commit()
    return summary_id


def get_summary(session: Session, summary_id: int) -> SavedSummaryItem | None:
    """Get saved summary.
    Args:
        session (Session): Database session.
        summary_id (int): Summary identifier."""
    result = session.execute(
        text(
            """
            SELECT
                summaries.summary_id,
                summaries.summary_type,
                summaries.title,
                summaries.summary_text,
                summaries.summary_json,
                summaries.country_id,
                countries.country_name_en,
                summaries.domain_id,
                domains.domain,
                summaries.channel_id,
                channels.channel_name,
                summaries.period_start,
                summaries.period_end,
                summaries.source_type,
                summaries.source_id,
                summaries.tags,
                summaries.importance_score,
                summaries.confidence_score,
                summaries.data_quality_status,
                summaries.rag_ready,
                summaries.embedding_status,
                summaries.created_at::text AS created_at,
                summaries.updated_at::text AS updated_at
            FROM saved_summaries AS summaries
            LEFT JOIN dim_country AS countries ON countries.country_id = summaries.country_id
            LEFT JOIN dim_domain AS domains ON domains.domain_id = summaries.domain_id
            LEFT JOIN dim_channel AS channels ON channels.channel_id = summaries.channel_id
            WHERE summaries.summary_id = :summary_id
            """,
        ),
        {'summary_id': summary_id},
    )
    row = result.first()
    if row is None:
        return None
    item = SavedSummaryItem(**dict(row._mapping))
    return item


def update_summary(session: Session, summary_id: int, payload: SavedSummaryUpdate) -> SavedSummaryItem | None:
    """Update saved summary.
    Args:
        session (Session): Database session.
        summary_id (int): Summary identifier.
        payload (SavedSummaryUpdate): Update payload."""
    current = get_summary(session, summary_id)
    if current is None:
        return None
    update_data = payload.model_dump(exclude_unset=True)
    merged = current.model_dump()
    merged.update(update_data)
    validation_payload = SavedSummaryCreate(
        summary_type=merged['summary_type'],
        title=merged['title'],
        summary_text=merged['summary_text'],
        summary_json=merged.get('summary_json'),
        country_id=merged.get('country_id'),
        domain_id=merged.get('domain_id'),
        channel_id=merged.get('channel_id'),
        period_start=merged.get('period_start'),
        period_end=merged.get('period_end'),
        source_type=merged['source_type'],
        source_id=merged['source_id'],
        tags=merged.get('tags') or [],
        importance_score=merged.get('importance_score'),
        confidence_score=merged.get('confidence_score'),
        data_quality_status=merged.get('data_quality_status') or 'unknown',
        rag_ready=merged.get('rag_ready') or False,
        embedding_status=merged.get('embedding_status') or 'not_started',
    )
    session.execute(
        text(
            """
            UPDATE saved_summaries
            SET title = :title,
                summary_text = :summary_text,
                summary_json = CAST(:summary_json AS jsonb),
                tags = :tags,
                importance_score = :importance_score,
                confidence_score = :confidence_score,
                data_quality_status = :data_quality_status,
                rag_ready = :rag_ready,
                embedding_status = :embedding_status,
                updated_at = now()
            WHERE summary_id = :summary_id
            """,
        ),
        {
            'summary_id': summary_id,
            'title': validation_payload.title,
            'summary_text': validation_payload.summary_text,
            'summary_json': json_text(validation_payload.summary_json or {}),
            'tags': validation_payload.tags,
            'importance_score': validation_payload.importance_score,
            'confidence_score': validation_payload.confidence_score,
            'data_quality_status': validation_payload.data_quality_status,
            'rag_ready': rag_allowed(validation_payload),
            'embedding_status': validation_payload.embedding_status,
        },
    )
    session.commit()
    updated = get_summary(session, summary_id)
    return updated


def list_summaries(
    session: Session,
    summary_type: str | None,
    country_id: int | None,
    domain_id: int | None,
    channel_id: int | None,
    tag: str | None,
    rag_ready: bool | None,
    search: str | None,
    limit: int,
    offset: int,
) -> dict[str, object]:
    """List saved summaries.
    Args:
        session (Session): Database session.
        summary_type (str | None): Summary type.
        country_id (int | None): Country identifier.
        domain_id (int | None): Domain identifier.
        channel_id (int | None): Channel identifier.
        tag (str | None): Tag filter.
        rag_ready (bool | None): RAG-ready filter.
        search (str | None): Search text.
        limit (int): Result limit.
        offset (int): Result offset."""
    filters = []
    params: dict[str, object] = {'limit': limit, 'offset': offset}
    if summary_type:
        filters.append('summaries.summary_type = :summary_type')
        params['summary_type'] = summary_type
    if country_id is not None:
        filters.append('summaries.country_id = :country_id')
        params['country_id'] = country_id
    if domain_id is not None:
        filters.append('summaries.domain_id = :domain_id')
        params['domain_id'] = domain_id
    if channel_id is not None:
        filters.append('summaries.channel_id = :channel_id')
        params['channel_id'] = channel_id
    if tag:
        filters.append(':tag = ANY(summaries.tags)')
        params['tag'] = tag
    if rag_ready is not None:
        filters.append('summaries.rag_ready = :rag_ready')
        params['rag_ready'] = rag_ready
    if search:
        filters.append('(summaries.title ILIKE :search OR summaries.summary_text ILIKE :search)')
        params['search'] = f'%{search}%'
    where_clause = f'WHERE {" AND ".join(filters)}' if filters else ''
    result = session.execute(
        text(
            f"""
            SELECT
                summaries.summary_id,
                summaries.summary_type,
                summaries.title,
                summaries.summary_text,
                summaries.summary_json,
                summaries.country_id,
                countries.country_name_en,
                summaries.domain_id,
                domains.domain,
                summaries.channel_id,
                channels.channel_name,
                summaries.period_start,
                summaries.period_end,
                summaries.source_type,
                summaries.source_id,
                summaries.tags,
                summaries.importance_score,
                summaries.confidence_score,
                summaries.data_quality_status,
                summaries.rag_ready,
                summaries.embedding_status,
                summaries.created_at::text AS created_at,
                summaries.updated_at::text AS updated_at,
                COUNT(*) OVER() AS total
            FROM saved_summaries AS summaries
            LEFT JOIN dim_country AS countries ON countries.country_id = summaries.country_id
            LEFT JOIN dim_domain AS domains ON domains.domain_id = summaries.domain_id
            LEFT JOIN dim_channel AS channels ON channels.channel_id = summaries.channel_id
            {where_clause}
            ORDER BY summaries.created_at DESC, summaries.summary_id DESC
            LIMIT :limit OFFSET :offset
            """,
        ),
        params,
    )
    rows = [dict(row._mapping) for row in result]
    total = int(rows[0]['total']) if rows else 0
    items = [SavedSummaryItem(**{key: value for key, value in row.items() if key != 'total'}) for row in rows]
    return {'items': items, 'total': total}
