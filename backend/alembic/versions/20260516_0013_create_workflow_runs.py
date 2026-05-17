"""create_workflow_runs

Revision ID: 20260516_0013
Revises: 20260516_0012
Create Date: 2026-05-16 00:00:00
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = '20260516_0013'
down_revision = '20260516_0012'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migration.
    Args:
        None (None): No arguments are required."""
    op.create_table(
        'workflow_runs',
        sa.Column('workflow_run_id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('workflow_type', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('country_id', sa.BigInteger(), sa.ForeignKey('dim_country.country_id'), nullable=True),
        sa.Column('period_start', sa.Date(), nullable=True),
        sa.Column('period_end', sa.Date(), nullable=True),
        sa.Column('budget_amount', sa.Numeric(20, 4), nullable=True),
        sa.Column('currency_code', sa.String(length=3), nullable=True),
        sa.Column('campaign_goal', sa.String(length=50), nullable=True),
        sa.Column('risk_appetite', sa.String(length=50), nullable=True),
        sa.Column('agent_run_id', sa.BigInteger(), sa.ForeignKey('agent_runs.agent_run_id'), nullable=True),
        sa.Column('report_id', sa.BigInteger(), sa.ForeignKey('report_snapshots.report_id'), nullable=True),
        sa.Column('strategy_id', sa.BigInteger(), sa.ForeignKey('budget_strategy_runs.strategy_id'), nullable=True),
        sa.Column('summary_id', sa.BigInteger(), sa.ForeignKey('saved_summaries.summary_id'), nullable=True),
        sa.Column('input_params', postgresql.JSONB(), nullable=True),
        sa.Column('result_payload', postgresql.JSONB(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_workflow_runs_status', 'workflow_runs', ['status'])
    op.create_index('idx_workflow_runs_country_period', 'workflow_runs', ['country_id', 'period_start', 'period_end'])
    op.create_index('idx_workflow_runs_created_at', 'workflow_runs', ['created_at'])


def downgrade() -> None:
    """Rollback migration.
    Args:
        None (None): No arguments are required."""
    op.drop_index('idx_workflow_runs_created_at', table_name='workflow_runs')
    op.drop_index('idx_workflow_runs_country_period', table_name='workflow_runs')
    op.drop_index('idx_workflow_runs_status', table_name='workflow_runs')
    op.drop_table('workflow_runs')
