from pathlib import Path
import unittest


ROOT_DIR = Path(__file__).resolve().parents[1]


class AdvancedStrategySchemaTest(unittest.TestCase):
    def test_strategy_migration(self) -> None:
        """Check advanced migration.
        Args:
            None (None): No arguments are required."""
        migration = ROOT_DIR / 'alembic' / 'versions' / '20260516_0018_create_advanced_strategy_tables.py'
        content = migration.read_text(encoding='utf-8')
        for table_name in ['growth_scenarios', 'advanced_country_scores', 'advanced_budget_allocations']:
            self.assertIn(table_name, content)
        for column_name in ['expected_traffic_capture', 'estimated_roi', 'competitor_threat_score']:
            self.assertIn(column_name, content)

    def test_strategy_routes(self) -> None:
        """Check advanced routes.
        Args:
            None (None): No arguments are required."""
        routes = (ROOT_DIR / 'app' / 'api' / 'routes' / 'marketing.py').read_text(encoding='utf-8')
        for route_text in [
            '/advanced-strategy',
            '/advanced-strategy/scenarios',
            '/advanced-strategy/scenarios/{growth_scenario_id}',
            '/countries/{country_id}/advanced-scores',
            '/countries/{country_id}/advanced-scores/recalculate',
        ]:
            self.assertIn(route_text, routes)

    def test_forecast_services(self) -> None:
        """Check forecast services.
        Args:
            None (None): No arguments are required."""
        service_names = [
            'advanced_strategy_service.py',
            'advanced_score_service.py',
            'traffic_capture_forecast_service.py',
            'lead_client_forecast_service.py',
            'roi_forecast_service.py',
            'advanced_budget_allocation_service.py',
        ]
        for service_name in service_names:
            self.assertTrue((ROOT_DIR / 'app' / 'services' / service_name).exists())

    def test_mas_tools(self) -> None:
        """Check MAS tools.
        Args:
            None (None): No arguments are required."""
        registry = (ROOT_DIR / 'app' / 'services' / 'mas_tool_registry_service.py').read_text(encoding='utf-8')
        for tool_name in [
            'calculate_growth_scenarios',
            'calculate_roi_forecast',
            'calculate_advanced_scores',
            'calculate_advanced_budget_allocation',
        ]:
            self.assertIn(tool_name, registry)


if __name__ == '__main__':
    unittest.main()
