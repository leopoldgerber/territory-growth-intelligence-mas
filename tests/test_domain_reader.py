import unittest

import pandas as pd

from app.domains.domain_reader import clean_domain, select_domains


class DomainReaderTest(unittest.TestCase):
    def test_clean_domain(self) -> None:
        """Test domain cleanup.
        Args:
            self (DomainReaderTest): Test case instance."""
        clean_value = clean_domain('https://www.example.com/')
        self.assertEqual(clean_value, 'example.com')

    def test_select_domains(self) -> None:
        """Test domain selection.
        Args:
            self (DomainReaderTest): Test case instance."""
        domains = pd.DataFrame({'domain': ['example.com', 'test.com']})
        domain_list = select_domains(domains)
        self.assertEqual(domain_list, ['example.com', 'test.com'])
