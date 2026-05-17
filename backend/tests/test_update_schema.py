from pathlib import Path
import unittest


ROOT_DIR = Path(__file__).resolve().parents[1]


class UpdateSchemaTest(unittest.TestCase):
    def test_update_migration(self) -> None:
        """Check update migration.
        Args:
            None (None): No arguments are required."""
        migration = ROOT_DIR / 'alembic' / 'versions' / '20260516_0016_create_update_schedules.py'
        content = migration.read_text(encoding='utf-8')
        for table_name in ['update_schedules', 'update_runs', 'update_run_steps']:
            self.assertIn(table_name, content)
        self.assertIn('idx_update_schedules_next_run', content)
        self.assertIn('idx_update_runs_project_created', content)

    def test_update_routes(self) -> None:
        """Check update routes.
        Args:
            None (None): No arguments are required."""
        routes = (ROOT_DIR / 'app' / 'api' / 'routes' / 'updates.py').read_text(encoding='utf-8')
        for route_text in [
            '/update-schedules',
            '/update-schedules/{schedule_id}/run-now',
            '/update-runs',
            '/update-runs/{update_run_id}/steps',
            '/update-status/latest',
        ]:
            self.assertIn(route_text, routes)

    def test_scheduler_task(self) -> None:
        """Check scheduler task.
        Args:
            None (None): No arguments are required."""
        tasks = (ROOT_DIR / 'app' / 'worker' / 'tasks.py').read_text(encoding='utf-8')
        celery = (ROOT_DIR / 'app' / 'worker' / 'celery_app.py').read_text(encoding='utf-8')
        compose = (ROOT_DIR.parent / 'docker-compose.yml').read_text(encoding='utf-8')
        self.assertIn('scheduled_update_task', tasks)
        self.assertIn('scan_update_schedules_task', tasks)
        self.assertIn('beat_schedule', celery)
        self.assertIn('beat:', compose)


if __name__ == '__main__':
    unittest.main()
