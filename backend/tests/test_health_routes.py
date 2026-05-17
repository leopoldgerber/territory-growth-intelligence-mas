from pathlib import Path
import unittest


ROOT_DIR = Path(__file__).resolve().parents[1]


class HealthRoutesTest(unittest.TestCase):
    def test_health_routes_exist(self) -> None:
        """Check health routes.
        Args:
            None (None): No arguments are required."""
        routes = (ROOT_DIR / 'app' / 'api' / 'routes' / 'health.py').read_text(encoding='utf-8')
        for route_text in ['/health', '/live', '/ready', '/metrics']:
            self.assertIn(route_text, routes)

    def test_observability_files_exist(self) -> None:
        """Check observability files.
        Args:
            None (None): No arguments are required."""
        observability = ROOT_DIR / 'app' / 'core' / 'observability.py'
        logging_path = ROOT_DIR / 'app' / 'core' / 'logging.py'
        self.assertTrue(observability.exists())
        self.assertTrue(logging_path.exists())


if __name__ == '__main__':
    unittest.main()
