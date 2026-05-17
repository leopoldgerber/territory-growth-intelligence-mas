from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.history import SavedSummaryCreate
from app.services.summary_storage_service import create_summary


def first_lines(value: str | None, limit: int) -> str:
    """Extract first lines.
    Args:
        value (str | None): Source text.
        limit (int): Character limit."""
    if not value:
        return ''
    normalized_value = ' '.join(value.split())
    summary_text = normalized_value[:limit].strip()
    return summary_text


def tag_values(*values: object) -> list[str]:
    """Build tag values.
    Args:
        values (object): Tag source values."""
    tags = []
    for value in values:
        if value is None:
            continue
        tag = str(value).strip().lower().replace(' ', '_')
        if tag and tag not in tags:
            tags.append(tag)
    return tags


def create_agent_summary(session: Session, agent_run_id: int) -> int | None:
    """Create agent summary.
    Args:
        session (Session): Database session.
        agent_run_id (int): Agent run identifier."""
    result = session.execute(
        text(
            """
            SELECT
                runs.agent_run_id,
                runs.user_query,
                runs.final_answer,
                runs.country_id,
                countries.country_name_en,
                runs.period_start,
                runs.period_end,
                runs.budget_amount,
                runs.currency_code,
                runs.campaign_goal,
                runs.confidence_score,
                runs.run_status
            FROM agent_runs AS runs
            LEFT JOIN dim_country AS countries ON countries.country_id = runs.country_id
            WHERE runs.agent_run_id = :agent_run_id
            """,
        ),
        {'agent_run_id': agent_run_id},
    )
    row = result.first()
    if row is None:
        return None
    data = dict(row._mapping)
    country_name = data.get('country_name_en') or 'selected country'
    summary_text = first_lines(data.get('final_answer'), 900)
    if len(summary_text) == 0:
        summary_text = f"MAS analysis for {country_name} finished with status {data.get('run_status') or 'unknown'}."
    summary = SavedSummaryCreate(
        summary_type='mas_final_summary',
        title=f"MAS summary: {country_name}",
        summary_text=summary_text,
        summary_json={
            'agent_run_id': data['agent_run_id'],
            'user_query': data['user_query'],
            'budget_amount': data.get('budget_amount'),
            'currency_code': data.get('currency_code'),
            'campaign_goal': data.get('campaign_goal'),
        },
        country_id=data.get('country_id'),
        period_start=data.get('period_start'),
        period_end=data.get('period_end'),
        source_type='agent_run',
        source_id=int(data['agent_run_id']),
        tags=tag_values(country_name, 'mas', data.get('campaign_goal')),
        importance_score=0.85,
        confidence_score=float(data.get('confidence_score') or 0.7),
        data_quality_status='unknown',
        rag_ready=True,
    )
    summary_id = create_summary(session, summary)
    if data.get('budget_amount') is not None:
        budget_summary = SavedSummaryCreate(
            summary_type='budget_strategy_summary',
            title=f"Budget strategy summary: {country_name}",
            summary_text=summary_text,
            summary_json=summary.summary_json,
            country_id=data.get('country_id'),
            period_start=data.get('period_start'),
            period_end=data.get('period_end'),
            source_type='agent_run',
            source_id=int(data['agent_run_id']),
            tags=tag_values(country_name, 'budget_strategy', data.get('campaign_goal')),
            importance_score=0.8,
            confidence_score=float(data.get('confidence_score') or 0.7),
            data_quality_status='unknown',
            rag_ready=True,
        )
        create_summary(session, budget_summary)
    return summary_id


def create_report_summary(session: Session, report_id: int) -> int | None:
    """Create report summary.
    Args:
        session (Session): Database session.
        report_id (int): Report identifier."""
    result = session.execute(
        text(
            """
            SELECT
                reports.report_id,
                reports.report_type,
                reports.title,
                reports.report_markdown,
                reports.report_json,
                reports.country_id,
                countries.country_name_en,
                reports.domain_id,
                reports.period_start,
                reports.period_end,
                reports.data_quality_status
            FROM report_snapshots AS reports
            LEFT JOIN dim_country AS countries ON countries.country_id = reports.country_id
            WHERE reports.report_id = :report_id
            """,
        ),
        {'report_id': report_id},
    )
    row = result.first()
    if row is None:
        return None
    data = dict(row._mapping)
    country_name = data.get('country_name_en') or 'selected country'
    summary_text = first_lines(data.get('report_markdown'), 900)
    if len(summary_text) == 0:
        summary_text = f"Saved report {data.get('title')} for {country_name}."
    summary = SavedSummaryCreate(
        summary_type='report_summary',
        title=f"Report summary: {data.get('title')}",
        summary_text=summary_text,
        summary_json={
            'report_id': data['report_id'],
            'report_type': data['report_type'],
            'report_json': data.get('report_json') or {},
        },
        country_id=data.get('country_id'),
        domain_id=data.get('domain_id'),
        period_start=data.get('period_start'),
        period_end=data.get('period_end'),
        source_type='report_snapshot',
        source_id=int(data['report_id']),
        tags=tag_values(country_name, data.get('report_type'), 'report'),
        importance_score=0.75,
        confidence_score=0.75,
        data_quality_status=data.get('data_quality_status') or 'unknown',
        rag_ready=True,
    )
    summary_id = create_summary(session, summary)
    if data.get('report_type') == 'country_report':
        country_summary = SavedSummaryCreate(
            summary_type='country_summary',
            title=f"Country summary: {country_name}",
            summary_text=summary_text,
            summary_json=summary.summary_json,
            country_id=data.get('country_id'),
            period_start=data.get('period_start'),
            period_end=data.get('period_end'),
            source_type='report_snapshot',
            source_id=int(data['report_id']),
            tags=tag_values(country_name, 'country_summary', 'report'),
            importance_score=0.78,
            confidence_score=0.75,
            data_quality_status=data.get('data_quality_status') or 'unknown',
            rag_ready=True,
        )
        create_summary(session, country_summary)
    return summary_id


def create_budget_summary(session: Session, strategy_id: int) -> int | None:
    """Create budget summary.
    Args:
        session (Session): Database session.
        strategy_id (int): Strategy identifier."""
    result = session.execute(
        text(
            """
            SELECT
                strategies.strategy_id,
                strategies.country_id,
                countries.country_name_en,
                strategies.period_start,
                strategies.period_end,
                strategies.budget_amount,
                strategies.currency_code,
                strategies.summary,
                strategies.confidence_score,
                strategies.data_quality_status,
                strategies.campaign_goal
            FROM budget_strategy_runs AS strategies
            LEFT JOIN dim_country AS countries ON countries.country_id = strategies.country_id
            WHERE strategies.strategy_id = :strategy_id
            """,
        ),
        {'strategy_id': strategy_id},
    )
    row = result.first()
    if row is None:
        return None
    data = dict(row._mapping)
    country_name = data.get('country_name_en') or 'selected country'
    summary = SavedSummaryCreate(
        summary_type='budget_strategy_summary',
        title=f"Budget strategy summary: {country_name}",
        summary_text=first_lines(data.get('summary'), 900),
        summary_json={
            'strategy_id': data['strategy_id'],
            'budget_amount': data.get('budget_amount'),
            'currency_code': data.get('currency_code'),
            'campaign_goal': data.get('campaign_goal'),
        },
        country_id=data.get('country_id'),
        period_start=data.get('period_start'),
        period_end=data.get('period_end'),
        source_type='budget_strategy',
        source_id=int(data['strategy_id']),
        tags=tag_values(country_name, 'budget_strategy', data.get('campaign_goal')),
        importance_score=0.8,
        confidence_score=float(data.get('confidence_score') or 0.7),
        data_quality_status=data.get('data_quality_status') or 'unknown',
        rag_ready=True,
    )
    summary_id = create_summary(session, summary)
    return summary_id
