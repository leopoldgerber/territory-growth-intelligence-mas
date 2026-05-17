import unittest
from pathlib import Path


class MigrationSchemaTest(unittest.TestCase):
    def test_initial_tables(self: 'MigrationSchemaTest') -> None:
        """Test initial migration table list.
        Args:
            self (MigrationSchemaTest): Test case instance."""
        migration_path = Path('alembic/versions/20260507_0001_create_initial_core_schema.py')
        migration_text = migration_path.read_text(encoding='utf-8')
        table_names = [
            'data_sources',
            'ingestion_runs',
            'source_files',
            'data_quality_checks',
            'dim_date',
            'dim_company',
            'dim_domain',
            'dim_region',
            'dim_country',
            'dim_channel',
            'dim_journey_source',
            'fact_domain_country_daily',
            'fact_domain_device_daily',
            'fact_domain_channel_daily',
            'fact_domain_journey_source_daily',
        ]
        for table_name in table_names:
            self.assertIn(table_name, migration_text)

    def test_seed_values(self: 'MigrationSchemaTest') -> None:
        """Test migration seed values.
        Args:
            self (MigrationSchemaTest): Test case instance."""
        migration_path = Path('alembic/versions/20260507_0001_create_initial_core_schema.py')
        migration_text = migration_path.read_text(encoding='utf-8')
        self.assertIn('semrush_parser', migration_text)
        self.assertIn('synthetic_daily_reports', migration_text)
        self.assertIn('manual_upload', migration_text)
        self.assertIn('direct', migration_text)
        self.assertIn('search', migration_text)
