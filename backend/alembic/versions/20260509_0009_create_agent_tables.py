"""create_agent_tables

Revision ID: 20260509_0009
Revises: 20260508_0008
Create Date: 2026-05-09 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '20260509_0009'
down_revision = '20260508_0008'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migration.
    Args:
        None (None): No arguments are required."""
    op.create_table(
        'agent_runs',
        sa.Column('agent_run_id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('user_query', sa.Text(), nullable=False),
        sa.Column('normalized_query', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('run_status', sa.String(30), nullable=True),
        sa.Column('run_type', sa.String(100), nullable=True),
        sa.Column('country_id', sa.BigInteger(), sa.ForeignKey('dim_country.country_id'), nullable=True),
        sa.Column('domain_id', sa.BigInteger(), sa.ForeignKey('dim_domain.domain_id'), nullable=True),
        sa.Column('period_start', sa.Date(), nullable=True),
        sa.Column('period_end', sa.Date(), nullable=True),
        sa.Column('budget_amount', sa.Numeric(20, 4), nullable=True),
        sa.Column('currency_code', sa.String(3), nullable=True),
        sa.Column('campaign_goal', sa.String(50), nullable=True),
        sa.Column('input_params', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('planner_output', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('final_answer', sa.Text(), nullable=True),
        sa.Column('final_report_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('output_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('confidence_score', sa.Numeric(10, 6), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        'agent_steps',
        sa.Column('agent_step_id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('agent_run_id', sa.BigInteger(), sa.ForeignKey('agent_runs.agent_run_id'), nullable=False),
        sa.Column('step_order', sa.Integer(), nullable=False),
        sa.Column('agent_name', sa.String(100), nullable=False),
        sa.Column('step_type', sa.String(100), nullable=True),
        sa.Column('step_status', sa.String(30), nullable=True),
        sa.Column('input_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('output_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        'agent_evidence',
        sa.Column('evidence_id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('agent_run_id', sa.BigInteger(), sa.ForeignKey('agent_runs.agent_run_id'), nullable=False),
        sa.Column('agent_step_id', sa.BigInteger(), sa.ForeignKey('agent_steps.agent_step_id'), nullable=True),
        sa.Column('evidence_type', sa.String(100), nullable=True),
        sa.Column('source_name', sa.Text(), nullable=True),
        sa.Column('source_ref', sa.Text(), nullable=True),
        sa.Column('country_id', sa.BigInteger(), sa.ForeignKey('dim_country.country_id'), nullable=True),
        sa.Column('domain_id', sa.BigInteger(), sa.ForeignKey('dim_domain.domain_id'), nullable=True),
        sa.Column('metric_name', sa.Text(), nullable=True),
        sa.Column('metric_value', sa.Numeric(20, 6), nullable=True),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_table(
        'agent_insights',
        sa.Column('insight_id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('agent_run_id', sa.BigInteger(), sa.ForeignKey('agent_runs.agent_run_id'), nullable=False),
        sa.Column('agent_name', sa.String(100), nullable=True),
        sa.Column('insight_type', sa.String(100), nullable=True),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('country_id', sa.BigInteger(), sa.ForeignKey('dim_country.country_id'), nullable=True),
        sa.Column('domain_id', sa.BigInteger(), sa.ForeignKey('dim_domain.domain_id'), nullable=True),
        sa.Column('channel_id', sa.BigInteger(), sa.ForeignKey('dim_channel.channel_id'), nullable=True),
        sa.Column('severity', sa.String(30), nullable=True),
        sa.Column('confidence_score', sa.Numeric(10, 6), nullable=True),
        sa.Column('evidence_ids', postgresql.ARRAY(sa.BigInteger()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_table(
        'agent_recommendations',
        sa.Column('recommendation_id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('agent_run_id', sa.BigInteger(), sa.ForeignKey('agent_runs.agent_run_id'), nullable=False),
        sa.Column('recommendation_type', sa.String(100), nullable=True),
        sa.Column('priority', sa.String(30), nullable=True),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('rationale', sa.Text(), nullable=True),
        sa.Column('country_id', sa.BigInteger(), sa.ForeignKey('dim_country.country_id'), nullable=True),
        sa.Column('channel_id', sa.BigInteger(), sa.ForeignKey('dim_channel.channel_id'), nullable=True),
        sa.Column('budget_amount', sa.Numeric(20, 4), nullable=True),
        sa.Column('currency_code', sa.String(3), nullable=True),
        sa.Column('expected_impact', sa.String(50), nullable=True),
        sa.Column('confidence_score', sa.Numeric(10, 6), nullable=True),
        sa.Column('evidence_ids', postgresql.ARRAY(sa.BigInteger()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_agent_runs_status', 'agent_runs', ['run_status'])
    op.create_index('ix_agent_steps_run', 'agent_steps', ['agent_run_id'])
    op.create_index('ix_agent_evidence_run', 'agent_evidence', ['agent_run_id'])
    op.create_index('ix_agent_insights_run', 'agent_insights', ['agent_run_id'])
    op.create_index('ix_agent_recommendations_run', 'agent_recommendations', ['agent_run_id'])


def downgrade() -> None:
    """Rollback migration.
    Args:
        None (None): No arguments are required."""
    op.drop_index('ix_agent_recommendations_run', table_name='agent_recommendations')
    op.drop_index('ix_agent_insights_run', table_name='agent_insights')
    op.drop_index('ix_agent_evidence_run', table_name='agent_evidence')
    op.drop_index('ix_agent_steps_run', table_name='agent_steps')
    op.drop_index('ix_agent_runs_status', table_name='agent_runs')
    op.drop_table('agent_recommendations')
    op.drop_table('agent_insights')
    op.drop_table('agent_evidence')
    op.drop_table('agent_steps')
    op.drop_table('agent_runs')
