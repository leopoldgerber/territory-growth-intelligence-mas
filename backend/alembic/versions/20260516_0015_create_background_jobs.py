"""create_background_jobs

Revision ID: 20260516_0015
Revises: 20260516_0014
Create Date: 2026-05-16 00:00:00
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = '20260516_0015'
down_revision = '20260516_0014'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migration.
    Args:
        None (None): No arguments are required."""
    op.create_table(
        'background_jobs',
        sa.Column('job_id', postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column('job_type', sa.String(100), nullable=False),
        sa.Column('status', sa.String(30), server_default='queued', nullable=False),
        sa.Column('project_id', sa.BigInteger(), sa.ForeignKey('projects.project_id'), nullable=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.user_id'), nullable=True),
        sa.Column('related_entity_type', sa.String(100), nullable=True),
        sa.Column('related_entity_id', sa.BigInteger(), nullable=True),
        sa.Column('progress_percent', sa.Numeric(5, 2), server_default='0', nullable=False),
        sa.Column('current_step', sa.Text(), nullable=True),
        sa.Column('input_payload', postgresql.JSONB(), nullable=True),
        sa.Column('result_payload', postgresql.JSONB(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('celery_task_id', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_table(
        'background_job_events',
        sa.Column('event_id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('job_id', postgresql.UUID(as_uuid=False), sa.ForeignKey('background_jobs.job_id'), nullable=False),
        sa.Column('event_type', sa.String(100), nullable=False),
        sa.Column('step_name', sa.Text(), nullable=True),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('progress_percent', sa.Numeric(5, 2), nullable=True),
        sa.Column('event_payload', postgresql.JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.execute('CREATE INDEX idx_background_jobs_project_created ON background_jobs(project_id, created_at DESC)')
    op.execute('CREATE INDEX idx_background_jobs_user_created ON background_jobs(user_id, created_at DESC)')
    op.create_index('idx_background_jobs_status', 'background_jobs', ['status'])
    op.execute('CREATE INDEX idx_background_job_events_job_created ON background_job_events(job_id, created_at ASC)')


def downgrade() -> None:
    """Rollback migration.
    Args:
        None (None): No arguments are required."""
    op.drop_index('idx_background_job_events_job_created', table_name='background_job_events')
    op.drop_index('idx_background_jobs_status', table_name='background_jobs')
    op.drop_index('idx_background_jobs_user_created', table_name='background_jobs')
    op.drop_index('idx_background_jobs_project_created', table_name='background_jobs')
    op.drop_table('background_job_events')
    op.drop_table('background_jobs')
