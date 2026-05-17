from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.strategy import BudgetAllocationItem
from app.schemas.workflow import WorkflowResponse
from app.services.mas_store_service import get_run


def latest_strategy(session: Session, agent_run_id: int) -> int | None:
    """Get latest strategy identifier.
    Args:
        session (Session): Database session.
        agent_run_id (int): Agent run identifier."""
    result = session.execute(
        text(
            """
            SELECT strategy.strategy_id
            FROM budget_strategy_runs AS strategy
            JOIN agent_runs AS agents
              ON agents.country_id = strategy.country_id
             AND agents.period_start = strategy.period_start
             AND agents.period_end = strategy.period_end
            WHERE agents.agent_run_id = :agent_run_id
            ORDER BY strategy.created_at DESC, strategy.strategy_id DESC
            LIMIT 1
            """,
        ),
        {'agent_run_id': agent_run_id},
    )
    value = result.scalar_one_or_none()
    return None if value is None else int(value)


def latest_report(session: Session, agent_run_id: int) -> int | None:
    """Get latest report identifier.
    Args:
        session (Session): Database session.
        agent_run_id (int): Agent run identifier."""
    result = session.execute(
        text(
            """
            SELECT reports.report_id
            FROM report_snapshots AS reports
            JOIN agent_runs AS agents
              ON agents.country_id = reports.country_id
             AND agents.period_start = reports.period_start
             AND agents.period_end = reports.period_end
            WHERE agents.agent_run_id = :agent_run_id
              AND reports.report_type = 'country_report'
            ORDER BY reports.created_at DESC, reports.report_id DESC
            LIMIT 1
            """,
        ),
        {'agent_run_id': agent_run_id},
    )
    value = result.scalar_one_or_none()
    return None if value is None else int(value)


def latest_summary(session: Session, agent_run_id: int) -> int | None:
    """Get latest summary identifier.
    Args:
        session (Session): Database session.
        agent_run_id (int): Agent run identifier."""
    result = session.execute(
        text(
            """
            SELECT summary_id
            FROM saved_summaries
            WHERE source_type = 'agent_run'
              AND source_id = :agent_run_id
            ORDER BY created_at DESC, summary_id DESC
            LIMIT 1
            """,
        ),
        {'agent_run_id': agent_run_id},
    )
    value = result.scalar_one_or_none()
    return None if value is None else int(value)


def strategy_allocation(session: Session, strategy_id: int | None) -> list[BudgetAllocationItem]:
    """Get strategy allocation.
    Args:
        session (Session): Database session.
        strategy_id (int | None): Strategy identifier."""
    if strategy_id is None:
        return []
    result = session.execute(
        text(
            """
            SELECT *
            FROM budget_strategy_allocations
            WHERE strategy_id = :strategy_id
            ORDER BY budget_share DESC NULLS LAST
            """,
        ),
        {'strategy_id': strategy_id},
    )
    allocation = [BudgetAllocationItem(**dict(row._mapping)) for row in result]
    return allocation


def workflow_response(
    session: Session,
    workflow_run_id: int,
    agent_run_id: int | None,
    status: str,
    saved: bool,
    warnings: list[str],
) -> WorkflowResponse:
    """Build workflow response.
    Args:
        session (Session): Database session.
        workflow_run_id (int): Workflow run identifier.
        agent_run_id (int | None): Agent run identifier.
        status (str): Workflow status.
        saved (bool): Saved result flag.
        warnings (list[str]): Workflow warnings."""
    mas_run = get_run(session, agent_run_id) if agent_run_id is not None else None
    report_id = latest_report(session, agent_run_id) if agent_run_id is not None else None
    strategy_id = latest_strategy(session, agent_run_id) if agent_run_id is not None else None
    summary_id = latest_summary(session, agent_run_id) if agent_run_id is not None else None
    response = WorkflowResponse(
        workflow_run_id=workflow_run_id,
        agent_run_id=agent_run_id,
        report_id=report_id,
        strategy_id=strategy_id,
        summary_id=summary_id,
        status=status,
        final_answer=mas_run.final_answer if mas_run else None,
        recommendations=mas_run.recommendations if mas_run else [],
        budget_allocation=strategy_allocation(session, strategy_id),
        evidence=mas_run.evidence if mas_run else [],
        steps=mas_run.steps if mas_run else [],
        saved=saved,
        warnings=warnings,
    )
    return response
