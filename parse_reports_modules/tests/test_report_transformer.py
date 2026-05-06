import datetime
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from app.processing import file_parser
from app.processing.month_utils import metric_period
from app.processing.report_transformer import parse_metrics


class ReportTransformerTest(unittest.TestCase):
    def test_metric_year(self) -> None:
        """Test metric period year.
        Args:
            self (ReportTransformerTest): Test case instance."""
        period = metric_period(3, datetime.date(2026, 5, 6), 2022)
        self.assertEqual(period, ('Feb', 'May', '2022'))

    def test_metrics_wide(self) -> None:
        """Test wide metrics output.
        Args:
            self (ReportTransformerTest): Test case instance."""
        with tempfile.TemporaryDirectory() as temp_name:
            downloads_path = Path(temp_name)
            domain = 'example.com'
            first_month, last_month, year = metric_period(1, report_year=2022)
            metric_values = {
                'visits': [100, 40, 60],
                'users': [80, 30, 50],
                'time_on_site': [120, 100, 130],
                'bounce_rate': [10, 25, 50],
            }
            for metric_name, values in metric_values.items():
                file_path = file_parser.metric_file(downloads_path, domain, metric_name, first_month, last_month, year)
                metric_data = pd.DataFrame(
                    {
                        'Unnamed: 0': ['2022-04-01'],
                        'All devices': [values[0]],
                        'Desktop': [values[1]],
                        'Mobile': [values[2]],
                    },
                )
                metric_data.to_csv(file_path, index=False)
            domains = pd.DataFrame({'domain': [domain], 'company': ['Example']})
            metrics = parse_metrics(downloads_path, [domain], domains, 1, 2022)
            self.assertNotIn('metric', metrics.columns)
            self.assertEqual(metrics.loc[0, 'visits'], 100)
            self.assertEqual(metrics.loc[0, 'unique'], 80)
            self.assertEqual(metrics.loc[0, 'all_bounce'], 10)
            self.assertEqual(metrics.loc[0, 'all_no_bounce'], 90)
            self.assertEqual(metrics.loc[0, 'desktop_bounce'], 10)
            self.assertEqual(metrics.loc[0, 'mobile_bounce'], 30)
            self.assertEqual(metrics.loc[0, 'year'], '2022')
