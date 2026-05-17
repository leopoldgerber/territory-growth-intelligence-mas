"""create_initial_core_schema

Revision ID: 20260507_0001
Revises:
Create Date: 2026-05-07 00:00:00
"""
import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '20260507_0001'
down_revision = None
branch_labels = None
depends_on = None


def timestamp_column(name: str, nullable: bool = True) -> sa.Column:
    """Build timestamp column.
    Args:
        name (str): Column name.
        nullable (bool): Nullable flag."""
    column = sa.Column(name, sa.DateTime(timezone=True), nullable=nullable)
    return column


def now_column(name: str = 'created_at') -> sa.Column:
    """Build created timestamp column.
    Args:
        name (str): Column name."""
    column = sa.Column(name, sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    return column


def json_column(name: str) -> sa.Column:
    """Build JSONB column.
    Args:
        name (str): Column name."""
    column = sa.Column(name, postgresql.JSONB(astext_type=sa.Text()), nullable=True)
    return column


def numeric_column(name: str, precision: int = 20, scale: int = 4) -> sa.Column:
    """Build numeric column.
    Args:
        name (str): Column name.
        precision (int): Numeric precision.
        scale (int): Numeric scale."""
    column = sa.Column(name, sa.Numeric(precision, scale), nullable=True)
    return column


def identity_column(name: str) -> sa.Column:
    """Build identity primary key column.
    Args:
        name (str): Column name."""
    column = sa.Column(name, sa.BigInteger(), sa.Identity(), primary_key=True)
    return column


def create_ingestion() -> None:
    """Create ingestion tables.
    Args:
        None (None): No arguments are required."""
    op.create_table(
        'data_sources',
        identity_column('source_id'),
        sa.Column('source_name', sa.Text(), nullable=False, unique=True),
        sa.Column('source_type', sa.String(50), nullable=True),
        sa.Column('provider', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        now_column(),
    )
    op.create_table(
        'ingestion_runs',
        identity_column('run_id'),
        sa.Column('source_id', sa.BigInteger(), sa.ForeignKey('data_sources.source_id'), nullable=True),
        sa.Column('run_type', sa.String(50), nullable=True),
        sa.Column('granularity', sa.String(20), nullable=True),
        sa.Column('period_start', sa.Date(), nullable=True),
        sa.Column('period_end', sa.Date(), nullable=True),
        sa.Column('status', sa.String(30), nullable=True),
        timestamp_column('started_at'),
        timestamp_column('finished_at'),
        sa.Column('row_count', sa.BigInteger(), server_default=sa.text('0'), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        json_column('metadata'),
    )
    op.create_table(
        'source_files',
        identity_column('file_id'),
        sa.Column('run_id', sa.BigInteger(), sa.ForeignKey('ingestion_runs.run_id'), nullable=True),
        sa.Column('source_file_name', sa.Text(), nullable=False),
        sa.Column('report_type', sa.String(100), nullable=False),
        sa.Column('file_path', sa.Text(), nullable=True),
        sa.Column('file_hash', sa.Text(), nullable=True),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=True),
        sa.Column('schema_version', sa.String(50), nullable=True),
        sa.Column('is_synthetic', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        now_column(),
    )
    op.create_table(
        'data_quality_checks',
        identity_column('check_id'),
        sa.Column('run_id', sa.BigInteger(), sa.ForeignKey('ingestion_runs.run_id'), nullable=True),
        sa.Column('file_id', sa.BigInteger(), sa.ForeignKey('source_files.file_id'), nullable=True),
        sa.Column('table_name', sa.Text(), nullable=True),
        sa.Column('check_name', sa.Text(), nullable=False),
        sa.Column('check_type', sa.String(50), nullable=True),
        sa.Column('status', sa.String(30), nullable=True),
        sa.Column('expected_value', sa.Text(), nullable=True),
        sa.Column('actual_value', sa.Text(), nullable=True),
        json_column('details'),
        now_column(),
    )


def create_dimensions() -> None:
    """Create dimension tables.
    Args:
        None (None): No arguments are required."""
    op.create_table(
        'dim_date',
        sa.Column('date_id', sa.Integer(), primary_key=True),
        sa.Column('date', sa.Date(), nullable=False, unique=True),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('quarter', sa.Integer(), nullable=True),
        sa.Column('month_number', sa.Integer(), nullable=True),
        sa.Column('month_name_en', sa.Text(), nullable=True),
        sa.Column('month_name_ru', sa.Text(), nullable=True),
        sa.Column('month_year', sa.Text(), nullable=True),
        sa.Column('week_number', sa.Integer(), nullable=True),
        sa.Column('day_of_month', sa.Integer(), nullable=True),
        sa.Column('day_of_week', sa.Integer(), nullable=True),
        sa.Column('day_name_en', sa.Text(), nullable=True),
        sa.Column('day_name_ru', sa.Text(), nullable=True),
        sa.Column('is_weekend', sa.Boolean(), nullable=True),
        sa.Column('is_month_start', sa.Boolean(), nullable=True),
        sa.Column('is_month_end', sa.Boolean(), nullable=True),
    )
    op.create_table(
        'dim_company',
        identity_column('company_id'),
        sa.Column('company_name', sa.Text(), nullable=False),
        sa.Column('company_slug', sa.Text(), nullable=True, unique=True),
        sa.Column('company_type', sa.String(50), nullable=True),
        sa.Column('industry', sa.Text(), nullable=True),
        sa.Column('website_url', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        now_column(),
        now_column('updated_at'),
    )
    op.create_table(
        'dim_region',
        identity_column('region_id'),
        sa.Column('region_code', sa.Text(), nullable=True, unique=True),
        sa.Column('region_name', sa.Text(), nullable=False),
        sa.Column('macroregion', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        now_column(),
        now_column('updated_at'),
    )
    op.create_table(
        'dim_country',
        identity_column('country_id'),
        sa.Column('region_id', sa.BigInteger(), sa.ForeignKey('dim_region.region_id'), nullable=True),
        sa.Column('country_code', sa.String(10), nullable=True, unique=True),
        sa.Column('country_name_en', sa.Text(), nullable=False),
        sa.Column('country_name_ru', sa.Text(), nullable=True),
        sa.Column('location_name_ru', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        now_column(),
        now_column('updated_at'),
    )
    op.create_table(
        'dim_domain',
        identity_column('domain_id'),
        sa.Column('company_id', sa.BigInteger(), sa.ForeignKey('dim_company.company_id'), nullable=True),
        sa.Column('domain', sa.Text(), nullable=False, unique=True),
        sa.Column('root_domain', sa.Text(), nullable=True),
        sa.Column('domain_type', sa.String(50), nullable=True),
        sa.Column('is_competitor', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('first_seen_date', sa.Date(), nullable=True),
        sa.Column('last_seen_date', sa.Date(), nullable=True),
        now_column(),
        now_column('updated_at'),
    )
    op.create_table(
        'dim_channel',
        identity_column('channel_id'),
        sa.Column('channel_code', sa.String(50), nullable=False, unique=True),
        sa.Column('channel_name', sa.Text(), nullable=False),
        sa.Column('channel_group', sa.String(50), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        now_column(),
    )
    op.create_table(
        'dim_journey_source',
        identity_column('journey_source_id'),
        sa.Column('channel_id', sa.BigInteger(), sa.ForeignKey('dim_channel.channel_id'), nullable=True),
        sa.Column('source_name', sa.Text(), nullable=False),
        sa.Column('source_domain', sa.Text(), nullable=True),
        sa.Column('source_type', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        now_column(),
        sa.UniqueConstraint('source_name', 'channel_id', name='uq_dim_journey_source_name_channel'),
    )


def create_facts() -> None:
    """Create fact tables.
    Args:
        None (None): No arguments are required."""
    op.create_table(
        'fact_domain_country_daily',
        identity_column('domain_country_daily_id'),
        sa.Column('date_id', sa.Integer(), sa.ForeignKey('dim_date.date_id'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('domain_id', sa.BigInteger(), sa.ForeignKey('dim_domain.domain_id'), nullable=False),
        sa.Column('company_id', sa.BigInteger(), sa.ForeignKey('dim_company.company_id'), nullable=True),
        sa.Column('country_id', sa.BigInteger(), sa.ForeignKey('dim_country.country_id'), nullable=False),
        sa.Column('region_id', sa.BigInteger(), sa.ForeignKey('dim_region.region_id'), nullable=True),
        numeric_column('traffic'),
        numeric_column('traffic_share', 10, 6),
        numeric_column('desktop_traffic'),
        numeric_column('mobile_traffic'),
        numeric_column('desktop_share_traffic'),
        numeric_column('mobile_share_traffic'),
        numeric_column('unique_visitors'),
        numeric_column('pages_per_visit', 12, 4),
        numeric_column('avg_visit_duration_seconds'),
        numeric_column('bounce_rate', 10, 6),
        numeric_column('traffic_no_bounce'),
        numeric_column('traffic_bounce'),
        numeric_column('desktop_share_bounce'),
        numeric_column('mobile_share_bounce'),
        sa.Column('is_synthetic', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('source_file_id', sa.BigInteger(), sa.ForeignKey('source_files.file_id'), nullable=False),
        sa.Column('run_id', sa.BigInteger(), sa.ForeignKey('ingestion_runs.run_id'), nullable=True),
        sa.Column('source_row_id', sa.Text(), nullable=True),
        now_column(),
        sa.UniqueConstraint('date_id', 'domain_id', 'country_id', 'source_file_id', name='uq_country_daily_source'),
    )
    op.create_table(
        'fact_domain_device_daily',
        identity_column('domain_device_daily_id'),
        sa.Column('date_id', sa.Integer(), sa.ForeignKey('dim_date.date_id'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('domain_id', sa.BigInteger(), sa.ForeignKey('dim_domain.domain_id'), nullable=False),
        sa.Column('company_id', sa.BigInteger(), sa.ForeignKey('dim_company.company_id'), nullable=True),
        numeric_column('visits_total'),
        numeric_column('visits_desktop'),
        numeric_column('visits_mobile'),
        numeric_column('unique_total'),
        numeric_column('unique_desktop'),
        numeric_column('unique_mobile'),
        numeric_column('duration_total_seconds'),
        numeric_column('duration_desktop_seconds'),
        numeric_column('duration_mobile_seconds'),
        numeric_column('bounce_total'),
        numeric_column('bounce_desktop'),
        numeric_column('bounce_mobile'),
        numeric_column('all_no_bounce'),
        numeric_column('all_bounce'),
        numeric_column('desktop_no_bounce'),
        numeric_column('desktop_bounce'),
        numeric_column('mobile_no_bounce'),
        numeric_column('mobile_bounce'),
        numeric_column('desktop_share', 10, 6),
        numeric_column('mobile_share', 10, 6),
        numeric_column('bounce_rate_total', 10, 6),
        sa.Column('is_synthetic', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('source_file_id', sa.BigInteger(), sa.ForeignKey('source_files.file_id'), nullable=False),
        sa.Column('run_id', sa.BigInteger(), sa.ForeignKey('ingestion_runs.run_id'), nullable=True),
        sa.Column('source_row_id', sa.Text(), nullable=True),
        now_column(),
        sa.UniqueConstraint('date_id', 'domain_id', 'source_file_id', name='uq_device_daily_source'),
    )
    op.create_table(
        'fact_domain_channel_daily',
        identity_column('domain_channel_daily_id'),
        sa.Column('date_id', sa.Integer(), sa.ForeignKey('dim_date.date_id'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('domain_id', sa.BigInteger(), sa.ForeignKey('dim_domain.domain_id'), nullable=False),
        sa.Column('company_id', sa.BigInteger(), sa.ForeignKey('dim_company.company_id'), nullable=True),
        sa.Column('channel_id', sa.BigInteger(), sa.ForeignKey('dim_channel.channel_id'), nullable=False),
        numeric_column('traffic'),
        numeric_column('traffic_share', 10, 6),
        sa.Column('is_synthetic', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('source_file_id', sa.BigInteger(), sa.ForeignKey('source_files.file_id'), nullable=False),
        sa.Column('run_id', sa.BigInteger(), sa.ForeignKey('ingestion_runs.run_id'), nullable=True),
        sa.Column('source_row_id', sa.Text(), nullable=True),
        now_column(),
        sa.UniqueConstraint('date_id', 'domain_id', 'channel_id', 'source_file_id', name='uq_channel_daily_source'),
    )
    op.create_table(
        'fact_domain_journey_source_daily',
        identity_column('domain_journey_source_daily_id'),
        sa.Column('date_id', sa.Integer(), sa.ForeignKey('dim_date.date_id'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('domain_id', sa.BigInteger(), sa.ForeignKey('dim_domain.domain_id'), nullable=False),
        sa.Column('company_id', sa.BigInteger(), sa.ForeignKey('dim_company.company_id'), nullable=True),
        sa.Column('journey_source_id', sa.BigInteger(), sa.ForeignKey('dim_journey_source.journey_source_id'), nullable=False),
        sa.Column('channel_id', sa.BigInteger(), sa.ForeignKey('dim_channel.channel_id'), nullable=True),
        sa.Column('source_type', sa.String(100), nullable=True),
        sa.Column('traffic_type', sa.String(100), nullable=True),
        sa.Column('source_name_raw', sa.Text(), nullable=True),
        numeric_column('traffic'),
        numeric_column('traffic_share', 10, 6),
        numeric_column('change_value'),
        numeric_column('change_rate', 10, 6),
        sa.Column('is_synthetic', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('source_file_id', sa.BigInteger(), sa.ForeignKey('source_files.file_id'), nullable=False),
        sa.Column('run_id', sa.BigInteger(), sa.ForeignKey('ingestion_runs.run_id'), nullable=True),
        sa.Column('source_row_id', sa.Text(), nullable=True),
        now_column(),
        sa.UniqueConstraint(
            'date_id',
            'domain_id',
            'journey_source_id',
            'source_file_id',
            name='uq_journey_daily_source',
        ),
    )


def create_indexes() -> None:
    """Create fact indexes.
    Args:
        None (None): No arguments are required."""
    index_map = {
        'fact_domain_country_daily': [
            ('ix_fdc_date', ['date_id']),
            ('ix_fdc_domain', ['domain_id']),
            ('ix_fdc_company', ['company_id']),
            ('ix_fdc_country', ['country_id']),
            ('ix_fdc_run', ['run_id']),
            ('ix_fdc_file', ['source_file_id']),
            ('ix_fdc_country_date', ['country_id', 'date_id']),
            ('ix_fdc_domain_date', ['domain_id', 'date_id']),
            ('ix_fdc_country_domain_date', ['country_id', 'domain_id', 'date_id']),
        ],
        'fact_domain_device_daily': [
            ('ix_fdd_date', ['date_id']),
            ('ix_fdd_domain', ['domain_id']),
            ('ix_fdd_company', ['company_id']),
            ('ix_fdd_run', ['run_id']),
            ('ix_fdd_file', ['source_file_id']),
            ('ix_fdd_domain_date', ['domain_id', 'date_id']),
            ('ix_fdd_company_date', ['company_id', 'date_id']),
        ],
        'fact_domain_channel_daily': [
            ('ix_fch_date', ['date_id']),
            ('ix_fch_domain', ['domain_id']),
            ('ix_fch_company', ['company_id']),
            ('ix_fch_channel', ['channel_id']),
            ('ix_fch_run', ['run_id']),
            ('ix_fch_file', ['source_file_id']),
            ('ix_fch_domain_channel_date', ['domain_id', 'channel_id', 'date_id']),
            ('ix_fch_channel_date', ['channel_id', 'date_id']),
        ],
        'fact_domain_journey_source_daily': [
            ('ix_fjs_date', ['date_id']),
            ('ix_fjs_domain', ['domain_id']),
            ('ix_fjs_company', ['company_id']),
            ('ix_fjs_channel', ['channel_id']),
            ('ix_fjs_run', ['run_id']),
            ('ix_fjs_file', ['source_file_id']),
            ('ix_fjs_domain_source_date', ['domain_id', 'journey_source_id', 'date_id']),
            ('ix_fjs_channel_date', ['channel_id', 'date_id']),
        ],
    }
    for table_name, indexes in index_map.items():
        for index_name, columns in indexes:
            op.create_index(index_name, table_name, columns)


def date_rows() -> list[dict[str, object]]:
    """Build date seed rows.
    Args:
        None (None): No arguments are required."""
    month_names_ru = [
        'January',
        'February',
        'March',
        'April',
        'May',
        'June',
        'July',
        'August',
        'September',
        'October',
        'November',
        'December',
    ]
    day_names_ru = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    start_date = datetime.date(2020, 1, 1)
    end_date = datetime.date(2030, 12, 31)
    rows = []
    current_date = start_date
    while current_date <= end_date:
        iso_year, week_number, day_number = current_date.isocalendar()
        next_day = current_date + datetime.timedelta(days=1)
        rows.append(
            {
                'date_id': int(current_date.strftime('%Y%m%d')),
                'date': current_date,
                'year': current_date.year,
                'quarter': ((current_date.month - 1) // 3) + 1,
                'month_number': current_date.month,
                'month_name_en': current_date.strftime('%B'),
                'month_name_ru': month_names_ru[current_date.month - 1],
                'month_year': current_date.strftime('%Y-%m'),
                'week_number': week_number,
                'day_of_month': current_date.day,
                'day_of_week': day_number,
                'day_name_en': current_date.strftime('%A'),
                'day_name_ru': day_names_ru[day_number - 1],
                'is_weekend': day_number in [6, 7],
                'is_month_start': current_date.day == 1,
                'is_month_end': next_day.month != current_date.month,
            },
        )
        current_date = next_day
    return rows


def seed_data() -> None:
    """Seed dimension data.
    Args:
        None (None): No arguments are required."""
    channel_table = sa.table(
        'dim_channel',
        sa.column('channel_code'),
        sa.column('channel_name'),
        sa.column('channel_group'),
    )
    source_table = sa.table(
        'data_sources',
        sa.column('source_name'),
        sa.column('source_type'),
        sa.column('provider'),
        sa.column('description'),
    )
    date_table = sa.table(
        'dim_date',
        sa.column('date_id'),
        sa.column('date'),
        sa.column('year'),
        sa.column('quarter'),
        sa.column('month_number'),
        sa.column('month_name_en'),
        sa.column('month_name_ru'),
        sa.column('month_year'),
        sa.column('week_number'),
        sa.column('day_of_month'),
        sa.column('day_of_week'),
        sa.column('day_name_en'),
        sa.column('day_name_ru'),
        sa.column('is_weekend'),
        sa.column('is_month_start'),
        sa.column('is_month_end'),
    )
    op.bulk_insert(
        channel_table,
        [
            {'channel_code': 'direct', 'channel_name': 'Direct', 'channel_group': 'owned'},
            {'channel_code': 'referral', 'channel_name': 'Referral', 'channel_group': 'earned'},
            {'channel_code': 'paid', 'channel_name': 'Paid', 'channel_group': 'paid'},
            {'channel_code': 'social', 'channel_name': 'Social', 'channel_group': 'earned'},
            {'channel_code': 'search', 'channel_name': 'Search', 'channel_group': 'organic'},
        ],
    )
    op.bulk_insert(
        source_table,
        [
            {
                'source_name': 'semrush_parser',
                'source_type': 'parser',
                'provider': 'Semrush',
                'description': 'Semrush parser output',
            },
            {
                'source_name': 'synthetic_daily_reports',
                'source_type': 'synthetic',
                'provider': 'Internal',
                'description': 'Synthetic daily report generator',
            },
            {
                'source_name': 'manual_upload',
                'source_type': 'manual',
                'provider': 'Internal',
                'description': 'Manual file upload',
            },
        ],
    )
    op.bulk_insert(date_table, date_rows())


def upgrade() -> None:
    """Apply migration.
    Args:
        None (None): No arguments are required."""
    create_ingestion()
    create_dimensions()
    create_facts()
    create_indexes()
    seed_data()


def downgrade() -> None:
    """Rollback migration.
    Args:
        None (None): No arguments are required."""
    tables = [
        'fact_domain_journey_source_daily',
        'fact_domain_channel_daily',
        'fact_domain_device_daily',
        'fact_domain_country_daily',
        'data_quality_checks',
        'source_files',
        'ingestion_runs',
        'dim_journey_source',
        'dim_channel',
        'dim_domain',
        'dim_country',
        'dim_region',
        'dim_company',
        'dim_date',
        'data_sources',
    ]
    for table_name in tables:
        op.drop_table(table_name)
