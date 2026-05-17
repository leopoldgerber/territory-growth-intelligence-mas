"""create_feedback_loop_tables

Revision ID: 20260516_0019
Revises: 20260516_0018
Create Date: 2026-05-16 00:19:00
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = '20260516_0019'
down_revision = '20260516_0018'
branch_labels = None
depends_on = None


def id_column(name: str) -> sa.Column:
    """Build id column.
    Args:
        name (str): Column name."""
    column = sa.Column(name, sa.BigInteger(), sa.Identity(), primary_key=True)
    return column


def now_column(name: str = 'created_at') -> sa.Column:
    """Build timestamp column.
    Args:
        name (str): Column name."""
    column = sa.Column(name, sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    return column


def num_column(name: str, precision: int = 20, scale: int = 6) -> sa.Column:
    """Build numeric column.
    Args:
        name (str): Column name.
        precision (int): Numeric precision.
        scale (int): Numeric scale."""
    column = sa.Column(name, sa.Numeric(precision, scale), nullable=True)
    return column


def create_feedback() -> None:
    """Create recommendation feedback.
    Args:
        None (None): No arguments are required."""
    op.create_table(
        'recommendation_feedback',
        id_column('feedback_id'),
        sa.Column('project_id', sa.BigInteger(), sa.ForeignKey('projects.project_id'), nullable=False),
        sa.Column('recommendation_id', sa.BigInteger(), sa.ForeignKey('agent_recommendations.recommendation_id'), nullable=True),
        sa.Column('agent_run_id', sa.BigInteger(), sa.ForeignKey('agent_runs.agent_run_id'), nullable=True),
        sa.Column('strategy_id', sa.BigInteger(), sa.ForeignKey('budget_strategy_runs.strategy_id'), nullable=True),
        sa.Column('growth_scenario_id', sa.BigInteger(), sa.ForeignKey('growth_scenarios.growth_scenario_id'), nullable=True),
        sa.Column('campaign_id', sa.BigInteger(), sa.ForeignKey('campaigns.campaign_id'), nullable=True),
        sa.Column('country_id', sa.BigInteger(), sa.ForeignKey('dim_country.country_id'), nullable=True),
        sa.Column('channel_id', sa.BigInteger(), sa.ForeignKey('dim_channel.channel_id'), nullable=True),
        sa.Column('feedback_status', sa.String(30), nullable=False),
        sa.Column('decision_reason', sa.Text(), nullable=True),
        sa.Column('decision_tags', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('decided_by_user_id', sa.BigInteger(), sa.ForeignKey('users.user_id'), nullable=True),
        now_column('decided_at'),
        now_column(),
    )


def create_snapshots() -> None:
    """Create campaign snapshots.
    Args:
        None (None): No arguments are required."""
    op.create_table(
        'campaign_result_snapshots',
        id_column('campaign_result_snapshot_id'),
        sa.Column('project_id', sa.BigInteger(), sa.ForeignKey('projects.project_id'), nullable=False),
        sa.Column('campaign_id', sa.BigInteger(), sa.ForeignKey('campaigns.campaign_id'), nullable=False),
        sa.Column('country_id', sa.BigInteger(), sa.ForeignKey('dim_country.country_id'), nullable=True),
        sa.Column('channel_id', sa.BigInteger(), sa.ForeignKey('dim_channel.channel_id'), nullable=True),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        num_column('budget_amount', 20, 4),
        num_column('actual_spend', 20, 4),
        num_column('impressions', 20, 4),
        num_column('clicks', 20, 4),
        num_column('visits', 20, 4),
        num_column('leads', 20, 4),
        num_column('clients', 20, 4),
        num_column('revenue', 20, 4),
        num_column('gross_profit', 20, 4),
        num_column('cac', 20, 4),
        num_column('cpl', 20, 4),
        num_column('roas', 10, 6),
        num_column('roi', 10, 6),
        sa.Column('currency_code', sa.String(3), server_default='EUR', nullable=False),
        sa.Column('data_quality_status', sa.String(30), server_default='passed', nullable=False),
        sa.Column('source_type', sa.String(50), server_default='manual', nullable=False),
        now_column(),
    )


def create_comparisons() -> None:
    """Create forecast comparisons.
    Args:
        None (None): No arguments are required."""
    op.create_table(
        'forecast_actual_comparisons',
        id_column('comparison_id'),
        sa.Column('project_id', sa.BigInteger(), sa.ForeignKey('projects.project_id'), nullable=False),
        sa.Column('country_id', sa.BigInteger(), sa.ForeignKey('dim_country.country_id'), nullable=True),
        sa.Column('channel_id', sa.BigInteger(), sa.ForeignKey('dim_channel.channel_id'), nullable=True),
        sa.Column('campaign_id', sa.BigInteger(), sa.ForeignKey('campaigns.campaign_id'), nullable=True),
        sa.Column('recommendation_id', sa.BigInteger(), sa.ForeignKey('agent_recommendations.recommendation_id'), nullable=True),
        sa.Column('strategy_id', sa.BigInteger(), sa.ForeignKey('budget_strategy_runs.strategy_id'), nullable=True),
        sa.Column('growth_scenario_id', sa.BigInteger(), sa.ForeignKey('growth_scenarios.growth_scenario_id'), nullable=True),
        sa.Column('campaign_result_snapshot_id', sa.BigInteger(), sa.ForeignKey('campaign_result_snapshots.campaign_result_snapshot_id'), nullable=False),
        sa.Column('metric_name', sa.String(100), nullable=False),
        num_column('forecast_value'),
        num_column('actual_value'),
        num_column('absolute_error'),
        num_column('relative_error', 10, 6),
        num_column('accuracy_score', 10, 6),
        sa.Column('bias_direction', sa.String(30), nullable=False),
        sa.Column('comparison_details', postgresql.JSONB(), nullable=True),
        now_column(),
    )


def create_weights() -> None:
    """Create weight tables.
    Args:
        None (None): No arguments are required."""
    op.create_table(
        'scoring_weight_versions',
        id_column('weight_version_id'),
        sa.Column('model_name', sa.String(100), nullable=False),
        sa.Column('version_name', sa.String(50), nullable=False),
        sa.Column('weights', postgresql.JSONB(), nullable=False),
        sa.Column('status', sa.String(30), server_default='draft', nullable=False),
        sa.Column('created_from_version_id', sa.BigInteger(), sa.ForeignKey('scoring_weight_versions.weight_version_id'), nullable=True),
        sa.Column('created_by_user_id', sa.BigInteger(), sa.ForeignKey('users.user_id'), nullable=True),
        now_column(),
        sa.Column('activated_at', sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint('model_name', 'version_name', name='uq_scoring_weight_version'),
    )
    op.create_table(
        'scoring_weight_adjustments',
        id_column('weight_adjustment_id'),
        sa.Column('project_id', sa.BigInteger(), sa.ForeignKey('projects.project_id'), nullable=False),
        sa.Column('model_name', sa.String(100), nullable=False),
        sa.Column('current_weight_version_id', sa.BigInteger(), sa.ForeignKey('scoring_weight_versions.weight_version_id'), nullable=True),
        sa.Column('proposed_version_name', sa.String(50), nullable=False),
        sa.Column('proposed_weights', postgresql.JSONB(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('evidence', postgresql.JSONB(), nullable=True),
        num_column('expected_improvement', 10, 6),
        sa.Column('status', sa.String(30), server_default='proposed', nullable=False),
        sa.Column('reviewed_by_user_id', sa.BigInteger(), sa.ForeignKey('users.user_id'), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        now_column(),
        now_column('updated_at'),
    )


def create_events() -> None:
    """Create agent events.
    Args:
        None (None): No arguments are required."""
    op.create_table(
        'agent_feedback_events',
        id_column('agent_feedback_event_id'),
        sa.Column('project_id', sa.BigInteger(), sa.ForeignKey('projects.project_id'), nullable=False),
        sa.Column('agent_run_id', sa.BigInteger(), sa.ForeignKey('agent_runs.agent_run_id'), nullable=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.user_id'), nullable=True),
        sa.Column('event_type', sa.String(100), nullable=False),
        num_column('rating', 10, 6),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('tags', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('event_payload', postgresql.JSONB(), nullable=True),
        now_column(),
    )


def create_indexes() -> None:
    """Create indexes.
    Args:
        None (None): No arguments are required."""
    op.create_index('ix_recommendation_feedback_project', 'recommendation_feedback', ['project_id', 'created_at'])
    op.create_index('ix_recommendation_feedback_status', 'recommendation_feedback', ['feedback_status'])
    op.create_index('ix_campaign_snapshots_project', 'campaign_result_snapshots', ['project_id', 'created_at'])
    op.create_index('ix_campaign_snapshots_campaign', 'campaign_result_snapshots', ['campaign_id', 'period_start', 'period_end'])
    op.create_index('ix_forecast_comparisons_project', 'forecast_actual_comparisons', ['project_id', 'created_at'])
    op.create_index('ix_forecast_comparisons_metric', 'forecast_actual_comparisons', ['metric_name', 'bias_direction'])
    op.create_index('ix_weight_versions_model_status', 'scoring_weight_versions', ['model_name', 'status'])
    op.create_index('ix_weight_adjustments_project_status', 'scoring_weight_adjustments', ['project_id', 'status'])
    op.create_index('ix_agent_feedback_events_project', 'agent_feedback_events', ['project_id', 'created_at'])


def seed_weights() -> None:
    """Seed initial weights.
    Args:
        None (None): No arguments are required."""
    weight_rows = [
        {
            'model_name': 'opportunity_score',
            'version_name': 'v1',
            'weights': {'traffic_score': 0.25, 'competition_score': 0.20, 'quality_score': 0.25, 'channel_gap_score': 0.15, 'volatility_score': 0.15},
        },
        {
            'model_name': 'advanced_strategy',
            'version_name': 'v2',
            'weights': {'roi_potential_score': 0.25, 'audience_fit_score': 0.20, 'seo_opportunity_score': 0.20, 'growth_feasibility_score': 0.20, 'risk_score': 0.15},
        },
        {
            'model_name': 'budget_strategy',
            'version_name': 'v1',
            'weights': {'expected_roi': 0.30, 'cac_fit': 0.25, 'channel_stability': 0.20, 'market_priority': 0.15, 'risk_control': 0.10},
        },
    ]
    op.bulk_insert(
        sa.table(
            'scoring_weight_versions',
            sa.column('model_name', sa.String),
            sa.column('version_name', sa.String),
            sa.column('weights', postgresql.JSONB),
            sa.column('status', sa.String),
        ),
        [{**row, 'status': 'active'} for row in weight_rows],
    )


def upgrade() -> None:
    """Apply migration.
    Args:
        None (None): No arguments are required."""
    create_feedback()
    create_snapshots()
    create_comparisons()
    create_weights()
    create_events()
    create_indexes()
    seed_weights()


def downgrade() -> None:
    """Rollback migration.
    Args:
        None (None): No arguments are required."""
    op.drop_table('agent_feedback_events')
    op.drop_table('scoring_weight_adjustments')
    op.drop_table('scoring_weight_versions')
    op.drop_table('forecast_actual_comparisons')
    op.drop_table('campaign_result_snapshots')
    op.drop_table('recommendation_feedback')
