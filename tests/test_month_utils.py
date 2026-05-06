import datetime
import unittest

from app.processing.month_utils import add_month_year, build_months, month_abbr, month_number


class MonthUtilsTest(unittest.TestCase):
    def test_build_months(self) -> None:
        """Test month list.
        Args:
            self (MonthUtilsTest): Test case instance."""
        month_list = build_months(3, datetime.date(2026, 5, 6))
        self.assertEqual(month_list, ['Apr', 'Mar', 'Feb'])

    def test_month_number(self) -> None:
        """Test month number.
        Args:
            self (MonthUtilsTest): Test case instance."""
        month_value = month_number('Apr')
        self.assertEqual(month_value, 4)

    def test_month_abbr(self) -> None:
        """Test month abbreviation.
        Args:
            self (MonthUtilsTest): Test case instance."""
        month_name = month_abbr('4')
        self.assertEqual(month_name, 'Apr')

    def test_add_month_year(self) -> None:
        """Test month year formatting.
        Args:
            self (MonthUtilsTest): Test case instance."""
        month_year = add_month_year('Apr', '2026')
        self.assertEqual(month_year, '01.04.2026')
