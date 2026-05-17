"""add_history_idempotency

Revision ID: 20260511_0011
Revises: 20260509_0010
Create Date: 2026-05-11 00:00:00
"""
from alembic import op


revision = '20260511_0011'
down_revision = '20260509_0010'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migration.
    Args:
        None (None): No arguments are required."""
    op.execute(
        """
        DELETE FROM saved_summaries AS older
        USING saved_summaries AS newer
        WHERE older.source_type = newer.source_type
          AND older.source_id = newer.source_id
          AND older.summary_type = newer.summary_type
          AND older.summary_id < newer.summary_id
        """,
    )
    op.execute(
        """
        DELETE FROM report_snapshots AS older
        USING report_snapshots AS newer
        WHERE older.country_id = newer.country_id
          AND older.period_start = newer.period_start
          AND older.period_end = newer.period_end
          AND older.report_type = newer.report_type
          AND older.calculation_version = newer.calculation_version
          AND older.report_id < newer.report_id
        """,
    )
    op.create_unique_constraint(
        'uq_saved_summaries_source',
        'saved_summaries',
        ['source_type', 'source_id', 'summary_type'],
    )
    op.create_unique_constraint(
        'uq_report_snapshot_context',
        'report_snapshots',
        ['country_id', 'period_start', 'period_end', 'report_type', 'calculation_version'],
    )


def downgrade() -> None:
    """Rollback migration.
    Args:
        None (None): No arguments are required."""
    op.drop_constraint('uq_report_snapshot_context', 'report_snapshots', type_='unique')
    op.drop_constraint('uq_saved_summaries_source', 'saved_summaries', type_='unique')
