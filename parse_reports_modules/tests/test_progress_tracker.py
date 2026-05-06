import unittest

from app.utils.progress_tracker import add_export, add_month_export, add_processed, create_progress


class ProgressTrackerTest(unittest.TestCase):
    def test_create_progress(self) -> None:
        """Test progress creation.
        Args:
            self (ProgressTrackerTest): Test case instance."""
        progress = create_progress(['visits'], ['Apr'])
        self.assertEqual(progress.report_exports, {'visits': []})
        self.assertEqual(progress.monthly_exports['journey_sources']['Apr'], [])

    def test_add_progress(self) -> None:
        """Test progress updates.
        Args:
            self (ProgressTrackerTest): Test case instance."""
        progress = create_progress(['visits'], ['Apr'])
        progress = add_processed(progress, 'example.com')
        progress = add_export(progress, 'visits', 'example.com')
        progress = add_month_export(progress, 'journey_sources', 'Apr', 'example.com')
        self.assertEqual(progress.processed_domains, ['example.com'])
        self.assertEqual(progress.report_exports['visits'], ['example.com'])
        self.assertEqual(progress.monthly_exports['journey_sources']['Apr'], ['example.com'])
