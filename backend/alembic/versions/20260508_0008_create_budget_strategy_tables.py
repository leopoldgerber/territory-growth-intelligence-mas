"""create_budget_strategy_tables

Revision ID: 20260508_0008
Revises: 20260508_0007
Create Date: 2026-05-08 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '20260508_0008'
down_revision = '20260508_0007'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migration.
    Args:
        None (None): No arguments are required."""
    op.create_table(
        'budget_strategy_runs',
        sa.Column('strategy_id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('country_id', sa.BigInteger(), sa.ForeignKey('dim_country.country_id'), nullable=False),
        sa.Column('region_id', sa.BigInteger(), sa.ForeignKey('dim_region.region_id'), nullable=True),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('budget_amount', sa.Numeric(20, 4), nullable=False),
        sa.Column('currency_code', sa.String(3), nullable=False),
        sa.Column('campaign_goal', sa.String(50), nullable=True),
        sa.Column('risk_appetite', sa.String(50), nullable=True),
        sa.Column('opportunity_score_id', sa.BigInteger(), sa.ForeignKey('country_opportunity_scores.opportunity_score_id'), nullable=True),
        sa.Column('strategy_status', sa.String(30), nullable=True),
        sa.Column('recommended_strategy_type', sa.String(100), nullable=True),
        sa.Column('total_expected_traffic', sa.Numeric(20, 4), nullable=True),
        sa.Column('total_expected_leads', sa.Numeric(20, 4), nullable=True),
        sa.Column('total_expected_clients', sa.Numeric(20, 4), nullable=True),
        sa.Column('confidence_score', sa.Numeric(10, 6), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('recommendations', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('risks', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('assumptions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('input_params', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('calculation_version', sa.String(50), nullable=False),
        sa.Column('data_quality_status', sa.String(30), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_table(
        'budget_strategy_allocations',
        sa.Column('allocation_id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('strategy_id', sa.BigInteger(), sa.ForeignKey('budget_strategy_runs.strategy_id'), nullable=False),
        sa.Column('channel_id', sa.BigInteger(), sa.ForeignKey('dim_channel.channel_id'), nullable=True),
        sa.Column('channel_code', sa.String(50), nullable=False),
        sa.Column('channel_name', sa.Text(), nullable=True),
        sa.Column('budget_amount', sa.Numeric(20, 4), nullable=True),
        sa.Column('budget_share', sa.Numeric(10, 6), nullable=True),
        sa.Column('rationale', sa.Text(), nullable=True),
        sa.Column('expected_traffic', sa.Numeric(20, 4), nullable=True),
        sa.Column('expected_leads', sa.Numeric(20, 4), nullable=True),
        sa.Column('expected_clients', sa.Numeric(20, 4), nullable=True),
        sa.Column('priority', sa.String(30), nullable=True),
        sa.Column('risk_level', sa.String(30), nullable=True),
        sa.Column('test_hypothesis', sa.Text(), nullable=True),
        sa.Column('success_metric', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_bsr_country_period', 'budget_strategy_runs', ['country_id', 'period_start', 'period_end'])
    op.create_index('ix_bsr_status', 'budget_strategy_runs', ['strategy_status'])
    op.create_index('ix_bsa_strategy', 'budget_strategy_allocations', ['strategy_id'])


def downgrade() -> None:
    """Rollback migration.
    Args:
        None (None): No arguments are required."""
    op.drop_index('ix_bsa_strategy', table_name='budget_strategy_allocations')
    op.drop_index('ix_bsr_status', table_name='budget_strategy_runs')
    op.drop_index('ix_bsr_country_period', table_name='budget_strategy_runs')
    op.drop_table('budget_strategy_allocations')
    op.drop_table('budget_strategy_runs')
