import unittest
from pathlib import Path


class ReportSchemaTest(unittest.TestCase):
    def test_report_table(self) -> None:
        """Test report migration.
        Args:
            None (None): No arguments are required."""
        migration_path = Path('alembic/versions/20260508_0004_create_report_snapshots.py')
        migration_text = migration_path.read_text(encoding='utf-8')
        expected_tokens = [
            'report_snapshots',
            'report_markdown',
            'report_json',
            'input_params',
            'data_quality_status',
            'generator_version',
        ]
        missing_tokens = [token for token in expected_tokens if token not in migration_text]
        if missing_tokens:
            self.fail(f'Missing report schema tokens: {missing_tokens}')


if __name__ == '__main__':
    unittest.main()
