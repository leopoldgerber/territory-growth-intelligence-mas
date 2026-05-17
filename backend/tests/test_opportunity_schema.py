from pathlib import Path
from unittest import TestCase


class OpportunitySchemaTest(TestCase):
    def test_opportunity_migration(self) -> None:
        """Check opportunity migration.
        Args:
            None (None): No arguments."""
        root_path = Path(__file__).resolve().parents[1]
        migration_path = root_path / 'alembic' / 'versions' / '20260508_0007_create_opportunity_scores.py'
        migration_text = migration_path.read_text(encoding='utf-8')
        required_tokens = [
            'country_opportunity_scores',
            'opportunity_score',
            'traffic_score',
            'competition_score',
            'entry_difficulty_score',
        ]

        missing_tokens = [token for token in required_tokens if token not in migration_text]

        if missing_tokens:
            raise AssertionError(f'Missing opportunity migration tokens: {missing_tokens}')
