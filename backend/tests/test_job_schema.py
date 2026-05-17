from pathlib import Path
import unittest


ROOT_DIR = Path(__file__).resolve().parents[1]


class JobSchemaTest(unittest.TestCase):
    def test_job_migration(self) -> None:
        """Check job migration.
        Args:
            None (None): No arguments are required."""
        migration = ROOT_DIR / 'alembic' / 'versions' / '20260516_0015_create_background_jobs.py'
        content = migration.read_text(encoding='utf-8')
        self.assertIn('background_jobs', content)
        self.assertIn('background_job_events', content)
        self.assertIn('idx_background_jobs_project_created', content)
        self.assertIn('idx_background_job_events_job_created', content)

    def test_job_routes(self) -> None:
        """Check job routes.
        Args:
            None (None): No arguments are required."""
        routes = (ROOT_DIR / 'app' / 'api' / 'routes' / 'jobs.py').read_text(encoding='utf-8')
        for route_text in ["@router.get(''", "'/{job_id}'", "'/{job_id}/events'", "'/{job_id}/stream'", "'/{job_id}/cancel'"]:
            self.assertIn(route_text, routes)

    def test_worker_config(self) -> None:
        """Check worker config.
        Args:
            None (None): No arguments are required."""
        compose = (ROOT_DIR.parent / 'docker-compose.yml').read_text(encoding='utf-8')
        requirements = (ROOT_DIR / 'requirements.txt').read_text(encoding='utf-8')
        self.assertIn('redis:', compose)
        self.assertIn('worker:', compose)
        self.assertIn('celery[redis]', requirements)


if __name__ == '__main__':
    unittest.main()
