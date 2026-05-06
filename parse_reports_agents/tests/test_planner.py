import unittest

from agent_app.agent.planner import build_plan


class PlannerTest(unittest.TestCase):
    def test_dry_plan(self) -> None:
        """Test task plan.
        Args:
            self (PlannerTest): Test case instance."""
        tasks = build_plan('full', ['example.com'], ['Apr'], 2022, 'google.com', False)
        task_names = [task.name for task in tasks]
        self.assertEqual(task_names[0], 'LoginTask')
        self.assertEqual(task_names[-1], 'ProcessDownloadedReportsTask')
        self.assertIn('ExportJourneyTask:example.com', task_names)

    def test_first_limit(self) -> None:
        """Test first domain limit.
        Args:
            self (PlannerTest): Test case instance."""
        tasks = build_plan('download', ['a.com', 'b.com'], ['Apr'], 2022, 'google.com', True)
        task_names = [task.name for task in tasks]
        self.assertIn('ExportTrafficAnalyticsTask:a.com', task_names)
        self.assertNotIn('ExportTrafficAnalyticsTask:b.com', task_names)
