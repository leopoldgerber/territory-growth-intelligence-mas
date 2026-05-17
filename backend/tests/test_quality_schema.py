import unittest
from pathlib import Path


class QualitySchemaTest(unittest.TestCase):
    def test_quality_columns(self) -> None:
        """Test quality migration.
        Args:
            None (None): No arguments are required."""
        migration_path = Path('alembic/versions/20260507_0002_add_data_quality_columns.py')
        migration_text = migration_path.read_text(encoding='utf-8')
        expected_tokens = [
            'quality_status',
            'severity',
            'message',
            'affected_rows_count',
            'sample_rows',
            'quality_dimension',
        ]
        missing_tokens = [token for token in expected_tokens if token not in migration_text]
        if missing_tokens:
            self.fail(f'Missing quality columns: {missing_tokens}')


if __name__ == '__main__':
    unittest.main()
