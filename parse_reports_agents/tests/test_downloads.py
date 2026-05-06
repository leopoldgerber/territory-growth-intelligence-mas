import tempfile
import unittest
from pathlib import Path

from agent_app.playwright_runtime.downloads import DownloadRecord, add_download, read_manifest


class DownloadsTest(unittest.TestCase):
    def test_manifest_record(self) -> None:
        """Test download manifest.
        Args:
            self (DownloadsTest): Test case instance."""
        with tempfile.TemporaryDirectory() as temp_name:
            downloads_path = Path(temp_name)
            record = DownloadRecord(
                domain='example.com',
                report_name='visits',
                month_name='',
                file_path='example.csv',
            )
            add_download(downloads_path, record)
            records = read_manifest(downloads_path)
        self.assertEqual(records[0]['domain'], 'example.com')
        self.assertEqual(records[0]['report_name'], 'visits')
