"""create_country_metric_tables

Revision ID: 20260508_0003
Revises: 20260507_0002
Create Date: 2026-05-08 00:00:00
"""
from alembic import op
import sqlalchemy as sa


revision = '20260508_0003'
down_revision = '20260507_0002'
branch_labels = None
depends_on = None


def metric_columns() -> list[sa.Column]:
    """Build metric columns.
    Args:
        None (None): No arguments are required."""
    columns = [
        sa.Column('total_competitor_traffic', sa.Numeric(20, 4), nullable=True),
        sa.Column('active_competitors_count', sa.Integer(), nullable=True),
        sa.Column('leader_domain_id', sa.BigInteger(), sa.ForeignKey('dim_domain.domain_id'), nullable=True),
        sa.Column('leader_company_id', sa.BigInteger(), sa.ForeignKey('dim_company.company_id'), nullable=True),
        sa.Column('leader_traffic', sa.Numeric(20, 4), nullable=True),
        sa.Column('leader_share', sa.Numeric(10, 6), nullable=True),
        sa.Column('top_3_share', sa.Numeric(10, 6), nullable=True),
        sa.Column('market_concentration_hhi', sa.Numeric(10, 6), nullable=True),
        sa.Column('desktop_traffic', sa.Numeric(20, 4), nullable=True),
        sa.Column('mobile_traffic', sa.Numeric(20, 4), nullable=True),
        sa.Column('desktop_share', sa.Numeric(10, 6), nullable=True),
        sa.Column('mobile_share', sa.Numeric(10, 6), nullable=True),
        sa.Column('traffic_no_bounce', sa.Numeric(20, 4), nullable=True),
        sa.Column('traffic_bounce', sa.Numeric(20, 4), nullable=True),
        sa.Column('no_bounce_share', sa.Numeric(10, 6), nullable=True),
        sa.Column('bounce_share', sa.Numeric(10, 6), nullable=True),
        sa.Column('avg_bounce_rate', sa.Numeric(10, 6), nullable=True),
        sa.Column('avg_pages_per_visit', sa.Numeric(12, 4), nullable=True),
        sa.Column('avg_visit_duration_seconds', sa.Numeric(20, 4), nullable=True),
        sa.Column('engagement_score', sa.Numeric(10, 6), nullable=True),
        sa.Column('market_volatility_score', sa.Numeric(10, 6), nullable=True),
    ]
    return columns


def upgrade() -> None:
    """Apply migration.
    Args:
        None (None): No arguments are required."""
    op.create_table(
        'metric_country_daily',
        sa.Column('country_daily_metric_id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('date_id', sa.Integer(), sa.ForeignKey('dim_date.date_id'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('country_id', sa.BigInteger(), sa.ForeignKey('dim_country.country_id'), nullable=False),
        sa.Column('region_id', sa.BigInteger(), sa.ForeignKey('dim_region.region_id'), nullable=True),
        *metric_columns(),
        sa.Column('quality_status', sa.String(30), nullable=True),
        sa.Column('calculation_version', sa.String(50), nullable=False),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('date_id', 'country_id', 'calculation_version', name='uq_metric_country_daily_version'),
    )
    op.create_table(
        'metric_country_period',
        sa.Column('country_period_metric_id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('country_id', sa.BigInteger(), sa.ForeignKey('dim_country.country_id'), nullable=False),
        sa.Column('region_id', sa.BigInteger(), sa.ForeignKey('dim_region.region_id'), nullable=True),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('days_count', sa.Integer(), nullable=True),
        *metric_columns(),
        sa.Column('data_quality_status', sa.String(30), nullable=True),
        sa.Column('calculation_version', sa.String(50), nullable=False),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint(
            'country_id',
            'period_start',
            'period_end',
            'calculation_version',
            name='uq_metric_country_period_version',
        ),
    )
    op.create_index('ix_mcd_country_date', 'metric_country_daily', ['country_id', 'date'])
    op.create_index('ix_mcp_country_period', 'metric_country_period', ['country_id', 'period_start', 'period_end'])


def downgrade() -> None:
    """Rollback migration.
    Args:
        None (None): No arguments are required."""
    op.drop_index('ix_mcp_country_period', table_name='metric_country_period')
    op.drop_index('ix_mcd_country_date', table_name='metric_country_daily')
    op.drop_table('metric_country_period')
    op.drop_table('metric_country_daily')
