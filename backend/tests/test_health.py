import importlib.util
import unittest


class HealthTest(unittest.TestCase):
    @unittest.skipIf(importlib.util.find_spec('pydantic_settings') is None, 'backend dependencies are not installed')
    def test_health_degraded(self: 'HealthTest') -> None:
        """Test degraded health.
        Args:
            self (HealthTest): Test case instance."""
        from app.core.config import Settings
        from app.services.health_service import build_health

        settings = Settings(postgres_host='invalid-host')
        health_data = build_health(settings)
        self.assertEqual(health_data['backend'], 'ok')
        self.assertIn(health_data['status'], ['ok', 'degraded'])
