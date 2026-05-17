from datetime import date
import unittest

from app.services.alert_rule_service import dedup_key, relative_change, severity_value, split_window


class AlertRuleTest(unittest.TestCase):
    def test_split_window(self) -> None:
        """Validate detection windows.
        Args:
            self (AlertRuleTest): Test case instance."""
        windows = split_window(date(2026, 1, 1), date(2026, 1, 14))
        self.assertEqual(windows, (date(2026, 1, 1), date(2026, 1, 7), date(2026, 1, 8), date(2026, 1, 14)))

    def test_relative_change(self) -> None:
        """Validate relative change.
        Args:
            self (AlertRuleTest): Test case instance."""
        self.assertEqual(relative_change(100, 250), 1.5)
        self.assertIsNone(relative_change(0, 250))

    def test_dedup_key(self) -> None:
        """Validate dedup key.
        Args:
            self (AlertRuleTest): Test case instance."""
        key = dedup_key('traffic_spike', date(2026, 1, 14), 1, 2, None, 'v1')
        self.assertEqual(key, 'traffic_spike|2026-01-14|country=1|domain=2|channel=null|v1')

    def test_severity_value(self) -> None:
        """Validate severity value.
        Args:
            self (AlertRuleTest): Test case instance."""
        self.assertEqual(severity_value(2.0, 5000, 1000), 'critical')
        self.assertEqual(severity_value(0.2, 100, 1000), 'low')


if __name__ == '__main__':
    unittest.main()
