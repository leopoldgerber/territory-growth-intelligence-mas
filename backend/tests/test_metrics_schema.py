import unittest
from pathlib import Path


class MetricsSchemaTest(unittest.TestCase):
    def test_metric_tables(self) -> None:
        """Test metric migration.
        Args:
            None (None): No arguments are required."""
        migration_path = Path('alembic/versions/20260508_0003_create_country_metric_tables.py')
        migration_text = migration_path.read_text(encoding='utf-8')
        expected_tokens = [
            'metric_country_daily',
            'metric_country_period',
            'market_concentration_hhi',
            'engagement_score',
            'market_volatility_score',
            'calculation_version',
        ]
        missing_tokens = [token for token in expected_tokens if token not in migration_text]
        if missing_tokens:
            self.fail(f'Missing metric schema tokens: {missing_tokens}')


if __name__ == '__main__':
    unittest.main()
