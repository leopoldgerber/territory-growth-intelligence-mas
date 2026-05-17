import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.marketing import (
    BusinessAssumptionCreate,
    BusinessAssumptionItem,
    BusinessAssumptionList,
    BusinessAssumptionUpdate,
    CampaignCreate,
    CampaignItem,
    CampaignList,
    CampaignPerformanceItem,
    CampaignPerformanceList,
)
from app.services.reference_ingestion_service import upsert_date


def assumption_item(row: dict[str, object]) -> BusinessAssumptionItem:
    """Build assumption item.
    Args:
        row (dict[str, object]): Query row."""
    item = BusinessAssumptionItem(**row)
    return item


def campaign_item(row: dict[str, object]) -> CampaignItem:
    """Build campaign item.
    Args:
        row (dict[str, object]): Query row."""
    item = CampaignItem(**row)
    return item


def list_assumptions(session: Session, project_id: int) -> BusinessAssumptionList:
    """List assumptions.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier."""
    result = session.execute(
        text(
            """
            SELECT *
            FROM business_assumptions
            WHERE project_id = :project_id
            ORDER BY created_at DESC, assumption_id DESC
            """,
        ),
        {'project_id': project_id},
    )
    rows = [dict(row._mapping) for row in result]
    items = [assumption_item(row) for row in rows]
    response = BusinessAssumptionList(items=items, total=len(items))
    return response


def create_assumption(session: Session, project_id: int, request: BusinessAssumptionCreate) -> BusinessAssumptionItem:
    """Create assumption.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        request (BusinessAssumptionCreate): Assumption request."""
    payload = request.model_dump()
    result = session.execute(
        text(
            """
            INSERT INTO business_assumptions (
                project_id, country_id, currency_code, visit_to_lead_rate, lead_to_client_rate,
                average_order_value, ltv, gross_margin, target_cac, monthly_budget,
                confidence_score, valid_from, valid_to, notes
            )
            VALUES (
                :project_id, :country_id, :currency_code, :visit_to_lead_rate, :lead_to_client_rate,
                :average_order_value, :ltv, :gross_margin, :target_cac, :monthly_budget,
                :confidence_score, :valid_from, :valid_to, :notes
            )
            RETURNING *
            """,
        ),
        {'project_id': project_id, **payload},
    )
    session.commit()
    item = assumption_item(dict(result.first()._mapping))
    return item


def update_assumption(
    session: Session,
    project_id: int,
    assumption_id: int,
    request: BusinessAssumptionUpdate,
) -> BusinessAssumptionItem:
    """Update assumption.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        assumption_id (int): Assumption identifier.
        request (BusinessAssumptionUpdate): Assumption update."""
    current = session.execute(
        text('SELECT * FROM business_assumptions WHERE project_id = :project_id AND assumption_id = :assumption_id'),
        {'project_id': project_id, 'assumption_id': assumption_id},
    ).first()
    values = dict(current._mapping)
    values.update({key: value for key, value in request.model_dump().items() if value is not None})
    result = session.execute(
        text(
            """
            UPDATE business_assumptions
            SET country_id = :country_id,
                currency_code = :currency_code,
                visit_to_lead_rate = :visit_to_lead_rate,
                lead_to_client_rate = :lead_to_client_rate,
                average_order_value = :average_order_value,
                ltv = :ltv,
                gross_margin = :gross_margin,
                target_cac = :target_cac,
                monthly_budget = :monthly_budget,
                confidence_score = :confidence_score,
                valid_from = :valid_from,
                valid_to = :valid_to,
                notes = :notes,
                updated_at = now()
            WHERE project_id = :project_id AND assumption_id = :assumption_id
            RETURNING *
            """,
        ),
        values,
    )
    session.commit()
    item = assumption_item(dict(result.first()._mapping))
    return item


def list_campaigns(session: Session, project_id: int) -> CampaignList:
    """List campaigns.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier."""
    result = session.execute(
        text(
            """
            SELECT *
            FROM campaigns
            WHERE project_id = :project_id
            ORDER BY created_at DESC, campaign_id DESC
            """,
        ),
        {'project_id': project_id},
    )
    rows = [dict(row._mapping) for row in result]
    items = [campaign_item(row) for row in rows]
    response = CampaignList(items=items, total=len(items))
    return response


def create_campaign(session: Session, project_id: int, request: CampaignCreate) -> CampaignItem:
    """Create campaign.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        request (CampaignCreate): Campaign request."""
    result = session.execute(
        text(
            """
            INSERT INTO campaigns (
                project_id, campaign_name, channel_code, country_id, status, currency_code, start_date, end_date, notes
            )
            VALUES (
                :project_id, :campaign_name, :channel_code, :country_id, :status, :currency_code, :start_date, :end_date, :notes
            )
            RETURNING *
            """,
        ),
        {'project_id': project_id, **request.model_dump()},
    )
    session.commit()
    item = campaign_item(dict(result.first()._mapping))
    return item


def performance_summary(items: list[CampaignPerformanceItem]) -> dict[str, float | None]:
    """Summarize performance.
    Args:
        items (list[CampaignPerformanceItem]): Performance items."""
    spend = sum(item.spend or 0 for item in items)
    revenue = sum(item.revenue or 0 for item in items)
    clients = sum(item.clients or 0 for item in items)
    leads = sum(item.leads or 0 for item in items)
    summary = {
        'spend': spend,
        'revenue': revenue,
        'leads': leads,
        'clients': clients,
        'cac': spend / clients if clients else None,
        'roas': revenue / spend if spend else None,
        'roi': (revenue - spend) / spend if spend else None,
    }
    return summary


def list_performance(session: Session, project_id: int, campaign_id: int) -> CampaignPerformanceList:
    """List performance.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        campaign_id (int): Campaign identifier."""
    result = session.execute(
        text(
            """
            SELECT *
            FROM campaign_performance_daily
            WHERE project_id = :project_id AND campaign_id = :campaign_id
            ORDER BY date
            """,
        ),
        {'project_id': project_id, 'campaign_id': campaign_id},
    )
    rows = [dict(row._mapping) for row in result]
    items = [CampaignPerformanceItem(**row) for row in rows]
    response = CampaignPerformanceList(items=items, total=len(items), summary=performance_summary(items))
    return response


def upload_performance(
    session: Session,
    project_id: int,
    campaign_id: int,
    data: pd.DataFrame,
    file_id: int | None = None,
    run_id: int | None = None,
) -> CampaignPerformanceList:
    """Upload performance.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        campaign_id (int): Campaign identifier.
        data (pd.DataFrame): Source data.
        file_id (int | None): Source file identifier.
        run_id (int | None): Ingestion run identifier."""
    columns = {str(column).strip().lower(): column for column in data.columns}
    for _, row in data.iterrows():
        date_data = upsert_date(session, row[columns['date']])
        if date_data is None:
            continue
        values = {
            'campaign_id': campaign_id,
            'project_id': project_id,
            'date_id': date_data[0],
            'date': date_data[1],
            'impressions': row.get(columns.get('impressions')),
            'clicks': row.get(columns.get('clicks')),
            'visits': row.get(columns.get('visits')),
            'spend': row.get(columns.get('spend')),
            'leads': row.get(columns.get('leads')),
            'clients': row.get(columns.get('clients')),
            'revenue': row.get(columns.get('revenue')),
            'source_file_id': file_id,
            'run_id': run_id,
        }
        spend = float(values['spend'] or 0)
        clients = float(values['clients'] or 0)
        revenue = float(values['revenue'] or 0)
        values['cac'] = spend / clients if clients else None
        values['roas'] = revenue / spend if spend else None
        values['roi'] = (revenue - spend) / spend if spend else None
        session.execute(
            text(
                """
                INSERT INTO campaign_performance_daily (
                    campaign_id, project_id, date_id, date, impressions, clicks, visits, spend, leads,
                    clients, revenue, cac, roas, roi, source_file_id, run_id
                )
                VALUES (
                    :campaign_id, :project_id, :date_id, :date, :impressions, :clicks, :visits, :spend, :leads,
                    :clients, :revenue, :cac, :roas, :roi, :source_file_id, :run_id
                )
                ON CONFLICT (campaign_id, date_id) DO UPDATE
                SET impressions = EXCLUDED.impressions,
                    clicks = EXCLUDED.clicks,
                    visits = EXCLUDED.visits,
                    spend = EXCLUDED.spend,
                    leads = EXCLUDED.leads,
                    clients = EXCLUDED.clients,
                    revenue = EXCLUDED.revenue,
                    cac = EXCLUDED.cac,
                    roas = EXCLUDED.roas,
                    roi = EXCLUDED.roi
                """,
            ),
            values,
        )
    session.commit()
    response = list_performance(session, project_id, campaign_id)
    return response
