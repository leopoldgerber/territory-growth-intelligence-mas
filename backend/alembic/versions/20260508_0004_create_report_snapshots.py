"""create_report_snapshots

Revision ID: 20260508_0004
Revises: 20260508_0003
Create Date: 2026-05-08 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '20260508_0004'
down_revision = '20260508_0003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migration.
    Args:
        None (None): No arguments are required."""
    op.create_table(
        'report_snapshots',
        sa.Column('report_id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('report_type', sa.String(100), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('country_id', sa.BigInteger(), sa.ForeignKey('dim_country.country_id'), nullable=True),
        sa.Column('region_id', sa.BigInteger(), sa.ForeignKey('dim_region.region_id'), nullable=True),
        sa.Column('domain_id', sa.BigInteger(), sa.ForeignKey('dim_domain.domain_id'), nullable=True),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('report_status', sa.String(30), nullable=True),
        sa.Column('report_markdown', sa.Text(), nullable=True),
        sa.Column('report_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('input_params', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('data_quality_status', sa.String(30), nullable=True),
        sa.Column('calculation_version', sa.String(50), nullable=True),
        sa.Column('generator_version', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index('ix_report_country_period', 'report_snapshots', ['country_id', 'period_start', 'period_end'])
    op.create_index('ix_report_type_created', 'report_snapshots', ['report_type', 'created_at'])


def downgrade() -> None:
    """Rollback migration.
    Args:
        None (None): No arguments are required."""
    op.drop_index('ix_report_type_created', table_name='report_snapshots')
    op.drop_index('ix_report_country_period', table_name='report_snapshots')
    op.drop_table('report_snapshots')
