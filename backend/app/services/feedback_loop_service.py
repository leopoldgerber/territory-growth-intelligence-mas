from datetime import date
import json

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.schemas.feedback import (
    AgentFeedbackCreate,
    AgentFeedbackItem,
    AgentFeedbackList,
    CampaignSnapshotCreate,
    CampaignSnapshotItem,
    CampaignSnapshotList,
    ConfidenceResponse,
    ForecastComparisonItem,
    ForecastComparisonList,
    ForecastComparisonRequest,
    LearningSummary,
    RecommendationFeedbackCreate,
    RecommendationFeedbackItem,
    RecommendationFeedbackList,
    ScoringWeightAdjustmentCreate,
    ScoringWeightAdjustmentItem,
    ScoringWeightAdjustmentList,
    ScoringWeightAdjustmentUpdate,
    ScoringWeightVersionItem,
    ScoringWeightVersionList,
)


FORECAST_FIELDS = {
    'traffic': 'expected_traffic_capture',
    'leads': 'expected_leads',
    'clients': 'expected_clients',
    'revenue': 'expected_revenue',
    'cac': 'estimated_cac',
    'roi': 'estimated_roi',
}

ACTUAL_FIELDS = {
    'traffic': 'visits',
    'leads': 'leads',
    'clients': 'clients',
    'revenue': 'revenue',
    'cac': 'cac',
    'roi': 'roi',
}


def json_text(value: object) -> str:
    """Convert JSON text.
    Args:
        value (object): Source value."""
    serialized_value = json.dumps(value)
    return serialized_value


def row_dict(row: object) -> dict[str, object]:
    """Convert query row.
    Args:
        row (object): Query row."""
    data = dict(row._mapping)
    return data


def feedback_item(row: dict[str, object]) -> RecommendationFeedbackItem:
    """Build feedback item.
    Args:
        row (dict[str, object]): Query row."""
    item = RecommendationFeedbackItem(**row)
    return item


def snapshot_item(row: dict[str, object]) -> CampaignSnapshotItem:
    """Build snapshot item.
    Args:
        row (dict[str, object]): Query row."""
    item = CampaignSnapshotItem(**row)
    return item


def comparison_item(row: dict[str, object]) -> ForecastComparisonItem:
    """Build comparison item.
    Args:
        row (dict[str, object]): Query row."""
    item = ForecastComparisonItem(**row)
    return item


def adjustment_item(row: dict[str, object]) -> ScoringWeightAdjustmentItem:
    """Build adjustment item.
    Args:
        row (dict[str, object]): Query row."""
    item = ScoringWeightAdjustmentItem(**row)
    return item


def weight_item(row: dict[str, object]) -> ScoringWeightVersionItem:
    """Build weight item.
    Args:
        row (dict[str, object]): Query row."""
    item = ScoringWeightVersionItem(**row)
    return item


def agent_event_item(row: dict[str, object]) -> AgentFeedbackItem:
    """Build event item.
    Args:
        row (dict[str, object]): Query row."""
    item = AgentFeedbackItem(**row)
    return item


def list_feedback(session: Session, project_id: int, limit: int = 50) -> RecommendationFeedbackList:
    """List recommendation feedback.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        limit (int): Result limit."""
    result = session.execute(
        text(
            """
            SELECT *
            FROM recommendation_feedback
            WHERE project_id = :project_id
            ORDER BY created_at DESC, feedback_id DESC
            LIMIT :limit
            """,
        ),
        {'project_id': project_id, 'limit': limit},
    )
    items = [feedback_item(row_dict(row)) for row in result]
    response = RecommendationFeedbackList(items=items, total=len(items))
    return response


def create_feedback(
    session: Session,
    project_id: int,
    request: RecommendationFeedbackCreate,
    user_id: int | None,
) -> RecommendationFeedbackItem:
    """Create recommendation feedback.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        request (RecommendationFeedbackCreate): Feedback payload.
        user_id (int | None): User identifier."""
    if request.feedback_status not in {'accepted', 'rejected', 'deferred', 'partially_accepted', 'accepted_no_campaign'}:
        raise HTTPException(status_code=400, detail='Unsupported feedback status.')
    result = session.execute(
        text(
            """
            INSERT INTO recommendation_feedback (
                project_id, recommendation_id, agent_run_id, strategy_id, growth_scenario_id,
                campaign_id, country_id, channel_id, feedback_status, decision_reason,
                decision_tags, decided_by_user_id
            )
            VALUES (
                :project_id, :recommendation_id, :agent_run_id, :strategy_id, :growth_scenario_id,
                :campaign_id, :country_id, :channel_id, :feedback_status, :decision_reason,
                :decision_tags, :decided_by_user_id
            )
            RETURNING *
            """,
        ),
        {'project_id': project_id, 'decided_by_user_id': user_id, **request.model_dump()},
    )
    session.commit()
    item = feedback_item(row_dict(result.first()))
    return item


def list_snapshots(session: Session, project_id: int, limit: int = 50) -> CampaignSnapshotList:
    """List campaign snapshots.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        limit (int): Result limit."""
    result = session.execute(
        text(
            """
            SELECT *
            FROM campaign_result_snapshots
            WHERE project_id = :project_id
            ORDER BY created_at DESC, campaign_result_snapshot_id DESC
            LIMIT :limit
            """,
        ),
        {'project_id': project_id, 'limit': limit},
    )
    items = [snapshot_item(row_dict(row)) for row in result]
    response = CampaignSnapshotList(items=items, total=len(items))
    return response


def calculate_rates(values: dict[str, object]) -> dict[str, object]:
    """Calculate snapshot rates.
    Args:
        values (dict[str, object]): Snapshot values."""
    spend = float(values.get('actual_spend') or 0)
    leads = float(values.get('leads') or 0)
    clients = float(values.get('clients') or 0)
    revenue = float(values.get('revenue') or 0)
    if values.get('cac') is None:
        values['cac'] = spend / clients if clients else None
    if values.get('cpl') is None:
        values['cpl'] = spend / leads if leads else None
    if values.get('roas') is None:
        values['roas'] = revenue / spend if spend else None
    if values.get('roi') is None:
        values['roi'] = (revenue - spend) / spend if spend else None
    if values.get('gross_profit') is None:
        values['gross_profit'] = revenue * 0.65 if revenue else None
    return values


def create_snapshot(session: Session, project_id: int, request: CampaignSnapshotCreate) -> CampaignSnapshotItem:
    """Create campaign snapshot.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        request (CampaignSnapshotCreate): Snapshot payload."""
    values = calculate_rates({'project_id': project_id, **request.model_dump()})
    result = session.execute(
        text(
            """
            INSERT INTO campaign_result_snapshots (
                project_id, campaign_id, country_id, channel_id, period_start, period_end,
                budget_amount, actual_spend, impressions, clicks, visits, leads, clients,
                revenue, gross_profit, cac, cpl, roas, roi, currency_code,
                data_quality_status, source_type
            )
            VALUES (
                :project_id, :campaign_id, :country_id, :channel_id, :period_start, :period_end,
                :budget_amount, :actual_spend, :impressions, :clicks, :visits, :leads, :clients,
                :revenue, :gross_profit, :cac, :cpl, :roas, :roi, :currency_code,
                :data_quality_status, :source_type
            )
            RETURNING *
            """,
        ),
        values,
    )
    session.commit()
    item = snapshot_item(row_dict(result.first()))
    return item


def aggregate_snapshot(
    session: Session,
    project_id: int,
    campaign_id: int,
    period_start: date,
    period_end: date,
) -> CampaignSnapshotItem:
    """Aggregate campaign snapshot.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        campaign_id (int): Campaign identifier.
        period_start (date): Period start.
        period_end (date): Period end."""
    result = session.execute(
        text(
            """
            SELECT
                c.campaign_id,
                c.country_id,
                NULL::BIGINT AS channel_id,
                c.currency_code,
                SUM(p.spend) AS actual_spend,
                SUM(p.impressions) AS impressions,
                SUM(p.clicks) AS clicks,
                SUM(p.visits) AS visits,
                SUM(p.leads) AS leads,
                SUM(p.clients) AS clients,
                SUM(p.revenue) AS revenue
            FROM campaigns c
            LEFT JOIN campaign_performance_daily p
                ON p.campaign_id = c.campaign_id
                AND p.project_id = c.project_id
                AND p.date BETWEEN :period_start AND :period_end
            WHERE c.project_id = :project_id AND c.campaign_id = :campaign_id
            GROUP BY c.campaign_id, c.country_id, c.currency_code
            """,
        ),
        {'project_id': project_id, 'campaign_id': campaign_id, 'period_start': period_start, 'period_end': period_end},
    ).first()
    if result is None:
        raise HTTPException(status_code=404, detail='Campaign not found.')
    payload = CampaignSnapshotCreate(
        campaign_id=campaign_id,
        country_id=row_dict(result).get('country_id'),
        channel_id=row_dict(result).get('channel_id'),
        period_start=period_start,
        period_end=period_end,
        actual_spend=row_dict(result).get('actual_spend'),
        impressions=row_dict(result).get('impressions'),
        clicks=row_dict(result).get('clicks'),
        visits=row_dict(result).get('visits'),
        leads=row_dict(result).get('leads'),
        clients=row_dict(result).get('clients'),
        revenue=row_dict(result).get('revenue'),
        currency_code=str(row_dict(result).get('currency_code') or 'EUR'),
        source_type='performance_aggregation',
    )
    item = create_snapshot(session, project_id, payload)
    return item


def fetch_snapshot(session: Session, project_id: int, snapshot_id: int) -> dict[str, object]:
    """Fetch snapshot.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        snapshot_id (int): Snapshot identifier."""
    row = session.execute(
        text('SELECT * FROM campaign_result_snapshots WHERE project_id = :project_id AND campaign_result_snapshot_id = :snapshot_id'),
        {'project_id': project_id, 'snapshot_id': snapshot_id},
    ).first()
    if row is None:
        raise HTTPException(status_code=404, detail='Campaign result snapshot not found.')
    data = row_dict(row)
    return data


def fetch_scenario(session: Session, project_id: int, scenario_id: int | None) -> dict[str, object]:
    """Fetch scenario.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        scenario_id (int | None): Scenario identifier."""
    if scenario_id is None:
        return {}
    row = session.execute(
        text('SELECT * FROM growth_scenarios WHERE project_id = :project_id AND growth_scenario_id = :scenario_id'),
        {'project_id': project_id, 'scenario_id': scenario_id},
    ).first()
    if row is None:
        raise HTTPException(status_code=404, detail='Growth scenario not found.')
    data = row_dict(row)
    return data


def metric_error(forecast_value: object, actual_value: object) -> dict[str, object]:
    """Calculate metric error.
    Args:
        forecast_value (object): Forecast metric value.
        actual_value (object): Actual metric value."""
    forecast_number = float(forecast_value or 0)
    actual_number = float(actual_value or 0)
    absolute_error = actual_number - forecast_number
    relative_error = abs(absolute_error) / abs(forecast_number) if forecast_number else None
    accuracy_score = max(0.0, 1.0 - relative_error) if relative_error is not None else None
    if forecast_number > actual_number * 1.05:
        bias_direction = 'overestimated'
    elif actual_number > forecast_number * 1.05:
        bias_direction = 'underestimated'
    else:
        bias_direction = 'accurate'
    data = {
        'forecast_value': forecast_number,
        'actual_value': actual_number,
        'absolute_error': absolute_error,
        'relative_error': relative_error,
        'accuracy_score': accuracy_score,
        'bias_direction': bias_direction,
    }
    return data


def compare_forecast(session: Session, project_id: int, request: ForecastComparisonRequest) -> ForecastComparisonList:
    """Compare forecast.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        request (ForecastComparisonRequest): Comparison request."""
    snapshot = fetch_snapshot(session, project_id, request.campaign_result_snapshot_id)
    scenario = fetch_scenario(session, project_id, request.growth_scenario_id)
    items: list[ForecastComparisonItem] = []
    for metric_name in request.metric_names:
        forecast_field = FORECAST_FIELDS.get(metric_name)
        actual_field = ACTUAL_FIELDS.get(metric_name)
        if forecast_field is None or actual_field is None:
            continue
        values = metric_error(scenario.get(forecast_field), snapshot.get(actual_field))
        result = session.execute(
            text(
                """
                INSERT INTO forecast_actual_comparisons (
                    project_id, country_id, channel_id, campaign_id, recommendation_id, strategy_id,
                    growth_scenario_id, campaign_result_snapshot_id, metric_name, forecast_value,
                    actual_value, absolute_error, relative_error, accuracy_score, bias_direction,
                    CAST(:comparison_details AS jsonb)
                )
                VALUES (
                    :project_id, :country_id, :channel_id, :campaign_id, :recommendation_id, :strategy_id,
                    :growth_scenario_id, :campaign_result_snapshot_id, :metric_name, :forecast_value,
                    :actual_value, :absolute_error, :relative_error, :accuracy_score, :bias_direction,
                    :comparison_details
                )
                RETURNING *
                """,
            ),
            {
                'project_id': project_id,
                'country_id': snapshot.get('country_id') or scenario.get('country_id'),
                'channel_id': snapshot.get('channel_id'),
                'campaign_id': snapshot.get('campaign_id'),
                'recommendation_id': request.recommendation_id,
                'strategy_id': request.strategy_id,
                'growth_scenario_id': request.growth_scenario_id,
                'campaign_result_snapshot_id': request.campaign_result_snapshot_id,
                'metric_name': metric_name,
                'comparison_details': json_text({'forecast_field': forecast_field, 'actual_field': actual_field}),
                **values,
            },
        )
        items.append(comparison_item(row_dict(result.first())))
    session.commit()
    response = ForecastComparisonList(items=items, total=len(items))
    return response


def list_comparisons(session: Session, project_id: int, limit: int = 100) -> ForecastComparisonList:
    """List comparisons.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        limit (int): Result limit."""
    result = session.execute(
        text(
            """
            SELECT *
            FROM forecast_actual_comparisons
            WHERE project_id = :project_id
            ORDER BY created_at DESC, comparison_id DESC
            LIMIT :limit
            """,
        ),
        {'project_id': project_id, 'limit': limit},
    )
    items = [comparison_item(row_dict(row)) for row in result]
    response = ForecastComparisonList(items=items, total=len(items))
    return response


def active_weights(session: Session) -> ScoringWeightVersionList:
    """List active weights.
    Args:
        session (Session): Database session."""
    result = session.execute(
        text(
            """
            SELECT *
            FROM scoring_weight_versions
            WHERE status = 'active'
            ORDER BY model_name, created_at DESC
            """,
        ),
    )
    items = [weight_item(row_dict(row)) for row in result]
    response = ScoringWeightVersionList(items=items, total=len(items))
    return response


def list_adjustments(session: Session, project_id: int) -> ScoringWeightAdjustmentList:
    """List adjustments.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier."""
    result = session.execute(
        text(
            """
            SELECT *
            FROM scoring_weight_adjustments
            WHERE project_id = :project_id
            ORDER BY created_at DESC, weight_adjustment_id DESC
            """,
        ),
        {'project_id': project_id},
    )
    items = [adjustment_item(row_dict(row)) for row in result]
    response = ScoringWeightAdjustmentList(items=items, total=len(items))
    return response


def create_adjustment(
    session: Session,
    project_id: int,
    request: ScoringWeightAdjustmentCreate,
) -> ScoringWeightAdjustmentItem:
    """Create adjustment.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        request (ScoringWeightAdjustmentCreate): Adjustment payload."""
    result = session.execute(
        text(
            """
            INSERT INTO scoring_weight_adjustments (
                project_id, model_name, current_weight_version_id, proposed_version_name,
                CAST(:proposed_weights AS jsonb), :reason, CAST(:evidence AS jsonb), :expected_improvement
            )
            VALUES (
                :project_id, :model_name, :current_weight_version_id, :proposed_version_name,
                :proposed_weights, :reason, :evidence, :expected_improvement
            )
            RETURNING *
            """,
        ),
        {
            'project_id': project_id,
            **request.model_dump(exclude={'proposed_weights', 'evidence'}),
            'proposed_weights': json_text(request.proposed_weights),
            'evidence': json_text(request.evidence or {}),
        },
    )
    session.commit()
    item = adjustment_item(row_dict(result.first()))
    return item


def apply_adjustment(session: Session, row: dict[str, object], user_id: int | None) -> None:
    """Apply adjustment.
    Args:
        session (Session): Database session.
        row (dict[str, object]): Adjustment row.
        user_id (int | None): User identifier."""
    session.execute(
        text(
            """
            UPDATE scoring_weight_versions
            SET status = 'archived'
            WHERE model_name = :model_name AND status = 'active'
            """,
        ),
        {'model_name': row['model_name']},
    )
    session.execute(
        text(
            """
            INSERT INTO scoring_weight_versions (
                model_name, version_name, weights, status, created_from_version_id,
                created_by_user_id, activated_at
            )
            VALUES (
                :model_name, :version_name, CAST(:weights AS jsonb), 'active', :created_from_version_id,
                :created_by_user_id, now()
            )
            """,
        ),
        {
            'model_name': row['model_name'],
            'version_name': row['proposed_version_name'],
            'weights': json_text(row['proposed_weights'] or {}),
            'created_from_version_id': row['current_weight_version_id'],
            'created_by_user_id': user_id,
        },
    )


def update_adjustment(
    session: Session,
    project_id: int,
    adjustment_id: int,
    request: ScoringWeightAdjustmentUpdate,
    user_id: int | None,
) -> ScoringWeightAdjustmentItem:
    """Update adjustment.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        adjustment_id (int): Adjustment identifier.
        request (ScoringWeightAdjustmentUpdate): Update payload.
        user_id (int | None): User identifier."""
    if request.status not in {'proposed', 'approved', 'rejected', 'applied', 'archived'}:
        raise HTTPException(status_code=400, detail='Unsupported adjustment status.')
    current = session.execute(
        text('SELECT * FROM scoring_weight_adjustments WHERE project_id = :project_id AND weight_adjustment_id = :adjustment_id'),
        {'project_id': project_id, 'adjustment_id': adjustment_id},
    ).first()
    if current is None:
        raise HTTPException(status_code=404, detail='Weight adjustment not found.')
    row = row_dict(current)
    if request.status == 'applied':
        apply_adjustment(session, row, user_id)
    result = session.execute(
        text(
            """
            UPDATE scoring_weight_adjustments
            SET status = :status,
                reviewed_by_user_id = :reviewed_by_user_id,
                reviewed_at = now(),
                updated_at = now()
            WHERE project_id = :project_id AND weight_adjustment_id = :adjustment_id
            RETURNING *
            """,
        ),
        {
            'project_id': project_id,
            'adjustment_id': adjustment_id,
            'status': request.status,
            'reviewed_by_user_id': user_id,
        },
    )
    session.commit()
    item = adjustment_item(row_dict(result.first()))
    return item


def recommendation_counts(session: Session, project_id: int) -> dict[str, int]:
    """Count recommendations.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier."""
    result = session.execute(
        text(
            """
            SELECT feedback_status, COUNT(*) AS row_count
            FROM recommendation_feedback
            WHERE project_id = :project_id
            GROUP BY feedback_status
            """,
        ),
        {'project_id': project_id},
    )
    counts = {str(row.feedback_status): int(row.row_count) for row in result}
    return counts


def accuracy_metrics(session: Session, project_id: int) -> tuple[float | None, dict[str, float], dict[str, dict[str, int]]]:
    """Summarize accuracy.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier."""
    result = session.execute(
        text(
            """
            SELECT metric_name, bias_direction, AVG(accuracy_score) AS avg_accuracy, COUNT(*) AS row_count
            FROM forecast_actual_comparisons
            WHERE project_id = :project_id
            GROUP BY metric_name, bias_direction
            """,
        ),
        {'project_id': project_id},
    )
    totals: dict[str, list[float]] = {}
    biases: dict[str, dict[str, int]] = {}
    for row in result:
        metric_name = str(row.metric_name)
        accuracy = float(row.avg_accuracy or 0)
        row_count = int(row.row_count or 0)
        totals.setdefault(metric_name, []).extend([accuracy] * row_count)
        biases.setdefault(metric_name, {})[str(row.bias_direction)] = row_count
    accuracy_by_metric = {metric: sum(values) / len(values) for metric, values in totals.items() if len(values) > 0}
    all_values = [value for values in totals.values() for value in values]
    average_accuracy = sum(all_values) / len(all_values) if len(all_values) > 0 else None
    return average_accuracy, accuracy_by_metric, biases


def bias_signals(biases: dict[str, dict[str, int]], bias_name: str) -> list[dict[str, object]]:
    """Build bias signals.
    Args:
        biases (dict[str, dict[str, int]]): Bias counters.
        bias_name (str): Bias name."""
    rows = [{'metric_name': metric, 'count': values.get(bias_name, 0)} for metric, values in biases.items()]
    signals = [row for row in rows if row['count'] > 0]
    signals.sort(key=lambda row: int(row['count']), reverse=True)
    return signals[:5]


def propose_weights(session: Session, project_id: int, average_accuracy: float | None, biases: dict[str, dict[str, int]]) -> None:
    """Propose weights.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        average_accuracy (float | None): Average accuracy.
        biases (dict[str, dict[str, int]]): Bias counters."""
    existing = session.execute(
        text(
            """
            SELECT 1
            FROM scoring_weight_adjustments
            WHERE project_id = :project_id AND status IN ('proposed', 'approved')
            LIMIT 1
            """,
        ),
        {'project_id': project_id},
    ).first()
    if existing is not None or average_accuracy is None or average_accuracy >= 0.70:
        return
    active = session.execute(
        text(
            """
            SELECT *
            FROM scoring_weight_versions
            WHERE model_name = 'advanced_strategy' AND status = 'active'
            ORDER BY created_at DESC
            LIMIT 1
            """,
        ),
    ).first()
    current = row_dict(active) if active is not None else {}
    request = ScoringWeightAdjustmentCreate(
        model_name='advanced_strategy',
        current_weight_version_id=current.get('weight_version_id'),
        proposed_version_name='v3_feedback',
        proposed_weights={
            'roi_potential_score': 0.27,
            'audience_fit_score': 0.24,
            'seo_opportunity_score': 0.18,
            'growth_feasibility_score': 0.18,
            'risk_score': 0.13,
        },
        reason='Forecast accuracy is below threshold. Increase quality and ROI sensitivity before scaling traffic-heavy recommendations.',
        evidence={'average_accuracy': average_accuracy, 'bias_by_metric': biases},
        expected_improvement=0.08,
    )
    create_adjustment(session, project_id, request)


def learning_summary(session: Session, project_id: int) -> LearningSummary:
    """Build learning summary.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier."""
    counts = recommendation_counts(session, project_id)
    total = sum(counts.values())
    accepted = counts.get('accepted', 0) + counts.get('partially_accepted', 0)
    acceptance_rate = accepted / total if total else None
    average_accuracy, accuracy_by_metric, biases = accuracy_metrics(session, project_id)
    propose_weights(session, project_id, average_accuracy, biases)
    proposals = list_adjustments(session, project_id).items
    response = LearningSummary(
        project_id=project_id,
        recommendation_acceptance_rate=acceptance_rate,
        recommendation_counts=counts,
        average_forecast_accuracy=average_accuracy,
        accuracy_by_metric=accuracy_by_metric,
        bias_by_metric=biases,
        overestimated_signals=bias_signals(biases, 'overestimated'),
        underestimated_signals=bias_signals(biases, 'underestimated'),
        weight_adjustment_proposals=proposals,
    )
    return response


def calibrated_confidence(session: Session, project_id: int, country_id: int | None, channel_id: int | None) -> ConfidenceResponse:
    """Calculate confidence.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        country_id (int | None): Country identifier.
        channel_id (int | None): Channel identifier."""
    average_accuracy, _, _ = accuracy_metrics(session, project_id)
    history_count = session.execute(
        text(
            """
            SELECT COUNT(*) AS row_count
            FROM campaign_result_snapshots
            WHERE project_id = :project_id
                AND (:country_id IS NULL OR country_id = :country_id)
                AND (:channel_id IS NULL OR channel_id = :channel_id)
                AND data_quality_status IN ('passed', 'warning')
            """,
        ),
        {'project_id': project_id, 'country_id': country_id, 'channel_id': channel_id},
    ).first()
    campaign_depth = min(float(history_count.row_count or 0) / 5, 1)
    components = {
        'data_quality_score': 0.85,
        'historical_forecast_accuracy': average_accuracy if average_accuracy is not None else 0.60,
        'assumptions_confidence': 0.70,
        'campaign_history_depth': campaign_depth,
        'channel_data_completeness': 0.75,
        'market_stability_score': 0.70,
    }
    confidence_score = (
        0.25 * components['data_quality_score']
        + 0.20 * components['historical_forecast_accuracy']
        + 0.20 * components['assumptions_confidence']
        + 0.15 * components['campaign_history_depth']
        + 0.10 * components['channel_data_completeness']
        + 0.10 * components['market_stability_score']
    )
    response = ConfidenceResponse(
        project_id=project_id,
        country_id=country_id,
        channel_id=channel_id,
        confidence_score=confidence_score,
        components=components,
    )
    return response


def create_agent_event(
    session: Session,
    project_id: int,
    request: AgentFeedbackCreate,
    user_id: int | None,
) -> AgentFeedbackItem:
    """Create agent event.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        request (AgentFeedbackCreate): Event payload.
        user_id (int | None): User identifier."""
    result = session.execute(
        text(
            """
            INSERT INTO agent_feedback_events (
                project_id, agent_run_id, user_id, event_type, rating, comment, tags, event_payload
            )
            VALUES (
                :project_id, :agent_run_id, :user_id, :event_type, :rating, :comment, :tags, CAST(:event_payload AS jsonb)
            )
            RETURNING *
            """,
        ),
        {
            'project_id': project_id,
            'user_id': user_id,
            **request.model_dump(exclude={'event_payload'}),
            'event_payload': json_text(request.event_payload or {}),
        },
    )
    session.commit()
    item = agent_event_item(row_dict(result.first()))
    return item


def similar_campaigns(session: Session, project_id: int, country_id: int | None, channel_id: int | None) -> CampaignSnapshotList:
    """Find similar campaigns.
    Args:
        session (Session): Database session.
        project_id (int): Project identifier.
        country_id (int | None): Country identifier.
        channel_id (int | None): Channel identifier."""
    result = session.execute(
        text(
            """
            SELECT *
            FROM campaign_result_snapshots
            WHERE project_id = :project_id
                AND (:country_id IS NULL OR country_id = :country_id)
                AND (:channel_id IS NULL OR channel_id = :channel_id)
            ORDER BY created_at DESC
            LIMIT 10
            """,
        ),
        {'project_id': project_id, 'country_id': country_id, 'channel_id': channel_id},
    )
    items = [snapshot_item(row_dict(row)) for row in result]
    response = CampaignSnapshotList(items=items, total=len(items))
    return response
