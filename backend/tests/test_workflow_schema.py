import unittest


class WorkflowSchemaTest(unittest.TestCase):
    def test_workflow_migration(self) -> None:
        """Check workflow migration.
        Args:
            self (WorkflowSchemaTest): Test case instance."""
        with open('alembic/versions/20260516_0013_create_workflow_runs.py', encoding='utf-8') as migration_file:
            migration_text = migration_file.read()
        self.assertIn('workflow_runs', migration_text)
        self.assertIn('agent_run_id', migration_text)
        self.assertIn('strategy_id', migration_text)

    def test_workflow_routes(self) -> None:
        """Check workflow routes.
        Args:
            self (WorkflowSchemaTest): Test case instance."""
        with open('app/api/routes/workflow.py', encoding='utf-8') as route_file:
            route_text = route_file.read()
        self.assertIn("@router.get('/options'", route_text)
        self.assertIn("@router.post('/strategy-analysis'", route_text)
        self.assertIn("@router.get('/recent'", route_text)
        self.assertIn("@router.get('/runs/{workflow_run_id}'", route_text)


if __name__ == '__main__':
    unittest.main()
