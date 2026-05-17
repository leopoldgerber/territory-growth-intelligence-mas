import unittest
from pathlib import Path

from app.schemas.mas import MASAnalyzeRequest, MASRunResponse


class MASSchemaTest(unittest.TestCase):
    def test_mas_migration(self) -> None:
        """Validate MAS migration.
        Args:
            self (MASSchemaTest): Test case instance."""
        migration_path = Path('alembic/versions/20260509_0009_create_agent_tables.py')
        migration_text = migration_path.read_text(encoding='utf-8')
        self.assertIn('agent_runs', migration_text)
        self.assertIn('agent_steps', migration_text)
        self.assertIn('agent_evidence', migration_text)
        self.assertIn('agent_insights', migration_text)
        self.assertIn('agent_recommendations', migration_text)

    def test_request_defaults(self) -> None:
        """Validate request defaults.
        Args:
            self (MASSchemaTest): Test case instance."""
        request = MASAnalyzeRequest(user_query='Analyze Germany.')
        self.assertEqual(request.currency_code, 'EUR')
        self.assertEqual(request.campaign_goal, 'market_test')
        self.assertEqual(request.calculation_version, 'v1')

    def test_response_lists(self) -> None:
        """Validate response list defaults.
        Args:
            self (MASSchemaTest): Test case instance."""
        response = MASRunResponse(agent_run_id=1, user_query='Analyze Germany.')
        self.assertEqual(response.steps, [])
        self.assertEqual(response.evidence, [])
        self.assertEqual(response.insights, [])
        self.assertEqual(response.recommendations, [])


if __name__ == '__main__':
    unittest.main()
