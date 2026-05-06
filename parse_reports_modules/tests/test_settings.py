import argparse
import unittest
from pathlib import Path

from app.config.settings import AppSettings
from app.pipeline_runner import update_settings


class SettingsTest(unittest.TestCase):
    def test_amount_range(self) -> None:
        """Test amount updates range.
        Args:
            self (SettingsTest): Test case instance."""
        settings = AppSettings(
            semrush_url='',
            semrush_email='',
            semrush_password='',
            chromedriver_path=Path('chromedriver.exe'),
            downloads_path=Path('downloads'),
            domains_path=Path('domains.csv'),
            countries_path=Path('countries.csv'),
            output_path=Path('output'),
            first_domain='example.com',
            domain_amount=5,
            start_index=0,
            end_index=5,
            report_months=8,
            month_year=2022,
            retry_attempts=3,
            retry_pause=2.0,
        )
        args = argparse.Namespace(start=10, end=None, amount=5, months=None)
        updated_settings = update_settings(settings, args)
        self.assertEqual(updated_settings.start_index, 10)
        self.assertEqual(updated_settings.end_index, 15)

    def test_end_priority(self) -> None:
        """Test explicit end priority.
        Args:
            self (SettingsTest): Test case instance."""
        settings = AppSettings(
            semrush_url='',
            semrush_email='',
            semrush_password='',
            chromedriver_path=Path('chromedriver.exe'),
            downloads_path=Path('downloads'),
            domains_path=Path('domains.csv'),
            countries_path=Path('countries.csv'),
            output_path=Path('output'),
            first_domain='example.com',
            domain_amount=5,
            start_index=0,
            end_index=5,
            report_months=8,
            month_year=2022,
            retry_attempts=3,
            retry_pause=2.0,
        )
        args = argparse.Namespace(start=10, end=12, amount=5, months=None)
        updated_settings = update_settings(settings, args)
        self.assertEqual(updated_settings.end_index, 12)
