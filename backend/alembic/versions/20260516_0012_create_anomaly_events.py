"""create_anomaly_events

Revision ID: 20260516_0012
Revises: 20260511_0011
Create Date: 2026-05-16 00:00:00
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = '20260516_0012'
down_revision = '20260511_0011'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migration.
    Args:
        None (None): No arguments are required."""
    op.create_table(
        'anomaly_events',
        sa.Column('anomaly_id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('dedup_key', sa.Text(), nullable=False),
        sa.Column('event_type', sa.String(length=100), nullable=False),
        sa.Column('event_category', sa.String(length=50), nullable=True),
        sa.Column('event_date', sa.Date(), nullable=False),
        sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('country_id', sa.BigInteger(), sa.ForeignKey('dim_country.country_id'), nullable=True),
        sa.Column('region_id', sa.BigInteger(), sa.ForeignKey('dim_region.region_id'), nullable=True),
        sa.Column('domain_id', sa.BigInteger(), sa.ForeignKey('dim_domain.domain_id'), nullable=True),
        sa.Column('company_id', sa.BigInteger(), sa.ForeignKey('dim_company.company_id'), nullable=True),
        sa.Column('channel_id', sa.BigInteger(), sa.ForeignKey('dim_channel.channel_id'), nullable=True),
        sa.Column('metric_name', sa.Text(), nullable=True),
        sa.Column('previous_value', sa.Numeric(20, 6), nullable=True),
        sa.Column('current_value', sa.Numeric(20, 6), nullable=True),
        sa.Column('absolute_change', sa.Numeric(20, 6), nullable=True),
        sa.Column('relative_change', sa.Numeric(10, 6), nullable=True),
        sa.Column('baseline_value', sa.Numeric(20, 6), nullable=True),
        sa.Column('threshold_value', sa.Numeric(20, 6), nullable=True),
        sa.Column('severity', sa.String(length=30), nullable=True),
        sa.Column('status', sa.String(length=30), server_default='new', nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('evidence', postgresql.JSONB(), nullable=True),
        sa.Column('recommendation_hint', sa.Text(), nullable=True),
        sa.Column('calculation_version', sa.String(length=50), nullable=True),
        sa.Column('data_quality_status', sa.String(length=30), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_unique_constraint('uq_anomaly_events_dedup_key', 'anomaly_events', ['dedup_key'])
    op.create_index('idx_anomaly_events_date', 'anomaly_events', ['event_date'])
    op.create_index('idx_anomaly_events_country_date', 'anomaly_events', ['country_id', 'event_date'])
    op.create_index('idx_anomaly_events_domain_date', 'anomaly_events', ['domain_id', 'event_date'])
    op.create_index('idx_anomaly_events_channel_date', 'anomaly_events', ['channel_id', 'event_date'])
    op.create_index('idx_anomaly_events_type_severity', 'anomaly_events', ['event_type', 'severity'])
    op.create_index('idx_anomaly_events_status', 'anomaly_events', ['status'])


def downgrade() -> None:
    """Rollback migration.
    Args:
        None (None): No arguments are required."""
    op.drop_index('idx_anomaly_events_status', table_name='anomaly_events')
    op.drop_index('idx_anomaly_events_type_severity', table_name='anomaly_events')
    op.drop_index('idx_anomaly_events_channel_date', table_name='anomaly_events')
    op.drop_index('idx_anomaly_events_domain_date', table_name='anomaly_events')
    op.drop_index('idx_anomaly_events_country_date', table_name='anomaly_events')
    op.drop_index('idx_anomaly_events_date', table_name='anomaly_events')
    op.drop_constraint('uq_anomaly_events_dedup_key', 'anomaly_events', type_='unique')
    op.drop_table('anomaly_events')
