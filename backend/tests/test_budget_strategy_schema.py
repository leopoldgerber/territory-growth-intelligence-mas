from pathlib import Path
from unittest import TestCase


class BudgetStrategySchemaTest(TestCase):
    def test_strategy_migration(self) -> None:
        """Check strategy migration.
        Args:
            None (None): No arguments."""
        root_path = Path(__file__).resolve().parents[1]
        migration_path = root_path / 'alembic' / 'versions' / '20260508_0008_create_budget_strategy_tables.py'
        migration_text = migration_path.read_text(encoding='utf-8')
        required_tokens = [
            'budget_strategy_runs',
            'budget_strategy_allocations',
            'budget_amount',
            'confidence_score',
            'expected_clients',
        ]

        missing_tokens = [token for token in required_tokens if token not in migration_text]

        if missing_tokens:
            raise AssertionError(f'Missing budget strategy migration tokens: {missing_tokens}')
