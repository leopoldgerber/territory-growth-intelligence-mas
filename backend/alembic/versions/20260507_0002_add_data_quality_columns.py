"""add_data_quality_columns

Revision ID: 20260507_0002
Revises: 20260507_0001
Create Date: 2026-05-07 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '20260507_0002'
down_revision = '20260507_0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migration.
    Args:
        None (None): No arguments are required."""
    op.add_column(
        'ingestion_runs',
        sa.Column('quality_status', sa.String(30), server_default='not_run', nullable=False),
    )
    op.add_column('data_quality_checks', sa.Column('severity', sa.String(30), nullable=True))
    op.add_column('data_quality_checks', sa.Column('message', sa.Text(), nullable=True))
    op.add_column('data_quality_checks', sa.Column('affected_rows_count', sa.BigInteger(), nullable=True))
    op.add_column('data_quality_checks', sa.Column('sample_rows', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('data_quality_checks', sa.Column('quality_dimension', sa.String(50), nullable=True))
    op.create_index('ix_dqc_run_dimension', 'data_quality_checks', ['run_id', 'quality_dimension'])
    op.create_index('ix_dqc_run_status', 'data_quality_checks', ['run_id', 'status'])


def downgrade() -> None:
    """Rollback migration.
    Args:
        None (None): No arguments are required."""
    op.drop_index('ix_dqc_run_status', table_name='data_quality_checks')
    op.drop_index('ix_dqc_run_dimension', table_name='data_quality_checks')
    op.drop_column('data_quality_checks', 'quality_dimension')
    op.drop_column('data_quality_checks', 'sample_rows')
    op.drop_column('data_quality_checks', 'affected_rows_count')
    op.drop_column('data_quality_checks', 'message')
    op.drop_column('data_quality_checks', 'severity')
    op.drop_column('ingestion_runs', 'quality_status')
