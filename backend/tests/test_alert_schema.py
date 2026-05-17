import unittest


class AlertSchemaTest(unittest.TestCase):
    def test_alert_migration(self) -> None:
        """Check alert migration.
        Args:
            self (AlertSchemaTest): Test case instance."""
        with open('alembic/versions/20260516_0012_create_anomaly_events.py', encoding='utf-8') as migration_file:
            migration_text = migration_file.read()
        self.assertIn('anomaly_events', migration_text)
        self.assertIn('dedup_key', migration_text)
        self.assertIn('idx_anomaly_events_status', migration_text)

    def test_alert_routes(self) -> None:
        """Check alert routes.
        Args:
            self (AlertSchemaTest): Test case instance."""
        with open('app/api/routes/alerts.py', encoding='utf-8') as route_file:
            route_text = route_file.read()
        self.assertIn("@router.get('/summary'", route_text)
        self.assertIn("@router.post('/detect'", route_text)
        self.assertIn("@router.patch('/{anomaly_id}/status'", route_text)


if __name__ == '__main__':
    unittest.main()
