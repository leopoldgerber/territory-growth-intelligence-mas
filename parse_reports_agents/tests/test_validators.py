import tempfile
import unittest
from pathlib import Path

from agent_app.agent.validators import validate_csv, validate_file


class ValidatorsTest(unittest.TestCase):
    def test_file_missing(self) -> None:
        """Test missing file.
        Args:
            self (ValidatorsTest): Test case instance."""
        result = validate_file(Path('missing.csv'))
        self.assertFalse(result.success)

    def test_csv_valid(self) -> None:
        """Test valid CSV.
        Args:
            self (ValidatorsTest): Test case instance."""
        with tempfile.TemporaryDirectory() as temp_name:
            file_path = Path(temp_name) / 'sample.csv'
            file_path.write_text('domain,value\nexample.com,1\n', encoding='utf-8')
            result = validate_csv(file_path, ['domain'])
        self.assertTrue(result.success)
