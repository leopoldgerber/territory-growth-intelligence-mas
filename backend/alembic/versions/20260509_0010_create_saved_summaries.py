"""create_saved_summaries

Revision ID: 20260509_0010
Revises: 20260509_0009
Create Date: 2026-05-09 00:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '20260509_0010'
down_revision = '20260509_0009'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migration.
    Args:
        None (None): No arguments are required."""
    op.create_table(
        'saved_summaries',
        sa.Column('summary_id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('summary_type', sa.String(100), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('summary_text', sa.Text(), nullable=False),
        sa.Column('summary_json', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('country_id', sa.BigInteger(), sa.ForeignKey('dim_country.country_id'), nullable=True),
        sa.Column('domain_id', sa.BigInteger(), sa.ForeignKey('dim_domain.domain_id'), nullable=True),
        sa.Column('channel_id', sa.BigInteger(), sa.ForeignKey('dim_channel.channel_id'), nullable=True),
        sa.Column('period_start', sa.Date(), nullable=True),
        sa.Column('period_end', sa.Date(), nullable=True),
        sa.Column('source_type', sa.String(100), nullable=False),
        sa.Column('source_id', sa.BigInteger(), nullable=False),
        sa.Column('tags', postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column('importance_score', sa.Numeric(10, 6), nullable=True),
        sa.Column('confidence_score', sa.Numeric(10, 6), nullable=True),
        sa.Column('data_quality_status', sa.String(30), nullable=True),
        sa.Column('rag_ready', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('embedding_status', sa.String(30), server_default='not_started', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_index(
        'ix_saved_summaries_country_period',
        'saved_summaries',
        ['country_id', 'period_start', 'period_end'],
    )
    op.create_index(
        'ix_saved_summaries_type_created',
        'saved_summaries',
        ['summary_type', 'created_at'],
    )
    op.create_index(
        'ix_saved_summaries_tags',
        'saved_summaries',
        ['tags'],
        postgresql_using='gin',
    )
    op.create_index(
        'ix_saved_summaries_rag_ready',
        'saved_summaries',
        ['rag_ready', 'embedding_status'],
    )


def downgrade() -> None:
    """Rollback migration.
    Args:
        None (None): No arguments are required."""
    op.drop_index('ix_saved_summaries_rag_ready', table_name='saved_summaries')
    op.drop_index('ix_saved_summaries_tags', table_name='saved_summaries')
    op.drop_index('ix_saved_summaries_type_created', table_name='saved_summaries')
    op.drop_index('ix_saved_summaries_country_period', table_name='saved_summaries')
    op.drop_table('saved_summaries')
