from pathlib import Path
from unittest import TestCase



class CompetitorSchemaTest(TestCase):
    def test_competitor_migration(self) -> None:
        """Check competitor migration.
        Args:
            None (None): No arguments."""
        root_path = Path(__file__).resolve().parents[1]
        migration_path = root_path / 'alembic' / 'versions' / '20260508_0005_create_competitor_metric_table.py'
        migration_text = migration_path.read_text(encoding='utf-8')
        required_tokens = [
            'metric_competitor_country_period',
            'traffic_share_in_domain',
            'presence_stability_score',
            'is_new_market_signal',
            'is_abandoned_market_signal',
        ]

        missing_tokens = [token for token in required_tokens if token not in migration_text]

        if missing_tokens:
            raise AssertionError(f'Missing competitor migration tokens: {missing_tokens}')
