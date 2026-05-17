import unittest
from pathlib import Path

from app.services.report_detector import detect_type, validate_columns


class ReportDetectorTest(unittest.TestCase):
    def test_known_report(self) -> None:
        """Test known report.
        Args:
            None (None): No arguments are required."""
        report_type = detect_type(Path('traffic_sources_daily.xlsx'))
        if report_type != 'domain_channel_daily':
            self.fail('Report type detection failed.')

    def test_prefixed_report(self) -> None:
        """Test prefixed report.
        Args:
            None (None): No arguments are required."""
        report_type = detect_type(Path('b0785a1492034d1abf889d751162905e_journey_sources_daily.xlsx'))
        if report_type != 'domain_journey_source_daily':
            self.fail('Prefixed report type detection failed.')

    def test_missing_columns(self) -> None:
        """Test missing columns.
        Args:
            None (None): No arguments are required."""
        missing_columns = validate_columns('domain_channel_daily', ['date', 'domain', 'company'])
        expected_columns = ['direct', 'referral', 'paid', 'social', 'search']
        if missing_columns != expected_columns:
            self.fail('Required column validation failed.')


if __name__ == '__main__':
    unittest.main()
