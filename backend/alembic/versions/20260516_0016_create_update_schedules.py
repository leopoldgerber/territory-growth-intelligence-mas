"""create_update_schedules

Revision ID: 20260516_0016
Revises: 20260516_0015
Create Date: 2026-05-16 00:00:00
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = '20260516_0016'
down_revision = '20260516_0015'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migration.
    Args:
        None (None): No arguments are required."""
    op.create_table(
        'update_schedules',
        sa.Column('schedule_id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('project_id', sa.BigInteger(), sa.ForeignKey('projects.project_id'), nullable=True),
        sa.Column('schedule_name', sa.Text(), nullable=False),
        sa.Column('source_id', sa.BigInteger(), nullable=True),
        sa.Column('update_type', sa.String(100), server_default='file_import', nullable=False),
        sa.Column('frequency', sa.String(50), server_default='weekly', nullable=False),
        sa.Column('cron_expression', sa.Text(), nullable=True),
        sa.Column('timezone', sa.Text(), server_default='UTC', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('lookback_days', sa.Integer(), server_default='14', nullable=False),
        sa.Column('default_granularity', sa.String(30), server_default='daily', nullable=False),
        sa.Column('config', postgresql.JSONB(), nullable=True),
        sa.Column('next_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by_user_id', sa.BigInteger(), sa.ForeignKey('users.user_id'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_table(
        'update_runs',
        sa.Column('update_run_id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('schedule_id', sa.BigInteger(), sa.ForeignKey('update_schedules.schedule_id'), nullable=True),
        sa.Column('project_id', sa.BigInteger(), sa.ForeignKey('projects.project_id'), nullable=True),
        sa.Column('job_id', postgresql.UUID(as_uuid=False), sa.ForeignKey('background_jobs.job_id'), nullable=True),
        sa.Column('ingestion_run_id', sa.BigInteger(), sa.ForeignKey('ingestion_runs.run_id'), nullable=True),
        sa.Column('run_type', sa.String(100), server_default='manual', nullable=False),
        sa.Column('status', sa.String(30), server_default='queued', nullable=False),
        sa.Column('period_start', sa.Date(), nullable=True),
        sa.Column('period_end', sa.Date(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('files_imported_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('rows_loaded_count', sa.BigInteger(), server_default='0', nullable=False),
        sa.Column('quality_status', sa.String(30), server_default='unknown', nullable=False),
        sa.Column('metrics_recalculated', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('scores_recalculated', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('alerts_detected_count', sa.Integer(), server_default='0', nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('result_payload', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_table(
        'update_run_steps',
        sa.Column('update_run_step_id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('update_run_id', sa.BigInteger(), sa.ForeignKey('update_runs.update_run_id'), nullable=False),
        sa.Column('step_order', sa.Integer(), nullable=False),
        sa.Column('step_name', sa.String(100), nullable=False),
        sa.Column('step_status', sa.String(30), server_default='queued', nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('details', postgresql.JSONB(), nullable=True),
    )
    op.execute('CREATE INDEX idx_update_schedules_project_active ON update_schedules(project_id, is_active)')
    op.execute('CREATE INDEX idx_update_schedules_next_run ON update_schedules(is_active, next_run_at)')
    op.execute('CREATE INDEX idx_update_runs_project_created ON update_runs(project_id, created_at DESC)')
    op.execute('CREATE INDEX idx_update_runs_schedule_created ON update_runs(schedule_id, created_at DESC)')
    op.create_index('idx_update_runs_status', 'update_runs', ['status'])
    op.create_index('idx_update_run_steps_run', 'update_run_steps', ['update_run_id'])


def downgrade() -> None:
    """Rollback migration.
    Args:
        None (None): No arguments are required."""
    op.drop_index('idx_update_run_steps_run', table_name='update_run_steps')
    op.drop_index('idx_update_runs_status', table_name='update_runs')
    op.drop_index('idx_update_runs_schedule_created', table_name='update_runs')
    op.drop_index('idx_update_runs_project_created', table_name='update_runs')
    op.drop_index('idx_update_schedules_next_run', table_name='update_schedules')
    op.drop_index('idx_update_schedules_project_active', table_name='update_schedules')
    op.drop_table('update_run_steps')
    op.drop_table('update_runs')
    op.drop_table('update_schedules')
