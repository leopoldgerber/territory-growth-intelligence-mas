from pathlib import Path
from unittest import TestCase


class ChannelSchemaTest(TestCase):
    def test_channel_migration(self) -> None:
        """Check channel migration.
        Args:
            None (None): No arguments."""
        root_path = Path(__file__).resolve().parents[1]
        migration_path = root_path / 'alembic' / 'versions' / '20260508_0006_create_channel_metric_tables.py'
        migration_text = migration_path.read_text(encoding='utf-8')
        required_tokens = [
            'metric_channel_period',
            'metric_journey_source_period',
            'dependency_score',
            'stability_score',
            'is_dominant_channel',
        ]

        missing_tokens = [token for token in required_tokens if token not in migration_text]

        if missing_tokens:
            raise AssertionError(f'Missing channel migration tokens: {missing_tokens}')
