from pathlib import Path
import unittest


ROOT_DIR = Path(__file__).resolve().parents[1]
WORKSPACE_DIR = ROOT_DIR.parent


class ProductionReadinessTest(unittest.TestCase):
    def test_production_files_exist(self) -> None:
        """Check production files.
        Args:
            None (None): No arguments are required."""
        expected_paths = [
            WORKSPACE_DIR / 'docker-compose.prod.yml',
            ROOT_DIR / 'Dockerfile.prod',
            WORKSPACE_DIR / 'infra' / 'nginx' / 'default.conf',
            WORKSPACE_DIR / '.github' / 'workflows' / 'ci.yml',
            WORKSPACE_DIR / 'scripts' / 'backup_postgres.ps1',
        ]
        for path in expected_paths:
            self.assertTrue(path.exists(), str(path))

    def test_frontend_test_files_exist(self) -> None:
        """Check frontend test files.
        Args:
            None (None): No arguments are required."""
        expected_paths = [
            WORKSPACE_DIR / 'frontend' / 'playwright.config.ts',
            WORKSPACE_DIR / 'frontend' / 'vite.config.test.ts',
            WORKSPACE_DIR / 'frontend' / 'src' / 'components' / 'SystemStatusCard.test.tsx',
        ]
        for path in expected_paths:
            self.assertTrue(path.exists(), str(path))


if __name__ == '__main__':
    unittest.main()
