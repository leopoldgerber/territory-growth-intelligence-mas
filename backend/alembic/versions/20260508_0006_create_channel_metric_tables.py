"""create_channel_metric_tables

Revision ID: 20260508_0006
Revises: 20260508_0005
Create Date: 2026-05-08 00:00:00
"""
from alembic import op
import sqlalchemy as sa


revision = '20260508_0006'
down_revision = '20260508_0005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migration.
    Args:
        None (None): No arguments are required."""
    op.create_table(
        'metric_channel_period',
        sa.Column('channel_period_metric_id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('scope_type', sa.String(30), nullable=False),
        sa.Column('country_id', sa.BigInteger(), sa.ForeignKey('dim_country.country_id'), nullable=True),
        sa.Column('domain_id', sa.BigInteger(), sa.ForeignKey('dim_domain.domain_id'), nullable=True),
        sa.Column('company_id', sa.BigInteger(), sa.ForeignKey('dim_company.company_id'), nullable=True),
        sa.Column('channel_id', sa.BigInteger(), sa.ForeignKey('dim_channel.channel_id'), nullable=False),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('traffic', sa.Numeric(20, 4), nullable=True),
        sa.Column('traffic_share', sa.Numeric(10, 6), nullable=True),
        sa.Column('growth_rate', sa.Numeric(10, 6), nullable=True),
        sa.Column('stability_score', sa.Numeric(10, 6), nullable=True),
        sa.Column('is_dominant_channel', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('dependency_score', sa.Numeric(10, 6), nullable=True),
        sa.Column('calculation_version', sa.String(50), nullable=False),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint(
            'scope_type',
            'country_id',
            'domain_id',
            'channel_id',
            'period_start',
            'period_end',
            'calculation_version',
            name='uq_metric_channel_period',
        ),
    )
    op.create_table(
        'metric_journey_source_period',
        sa.Column('journey_source_period_metric_id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('scope_type', sa.String(30), nullable=False),
        sa.Column('country_id', sa.BigInteger(), sa.ForeignKey('dim_country.country_id'), nullable=True),
        sa.Column('domain_id', sa.BigInteger(), sa.ForeignKey('dim_domain.domain_id'), nullable=True),
        sa.Column('company_id', sa.BigInteger(), sa.ForeignKey('dim_company.company_id'), nullable=True),
        sa.Column('journey_source_id', sa.BigInteger(), sa.ForeignKey('dim_journey_source.journey_source_id'), nullable=False),
        sa.Column('channel_id', sa.BigInteger(), sa.ForeignKey('dim_channel.channel_id'), nullable=True),
        sa.Column('source_name', sa.Text(), nullable=True),
        sa.Column('source_type', sa.String(100), nullable=True),
        sa.Column('traffic_type', sa.String(100), nullable=True),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('traffic', sa.Numeric(20, 4), nullable=True),
        sa.Column('traffic_share', sa.Numeric(10, 6), nullable=True),
        sa.Column('growth_rate', sa.Numeric(10, 6), nullable=True),
        sa.Column('stability_score', sa.Numeric(10, 6), nullable=True),
        sa.Column('calculation_version', sa.String(50), nullable=False),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint(
            'scope_type',
            'country_id',
            'domain_id',
            'journey_source_id',
            'period_start',
            'period_end',
            'calculation_version',
            name='uq_metric_journey_source_period',
        ),
    )
    op.create_index('ix_mcp_scope_period', 'metric_channel_period', ['scope_type', 'period_start', 'period_end'])
    op.create_index('ix_mcp_country_domain', 'metric_channel_period', ['country_id', 'domain_id'])
    op.create_index('ix_mjsp_scope_period', 'metric_journey_source_period', ['scope_type', 'period_start', 'period_end'])
    op.create_index('ix_mjsp_country_domain', 'metric_journey_source_period', ['country_id', 'domain_id'])


def downgrade() -> None:
    """Rollback migration.
    Args:
        None (None): No arguments are required."""
    op.drop_index('ix_mjsp_country_domain', table_name='metric_journey_source_period')
    op.drop_index('ix_mjsp_scope_period', table_name='metric_journey_source_period')
    op.drop_index('ix_mcp_country_domain', table_name='metric_channel_period')
    op.drop_index('ix_mcp_scope_period', table_name='metric_channel_period')
    op.drop_table('metric_journey_source_period')
    op.drop_table('metric_channel_period')
