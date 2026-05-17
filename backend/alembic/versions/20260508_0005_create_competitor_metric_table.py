"""create_competitor_metric_table

Revision ID: 20260508_0005
Revises: 20260508_0004
Create Date: 2026-05-08 00:00:00
"""
from alembic import op
import sqlalchemy as sa


revision = '20260508_0005'
down_revision = '20260508_0004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migration.
    Args:
        None (None): No arguments are required."""
    op.create_table(
        'metric_competitor_country_period',
        sa.Column('competitor_country_period_metric_id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('domain_id', sa.BigInteger(), sa.ForeignKey('dim_domain.domain_id'), nullable=False),
        sa.Column('company_id', sa.BigInteger(), sa.ForeignKey('dim_company.company_id'), nullable=True),
        sa.Column('country_id', sa.BigInteger(), sa.ForeignKey('dim_country.country_id'), nullable=False),
        sa.Column('region_id', sa.BigInteger(), sa.ForeignKey('dim_region.region_id'), nullable=True),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('total_traffic', sa.Numeric(20, 4), nullable=True),
        sa.Column('traffic_share_in_domain', sa.Numeric(10, 6), nullable=True),
        sa.Column('growth_rate', sa.Numeric(10, 6), nullable=True),
        sa.Column('presence_stability_score', sa.Numeric(10, 6), nullable=True),
        sa.Column('desktop_share', sa.Numeric(10, 6), nullable=True),
        sa.Column('mobile_share', sa.Numeric(10, 6), nullable=True),
        sa.Column('bounce_rate', sa.Numeric(10, 6), nullable=True),
        sa.Column('no_bounce_share', sa.Numeric(10, 6), nullable=True),
        sa.Column('quality_label', sa.String(30), nullable=True),
        sa.Column('country_role', sa.String(30), nullable=True),
        sa.Column('is_new_market_signal', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('is_abandoned_market_signal', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('calculation_version', sa.String(50), nullable=False),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint(
            'domain_id',
            'country_id',
            'period_start',
            'period_end',
            'calculation_version',
            name='uq_metric_competitor_country_period',
        ),
    )
    op.create_index('ix_mccp_domain_period', 'metric_competitor_country_period', ['domain_id', 'period_start', 'period_end'])
    op.create_index('ix_mccp_country', 'metric_competitor_country_period', ['country_id'])


def downgrade() -> None:
    """Rollback migration.
    Args:
        None (None): No arguments are required."""
    op.drop_index('ix_mccp_country', table_name='metric_competitor_country_period')
    op.drop_index('ix_mccp_domain_period', table_name='metric_competitor_country_period')
    op.drop_table('metric_competitor_country_period')
