from pathlib import Path
import unittest


ROOT_DIR = Path(__file__).resolve().parents[1]


class FeedbackLoopSchemaTest(unittest.TestCase):
    def test_feedback_migration(self) -> None:
        """Check feedback migration.
        Args:
            None (None): No arguments are required."""
        migration = ROOT_DIR / 'alembic' / 'versions' / '20260516_0019_create_feedback_loop_tables.py'
        content = migration.read_text(encoding='utf-8')
        for table_name in [
            'recommendation_feedback',
            'campaign_result_snapshots',
            'forecast_actual_comparisons',
            'scoring_weight_versions',
            'scoring_weight_adjustments',
            'agent_feedback_events',
        ]:
            self.assertIn(table_name, content)
        for column_name in ['accuracy_score', 'bias_direction', 'proposed_weights', 'decision_tags']:
            self.assertIn(column_name, content)

    def test_feedback_routes(self) -> None:
        """Check feedback routes.
        Args:
            None (None): No arguments are required."""
        routes = (ROOT_DIR / 'app' / 'api' / 'routes' / 'feedback.py').read_text(encoding='utf-8')
        for route_text in [
            '/recommendations',
            '/campaign-snapshots',
            '/forecast-comparisons',
            '/learning-summary',
            '/scoring-weights',
            '/scoring-adjustments',
            '/agent-events',
        ]:
            self.assertIn(route_text, routes)

    def test_feedback_services(self) -> None:
        """Check feedback services.
        Args:
            None (None): No arguments are required."""
        service = ROOT_DIR / 'app' / 'services' / 'feedback_loop_service.py'
        content = service.read_text(encoding='utf-8')
        for function_name in [
            'create_feedback',
            'create_snapshot',
            'compare_forecast',
            'learning_summary',
            'calibrated_confidence',
            'update_adjustment',
        ]:
            self.assertIn(function_name, content)

    def test_mas_tools(self) -> None:
        """Check MAS tools.
        Args:
            None (None): No arguments are required."""
        registry = (ROOT_DIR / 'app' / 'services' / 'mas_tool_registry_service.py').read_text(encoding='utf-8')
        for tool_name in [
            'get_recommendation_feedback',
            'get_forecast_accuracy',
            'get_campaign_results',
            'get_learning_summary',
            'get_active_scoring_weights',
            'get_similar_past_campaigns',
        ]:
            self.assertIn(tool_name, registry)


if __name__ == '__main__':
    unittest.main()
