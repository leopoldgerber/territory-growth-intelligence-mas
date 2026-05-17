"""create_advanced_strategy_tables

Revision ID: 20260516_0018
Revises: 20260516_0017
Create Date: 2026-05-16 00:18:00
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = '20260516_0018'
down_revision = '20260516_0017'
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


def num_column(name: str, precision: int = 20, scale: int = 4) -> sa.Column:
    """Build numeric column.
    Args:
        name (str): Column name.
        precision (int): Numeric precision.
        scale (int): Numeric scale."""
    column = sa.Column(name, sa.Numeric(precision, scale), nullable=True)
    return column


def create_scores() -> None:
    """Create score table.
    Args:
        None (None): No arguments are required."""
    op.create_table(
        'advanced_country_scores',
        id_column('advanced_score_id'),
        sa.Column('project_id', sa.BigInteger(), sa.ForeignKey('projects.project_id'), nullable=False),
        sa.Column('country_id', sa.BigInteger(), sa.ForeignKey('dim_country.country_id'), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        num_column('competitor_threat_score', 10, 6),
        num_column('market_maturity_score', 10, 6),
        num_column('paid_dependency_score', 10, 6),
        num_column('seo_opportunity_score', 10, 6),
        num_column('audience_fit_score', 10, 6),
        num_column('roi_potential_score', 10, 6),
        num_column('growth_feasibility_score', 10, 6),
        num_column('strategic_priority_score', 10, 6),
        sa.Column('recommended_strategy_type', sa.String(100), nullable=True),
        sa.Column('score_breakdown', postgresql.JSONB(), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('calculation_version', sa.String(50), server_default='v2', nullable=False),
        now_column(),
        sa.UniqueConstraint('project_id', 'country_id', 'period_start', 'period_end', 'calculation_version', name='uq_advanced_country_score'),
    )


def create_scenarios() -> None:
    """Create scenario table.
    Args:
        None (None): No arguments are required."""
    op.create_table(
        'growth_scenarios',
        id_column('growth_scenario_id'),
        sa.Column('project_id', sa.BigInteger(), sa.ForeignKey('projects.project_id'), nullable=False),
        sa.Column('country_id', sa.BigInteger(), sa.ForeignKey('dim_country.country_id'), nullable=False),
        sa.Column('advanced_score_id', sa.BigInteger(), sa.ForeignKey('advanced_country_scores.advanced_score_id'), nullable=True),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('forecast_start', sa.Date(), nullable=True),
        sa.Column('forecast_end', sa.Date(), nullable=True),
        sa.Column('scenario_name', sa.String(50), nullable=False),
        num_column('budget_amount'),
        sa.Column('currency_code', sa.String(3), server_default='EUR', nullable=False),
        num_column('expected_traffic_capture'),
        num_column('expected_leads'),
        num_column('expected_clients'),
        num_column('expected_revenue'),
        num_column('expected_gross_profit'),
        num_column('estimated_cac'),
        num_column('estimated_roi', 10, 6),
        sa.Column('payback_period_days', sa.Integer(), nullable=True),
        num_column('confidence_score', 10, 6),
        sa.Column('assumptions', postgresql.JSONB(), nullable=True),
        sa.Column('scenario_details', postgresql.JSONB(), nullable=True),
        sa.Column('calculation_version', sa.String(50), server_default='v2', nullable=False),
        now_column(),
    )


def create_allocations() -> None:
    """Create allocation table.
    Args:
        None (None): No arguments are required."""
    op.create_table(
        'advanced_budget_allocations',
        id_column('advanced_allocation_id'),
        sa.Column('growth_scenario_id', sa.BigInteger(), sa.ForeignKey('growth_scenarios.growth_scenario_id'), nullable=False),
        sa.Column('project_id', sa.BigInteger(), sa.ForeignKey('projects.project_id'), nullable=False),
        sa.Column('country_id', sa.BigInteger(), sa.ForeignKey('dim_country.country_id'), nullable=False),
        sa.Column('channel_id', sa.BigInteger(), sa.ForeignKey('dim_channel.channel_id'), nullable=True),
        sa.Column('allocation_category', sa.String(100), nullable=False),
        num_column('budget_share', 10, 6),
        num_column('budget_amount'),
        num_column('expected_traffic'),
        num_column('expected_leads'),
        num_column('expected_clients'),
        num_column('expected_revenue'),
        num_column('estimated_cac'),
        sa.Column('rationale', sa.Text(), nullable=True),
        sa.Column('risk_level', sa.String(30), nullable=True),
        sa.Column('success_metric', sa.Text(), nullable=True),
        now_column(),
    )


def create_indexes() -> None:
    """Create indexes.
    Args:
        None (None): No arguments are required."""
    op.create_index('ix_advanced_scores_project_country', 'advanced_country_scores', ['project_id', 'country_id'])
    op.create_index('ix_growth_scenarios_project_created', 'growth_scenarios', ['project_id', 'created_at'])
    op.create_index('ix_growth_scenarios_country_period', 'growth_scenarios', ['country_id', 'period_start', 'period_end'])
    op.create_index('ix_advanced_allocations_scenario', 'advanced_budget_allocations', ['growth_scenario_id'])


def upgrade() -> None:
    """Apply migration.
    Args:
        None (None): No arguments are required."""
    create_scores()
    create_scenarios()
    create_allocations()
    create_indexes()


def downgrade() -> None:
    """Rollback migration.
    Args:
        None (None): No arguments are required."""
    op.drop_table('advanced_budget_allocations')
    op.drop_table('growth_scenarios')
    op.drop_table('advanced_country_scores')
