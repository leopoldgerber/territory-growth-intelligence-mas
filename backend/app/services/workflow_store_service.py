import json

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.workflow import WorkflowRequest, WorkflowRunDetail, WorkflowRunItem
from app.services.mas_store_service import get_run


def json_text(value: object) -> str:
    """Convert value to JSON text.
    Args:
        value (object): Source value."""
    serialized_value = json.dumps(value, default=str)
    return serialized_value


def create_workflow(session: Session, request: WorkflowRequest, quality_status: str) -> int:
    """Create workflow run.
    Args:
        session (Session): Database session.
        request (WorkflowRequest): Workflow request.
        quality_status (str): Data quality status."""
    result = session.execute(
        text(
            """
            INSERT INTO workflow_runs (
                project_id, workflow_type, status, country_id, period_start, period_end, budget_amount,
                currency_code, campaign_goal, risk_appetite, input_params
            )
            VALUES (
                :project_id, 'strategy_analysis', 'running', :country_id, :period_start, :period_end, :budget_amount,
                :currency_code, :campaign_goal, :risk_appetite, CAST(:input_params AS jsonb)
            )
            RETURNING workflow_run_id
            """,
        ),
        {
            'project_id': request.project_id,
            'country_id': request.country_id,
            'period_start': request.date_from,
            'period_end': request.date_to,
            'budget_amount': request.budget_amount,
            'currency_code': request.currency_code[:3].upper(),
            'campaign_goal': request.campaign_goal,
            'risk_appetite': request.risk_appetite,
            'input_params': json_text({**request.model_dump(mode='json'), 'data_quality_status': quality_status}),
        },
    )
    workflow_run_id = int(result.scalar_one())
    session.commit()
    return workflow_run_id


def update_workflow(
    session: Session,
    workflow_run_id: int,
    status: str,
    result_payload: dict[str, object],
    agent_run_id: int | None,
    report_id: int | None,
    strategy_id: int | None,
    summary_id: int | None,
    error_message: str | None = None,
) -> int:
    """Update workflow run.
    Args:
        session (Session): Database session.
        workflow_run_id (int): Workflow run identifier.
        status (str): Workflow status.
        result_payload (dict[str, object]): Result payload.
        agent_run_id (int | None): Agent run identifier.
        report_id (int | None): Report identifier.
        strategy_id (int | None): Strategy identifier.
        summary_id (int | None): Summary identifier.
        error_message (str | None): Error message."""
    session.execute(
        text(
            """
            UPDATE workflow_runs
            SET status = :status,
                agent_run_id = :agent_run_id,
                report_id = :report_id,
                strategy_id = :strategy_id,
                summary_id = :summary_id,
                result_payload = CAST(:result_payload AS jsonb),
                error_message = :error_message,
                finished_at = now()
            WHERE workflow_run_id = :workflow_run_id
            """,
        ),
        {
            'workflow_run_id': workflow_run_id,
            'status': status,
            'agent_run_id': agent_run_id,
            'report_id': report_id,
            'strategy_id': strategy_id,
            'summary_id': summary_id,
            'result_payload': json_text(result_payload),
            'error_message': error_message,
        },
    )
    session.commit()
    return workflow_run_id


def link_project_results(
    session: Session,
    project_id: int | None,
    agent_run_id: int | None,
    report_id: int | None,
    strategy_id: int | None,
    summary_id: int | None,
) -> int | None:
    """Link project results.
    Args:
        session (Session): Database session.
        project_id (int | None): Project identifier.
        agent_run_id (int | None): Agent run identifier.
        report_id (int | None): Report identifier.
        strategy_id (int | None): Strategy identifier.
        summary_id (int | None): Summary identifier."""
    if project_id is None:
        return project_id
    updates = [
        ('agent_runs', 'agent_run_id', agent_run_id),
        ('report_snapshots', 'report_id', report_id),
        ('budget_strategy_runs', 'strategy_id', strategy_id),
        ('saved_summaries', 'summary_id', summary_id),
    ]
    for table_name, key_name, key_value in updates:
        if key_value is not None:
            session.execute(
                text(f'UPDATE {table_name} SET project_id = :project_id WHERE {key_name} = :key_value'),
                {'project_id': project_id, 'key_value': key_value},
            )
    session.commit()
    return project_id


def workflow_row(session: Session, workflow_run_id: int) -> dict[str, object] | None:
    """Get workflow row.
    Args:
        session (Session): Database session.
        workflow_run_id (int): Workflow run identifier."""
    result = session.execute(
        text(
            """
            SELECT
                workflow.*,
                workflow.created_at::text AS created_at,
                country.country_name_en,
                agents.final_answer
            FROM workflow_runs AS workflow
            LEFT JOIN dim_country AS country ON country.country_id = workflow.country_id
            LEFT JOIN agent_runs AS agents ON agents.agent_run_id = workflow.agent_run_id
            WHERE workflow.workflow_run_id = :workflow_run_id
            """,
        ),
        {'workflow_run_id': workflow_run_id},
    )
    row = result.first()
    data = dict(row._mapping) if row else None
    return data


def get_workflow(session: Session, workflow_run_id: int) -> WorkflowRunDetail | None:
    """Get workflow detail.
    Args:
        session (Session): Database session.
        workflow_run_id (int): Workflow run identifier."""
    data = workflow_row(session, workflow_run_id)
    if data is None:
        return None
    mas_run = get_run(session, int(data['agent_run_id'])) if data.get('agent_run_id') is not None else None
    detail = WorkflowRunDetail(**data, mas_run=mas_run)
    return detail


def list_workflows(session: Session, limit: int, offset: int) -> dict[str, object]:
    """List workflow runs.
    Args:
        session (Session): Database session.
        limit (int): Result limit.
        offset (int): Result offset."""
    result = session.execute(
        text(
            """
            SELECT
                workflow.workflow_run_id,
                workflow.project_id,
                workflow.workflow_type,
                workflow.status,
                workflow.country_id,
                country.country_name_en,
                workflow.period_start,
                workflow.period_end,
                workflow.budget_amount,
                workflow.currency_code,
                workflow.campaign_goal,
                workflow.risk_appetite,
                workflow.agent_run_id,
                workflow.report_id,
                workflow.strategy_id,
                workflow.summary_id,
                agents.final_answer,
                workflow.error_message,
                workflow.created_at::text AS created_at,
                COUNT(*) OVER() AS total
            FROM workflow_runs AS workflow
            LEFT JOIN dim_country AS country ON country.country_id = workflow.country_id
            LEFT JOIN agent_runs AS agents ON agents.agent_run_id = workflow.agent_run_id
            ORDER BY workflow.created_at DESC, workflow.workflow_run_id DESC
            LIMIT :limit OFFSET :offset
            """,
        ),
        {'limit': limit, 'offset': offset},
    )
    rows = [dict(row._mapping) for row in result]
    total = int(rows[0]['total']) if rows else 0
    items = [WorkflowRunItem(**{key: value for key, value in row.items() if key != 'total'}) for row in rows]
    return {'items': items, 'total': total}
