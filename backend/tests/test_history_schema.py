import unittest
from pathlib import Path

from app.schemas.history import SavedSummaryCreate
from app.services.summary_storage_service import rag_allowed


class HistorySchemaTest(unittest.TestCase):
    def test_summary_migration(self) -> None:
        """Validate summary migration.
        Args:
            self (HistorySchemaTest): Test case instance."""
        migration_path = Path('alembic/versions/20260509_0010_create_saved_summaries.py')
        migration_text = migration_path.read_text(encoding='utf-8')
        self.assertIn('saved_summaries', migration_text)
        self.assertIn('rag_ready', migration_text)
        self.assertIn('embedding_status', migration_text)

    def test_idempotency_migration(self) -> None:
        """Validate idempotency migration.
        Args:
            self (HistorySchemaTest): Test case instance."""
        migration_path = Path('alembic/versions/20260511_0011_add_history_idempotency.py')
        migration_text = migration_path.read_text(encoding='utf-8')
        self.assertIn('uq_saved_summaries_source', migration_text)
        self.assertIn('uq_report_snapshot_context', migration_text)

    def test_failed_quality(self) -> None:
        """Validate failed quality rule.
        Args:
            self (HistorySchemaTest): Test case instance."""
        summary = SavedSummaryCreate(
            summary_type='mas_final_summary',
            title='MAS summary',
            summary_text='This summary has enough context and evidence for storage validation.',
            source_type='agent_run',
            source_id=1,
            data_quality_status='failed',
            rag_ready=True,
            confidence_score=0.9,
        )
        self.assertFalse(rag_allowed(summary))

    def test_ready_summary(self) -> None:
        """Validate ready summary rule.
        Args:
            self (HistorySchemaTest): Test case instance."""
        summary = SavedSummaryCreate(
            summary_type='manual',
            title='Manual summary',
            summary_text='This summary has enough context and evidence for storage validation.',
            source_type='manual',
            source_id=1,
            data_quality_status='passed',
            rag_ready=True,
            confidence_score=0.9,
        )
        self.assertTrue(rag_allowed(summary))


if __name__ == '__main__':
    unittest.main()
