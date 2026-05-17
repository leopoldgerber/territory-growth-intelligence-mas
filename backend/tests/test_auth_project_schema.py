from pathlib import Path
import unittest


ROOT_DIR = Path(__file__).resolve().parents[1]


class AuthProjectSchemaTest(unittest.TestCase):
    def test_auth_migration(self) -> None:
        """Check auth project migration.
        Args:
            None (None): No arguments are required."""
        migration = ROOT_DIR / 'alembic' / 'versions' / '20260516_0014_create_auth_project_tables.py'
        content = migration.read_text(encoding='utf-8')
        for table_name in [
            'users',
            'projects',
            'project_members',
            'project_competitors',
            'project_target_countries',
            'refresh_tokens',
        ]:
            self.assertIn(table_name, content)
        self.assertIn("op.add_column('workflow_runs'", content)
        self.assertIn("op.add_column('agent_runs'", content)

    def test_auth_routes(self) -> None:
        """Check auth routes.
        Args:
            None (None): No arguments are required."""
        auth_routes = (ROOT_DIR / 'app' / 'api' / 'routes' / 'auth.py').read_text(encoding='utf-8')
        project_routes = (ROOT_DIR / 'app' / 'api' / 'routes' / 'projects.py').read_text(encoding='utf-8')
        for route_text in ['/register', '/login', '/refresh', '/logout', '/me']:
            self.assertIn(route_text, auth_routes)
        for route_text in ['/{project_id}/members', '/{project_id}/competitors', '/{project_id}/target-countries']:
            self.assertIn(route_text, project_routes)


if __name__ == '__main__':
    unittest.main()
