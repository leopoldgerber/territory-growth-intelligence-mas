"""create_opportunity_scores

Revision ID: 20260508_0007
Revises: 20260508_0006
Create Date: 2026-05-08 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '20260508_0007'
down_revision = '20260508_0006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migration.
    Args:
        None (None): No arguments are required."""
    op.create_table(
        'country_opportunity_scores',
        sa.Column('opportunity_score_id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('country_id', sa.BigInteger(), sa.ForeignKey('dim_country.country_id'), nullable=False),
        sa.Column('region_id', sa.BigInteger(), sa.ForeignKey('dim_region.region_id'), nullable=True),
        sa.Column('period_start', sa.Date(), nullable=False),
        sa.Column('period_end', sa.Date(), nullable=False),
        sa.Column('opportunity_score', sa.Numeric(10, 6), nullable=True),
        sa.Column('traffic_score', sa.Numeric(10, 6), nullable=True),
        sa.Column('competition_score', sa.Numeric(10, 6), nullable=True),
        sa.Column('quality_score', sa.Numeric(10, 6), nullable=True),
        sa.Column('channel_gap_score', sa.Numeric(10, 6), nullable=True),
        sa.Column('volatility_score', sa.Numeric(10, 6), nullable=True),
        sa.Column('localization_potential_score', sa.Numeric(10, 6), nullable=True),
        sa.Column('entry_difficulty_score', sa.Numeric(10, 6), nullable=True),
        sa.Column('recommended_priority', sa.String(50), nullable=True),
        sa.Column('market_type', sa.String(100), nullable=True),
        sa.Column('strengths', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('risks', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('score_breakdown', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('data_quality_status', sa.String(30), nullable=True),
        sa.Column('calculation_version', sa.String(50), nullable=False),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.UniqueConstraint('country_id', 'period_start', 'period_end', 'calculation_version', name='uq_country_opportunity_score'),
    )
    op.create_index('ix_cos_period', 'country_opportunity_scores', ['period_start', 'period_end'])
    op.create_index('ix_cos_priority', 'country_opportunity_scores', ['recommended_priority'])
    op.create_index('ix_cos_score', 'country_opportunity_scores', ['opportunity_score'])


def downgrade() -> None:
    """Rollback migration.
    Args:
        None (None): No arguments are required."""
    op.drop_index('ix_cos_score', table_name='country_opportunity_scores')
    op.drop_index('ix_cos_priority', table_name='country_opportunity_scores')
    op.drop_index('ix_cos_period', table_name='country_opportunity_scores')
    op.drop_table('country_opportunity_scores')
