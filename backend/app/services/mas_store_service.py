from datetime import date
import json

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.mas import (
    MASEvidenceItem,
    MASInsightItem,
    MASRecommendationItem,
    MASRunListItem,
    MASRunResponse,
    MASStepItem,
)


def json_text(value: object) -> str:
    """Convert value to JSON text.
    Args:
        value (object): Source value."""
    serialized_value = json.dumps(value)
    return serialized_value


def create_run(
    session: Session,
    user_query: str,
    country_id: int | None,
    date_from: date | None,
    date_to: date | None,
    budget_amount: float | None,
    currency_code: str,
    campaign_goal: str,
) -> int:
    """Create agent run.
    Args:
        session (Session): Database session.
        user_query (str): User query text.
        country_id (int | None): Country identifier.
        date_from (date | None): Period start date.
        date_to (date | None): Period end date.
        budget_amount (float | None): Budget amount.
        currency_code (str): Currency code.
        campaign_goal (str): Campaign goal."""
    result = session.execute(
        text(
            """
            INSERT INTO agent_runs (
                run_type, run_status, user_query, country_id, period_start, period_end,
                budget_amount, currency_code, campaign_goal, input_params
            )
            VALUES (
                'strategy_analysis', 'running', :user_query, :country_id, :period_start, :period_end,
                :budget_amount, :currency_code, :campaign_goal, CAST(:input_params AS jsonb)
            )
            RETURNING agent_run_id
            """,
        ),
        {
            'user_query': user_query,
            'country_id': country_id,
            'period_start': date_from,
            'period_end': date_to,
            'budget_amount': budget_amount,
            'currency_code': currency_code,
            'campaign_goal': campaign_goal,
            'input_params': json_text(
                {
                    'country_id': country_id,
                    'date_from': str(date_from) if date_from else None,
                    'date_to': str(date_to) if date_to else None,
                    'budget_amount': budget_amount,
                    'currency_code': currency_code,
                    'campaign_goal': campaign_goal,
                },
            ),
        },
    )
    agent_run_id = int(result.scalar_one())
    session.commit()
    return agent_run_id


def update_run(
    session: Session,
    agent_run_id: int,
    run_status: str,
    final_answer: str | None,
    confidence_score: float | None,
    output_payload: dict[str, object],
) -> int:
    """Update agent run.
    Args:
        session (Session): Database session.
        agent_run_id (int): Agent run identifier.
        run_status (str): Run status.
        final_answer (str | None): Final answer text.
        confidence_score (float | None): Confidence score.
        output_payload (dict[str, object]): Output payload."""
    session.execute(
        text(
            """
            UPDATE agent_runs
            SET run_status = :run_status,
                final_answer = :final_answer,
                confidence_score = :confidence_score,
                output_payload = CAST(:output_payload AS jsonb),
                finished_at = now(),
                updated_at = now()
            WHERE agent_run_id = :agent_run_id
            """,
        ),
        {
            'agent_run_id': agent_run_id,
            'run_status': run_status,
            'final_answer': final_answer,
            'confidence_score': confidence_score,
            'output_payload': json_text(output_payload),
        },
    )
    session.commit()
    return agent_run_id


def save_step(
    session: Session,
    agent_run_id: int,
    step_order: int,
    agent_name: str,
    step_type: str,
    step_status: str,
    summary: str,
    output_payload: dict[str, object],
) -> int:
    """Save agent step.
    Args:
        session (Session): Database session.
        agent_run_id (int): Agent run identifier.
        step_order (int): Step order.
        agent_name (str): Agent name.
        step_type (str): Step type.
        step_status (str): Step status.
        summary (str): Step summary.
        output_payload (dict[str, object]): Output payload."""
    result = session.execute(
        text(
            """
            INSERT INTO agent_steps (
                agent_run_id, step_order, agent_name, step_type, step_status, summary,
                output_payload, started_at, finished_at
            )
            VALUES (
                :agent_run_id, :step_order, :agent_name, :step_type, :step_status, :summary,
                CAST(:output_payload AS jsonb), now(), now()
            )
            RETURNING agent_step_id
            """,
        ),
        {
            'agent_run_id': agent_run_id,
            'step_order': step_order,
            'agent_name': agent_name,
            'step_type': step_type,
            'step_status': step_status,
            'summary': summary,
            'output_payload': json_text(output_payload),
        },
    )
    agent_step_id = int(result.scalar_one())
    session.commit()
    return agent_step_id


def save_evidence(
    session: Session,
    agent_run_id: int,
    evidence_type: str,
    source_name: str,
    source_ref: str,
    metric_name: str,
    metric_value: float | None,
    payload: dict[str, object],
) -> int:
    """Save evidence item.
    Args:
        session (Session): Database session.
        agent_run_id (int): Agent run identifier.
        evidence_type (str): Evidence type.
        source_name (str): Source name.
        source_ref (str): Source reference.
        metric_name (str): Metric name.
        metric_value (float | None): Metric value.
        payload (dict[str, object]): Evidence payload."""
    result = session.execute(
        text(
            """
            INSERT INTO agent_evidence (
                agent_run_id, evidence_type, source_name, source_ref, metric_name,
                metric_value, payload
            )
            VALUES (
                :agent_run_id, :evidence_type, :source_name, :source_ref, :metric_name,
                :metric_value, CAST(:payload AS jsonb)
            )
            RETURNING evidence_id
            """,
        ),
        {
            'agent_run_id': agent_run_id,
            'evidence_type': evidence_type,
            'source_name': source_name,
            'source_ref': source_ref,
            'metric_name': metric_name,
            'metric_value': metric_value,
            'payload': json_text(payload),
        },
    )
    evidence_id = int(result.scalar_one())
    session.commit()
    return evidence_id


def save_insight(
    session: Session,
    agent_run_id: int,
    agent_name: str,
    insight_type: str,
    title: str,
    summary: str,
    severity: str,
    confidence_score: float,
) -> int:
    """Save insight item.
    Args:
        session (Session): Database session.
        agent_run_id (int): Agent run identifier.
        agent_name (str): Agent name.
        insight_type (str): Insight type.
        title (str): Insight title.
        summary (str): Insight summary.
        severity (str): Insight severity.
        confidence_score (float): Confidence score."""
    result = session.execute(
        text(
            """
            INSERT INTO agent_insights (
                agent_run_id, agent_name, insight_type, title, summary, severity, confidence_score
            )
            VALUES (
                :agent_run_id, :agent_name, :insight_type, :title, :summary, :severity, :confidence_score
            )
            RETURNING insight_id
            """,
        ),
        {
            'agent_run_id': agent_run_id,
            'agent_name': agent_name,
            'insight_type': insight_type,
            'title': title,
            'summary': summary,
            'severity': severity,
            'confidence_score': confidence_score,
        },
    )
    insight_id = int(result.scalar_one())
    session.commit()
    return insight_id


def save_recommendation(
    session: Session,
    agent_run_id: int,
    recommendation_type: str,
    priority: str,
    title: str,
    description: str,
    rationale: str,
    expected_impact: str,
    confidence_score: float,
) -> int:
    """Save recommendation item.
    Args:
        session (Session): Database session.
        agent_run_id (int): Agent run identifier.
        recommendation_type (str): Recommendation type.
        priority (str): Recommendation priority.
        title (str): Recommendation title.
        description (str): Recommendation description.
        rationale (str): Recommendation rationale.
        expected_impact (str): Expected impact.
        confidence_score (float): Confidence score."""
    result = session.execute(
        text(
            """
            INSERT INTO agent_recommendations (
                agent_run_id, recommendation_type, priority, title, description,
                rationale, expected_impact, confidence_score
            )
            VALUES (
                :agent_run_id, :recommendation_type, :priority, :title, :description,
                :rationale, :expected_impact, :confidence_score
            )
            RETURNING recommendation_id
            """,
        ),
        {
            'agent_run_id': agent_run_id,
            'recommendation_type': recommendation_type,
            'priority': priority,
            'title': title,
            'description': description,
            'rationale': rationale,
            'expected_impact': expected_impact,
            'confidence_score': confidence_score,
        },
    )
    recommendation_id = int(result.scalar_one())
    session.commit()
    return recommendation_id


def step_items(session: Session, agent_run_id: int) -> list[MASStepItem]:
    """Get step items.
    Args:
        session (Session): Database session.
        agent_run_id (int): Agent run identifier."""
    result = session.execute(
        text(
            """
            SELECT agent_step_id, step_order, agent_name, step_type, step_status, summary
            FROM agent_steps
            WHERE agent_run_id = :agent_run_id
            ORDER BY step_order
            """,
        ),
        {'agent_run_id': agent_run_id},
    )
    items = [MASStepItem(**dict(row._mapping)) for row in result]
    return items


def evidence_items(session: Session, agent_run_id: int) -> list[MASEvidenceItem]:
    """Get evidence items.
    Args:
        session (Session): Database session.
        agent_run_id (int): Agent run identifier."""
    result = session.execute(
        text(
            """
            SELECT evidence_id, evidence_type, source_name, source_ref, metric_name, metric_value
            FROM agent_evidence
            WHERE agent_run_id = :agent_run_id
            ORDER BY evidence_id
            """,
        ),
        {'agent_run_id': agent_run_id},
    )
    items = [MASEvidenceItem(**dict(row._mapping)) for row in result]
    return items


def insight_items(session: Session, agent_run_id: int) -> list[MASInsightItem]:
    """Get insight items.
    Args:
        session (Session): Database session.
        agent_run_id (int): Agent run identifier."""
    result = session.execute(
        text(
            """
            SELECT insight_id, agent_name, insight_type, title, summary, severity, confidence_score
            FROM agent_insights
            WHERE agent_run_id = :agent_run_id
            ORDER BY insight_id
            """,
        ),
        {'agent_run_id': agent_run_id},
    )
    items = [MASInsightItem(**dict(row._mapping)) for row in result]
    return items


def recommendation_items(session: Session, agent_run_id: int) -> list[MASRecommendationItem]:
    """Get recommendation items.
    Args:
        session (Session): Database session.
        agent_run_id (int): Agent run identifier."""
    result = session.execute(
        text(
            """
            SELECT
                recommendation_id, recommendation_type, priority, title, description,
                rationale, expected_impact, confidence_score
            FROM agent_recommendations
            WHERE agent_run_id = :agent_run_id
            ORDER BY recommendation_id
            """,
        ),
        {'agent_run_id': agent_run_id},
    )
    items = [MASRecommendationItem(**dict(row._mapping)) for row in result]
    return items


def get_run(session: Session, agent_run_id: int) -> MASRunResponse | None:
    """Get agent run.
    Args:
        session (Session): Database session.
        agent_run_id (int): Agent run identifier."""
    result = session.execute(
        text(
            """
            SELECT
                agent_run_id, user_query, run_status, run_type, country_id, period_start,
                period_end, budget_amount, currency_code, campaign_goal, final_answer, confidence_score
            FROM agent_runs
            WHERE agent_run_id = :agent_run_id
            """,
        ),
        {'agent_run_id': agent_run_id},
    )
    row = result.first()
    if row is None:
        return None
    row_data = dict(row._mapping)
    response = MASRunResponse(
        **row_data,
        steps=step_items(session, agent_run_id),
        evidence=evidence_items(session, agent_run_id),
        insights=insight_items(session, agent_run_id),
        recommendations=recommendation_items(session, agent_run_id),
    )
    return response


def list_runs(session: Session, limit: int, offset: int) -> dict[str, object]:
    """List agent runs.
    Args:
        session (Session): Database session.
        limit (int): Result limit.
        offset (int): Result offset."""
    result = session.execute(
        text(
            """
            SELECT
                agent_run_id, user_query, run_status, run_type, country_id, period_start,
                period_end, confidence_score, created_at::text AS created_at, COUNT(*) OVER() AS total
            FROM agent_runs
            ORDER BY created_at DESC
            LIMIT :limit OFFSET :offset
            """,
        ),
        {'limit': limit, 'offset': offset},
    )
    rows = [dict(row._mapping) for row in result]
    total = int(rows[0]['total']) if rows else 0
    items = [MASRunListItem(**{key: value for key, value in row.items() if key != 'total'}) for row in rows]
    return {'items': items, 'total': total}
