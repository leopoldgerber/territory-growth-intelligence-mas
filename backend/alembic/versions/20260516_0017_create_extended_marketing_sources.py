"""create_extended_marketing_sources

Revision ID: 20260516_0017
Revises: 20260516_0016
Create Date: 2026-05-16 00:17:00
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = '20260516_0017'
down_revision = '20260516_0016'
branch_labels = None
depends_on = None


def id_column(name: str) -> sa.Column:
    """Build id column.
    Args:
        name (str): Column name."""
    column = sa.Column(name, sa.BigInteger(), sa.Identity(), primary_key=True)
    return column


def now_column(name: str = 'created_at') -> sa.Column:
    """Build timestamp column.
    Args:
        name (str): Column name."""
    column = sa.Column(name, sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False)
    return column


def num_column(name: str, precision: int = 20, scale: int = 4) -> sa.Column:
    """Build numeric column.
    Args:
        name (str): Column name.
        precision (int): Numeric precision.
        scale (int): Numeric scale."""
    column = sa.Column(name, sa.Numeric(precision, scale), nullable=True)
    return column


def fact_columns() -> list[sa.Column]:
    """Build common fact columns.
    Args:
        None (None): No arguments are required."""
    columns = [
        sa.Column('date_id', sa.Integer(), sa.ForeignKey('dim_date.date_id'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('domain_id', sa.BigInteger(), sa.ForeignKey('dim_domain.domain_id'), nullable=False),
        sa.Column('company_id', sa.BigInteger(), sa.ForeignKey('dim_company.company_id'), nullable=True),
        sa.Column('country_id', sa.BigInteger(), sa.ForeignKey('dim_country.country_id'), nullable=True),
        sa.Column('is_synthetic', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('source_file_id', sa.BigInteger(), sa.ForeignKey('source_files.file_id'), nullable=False),
        sa.Column('run_id', sa.BigInteger(), sa.ForeignKey('ingestion_runs.run_id'), nullable=True),
        sa.Column('source_row_id', sa.Text(), nullable=True),
        now_column(),
    ]
    return columns


def create_dimensions() -> None:
    """Create extended dimensions.
    Args:
        None (None): No arguments are required."""
    op.create_table(
        'dim_audience_segment',
        id_column('audience_segment_id'),
        sa.Column('segment_type', sa.String(50), nullable=False),
        sa.Column('segment_name', sa.Text(), nullable=False),
        sa.Column('segment_value', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        now_column(),
        sa.UniqueConstraint('segment_type', 'segment_name', 'segment_value', name='uq_audience_segment_identity'),
    )
    op.create_table(
        'dim_keyword',
        id_column('keyword_id'),
        sa.Column('keyword_text', sa.Text(), nullable=False),
        sa.Column('keyword_normalized', sa.Text(), nullable=False),
        sa.Column('language_code', sa.String(10), nullable=True),
        sa.Column('country_id', sa.BigInteger(), sa.ForeignKey('dim_country.country_id'), nullable=True),
        sa.Column('intent', sa.String(50), server_default='unknown', nullable=False),
        sa.Column('is_branded', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        now_column(),
        sa.UniqueConstraint('keyword_normalized', 'country_id', 'language_code', name='uq_keyword_country_language'),
    )
    op.create_table(
        'dim_page',
        id_column('page_id'),
        sa.Column('domain_id', sa.BigInteger(), sa.ForeignKey('dim_domain.domain_id'), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('url_hash', sa.Text(), nullable=False),
        sa.Column('page_path', sa.Text(), nullable=True),
        sa.Column('page_type', sa.String(100), server_default='unknown', nullable=False),
        sa.Column('title', sa.Text(), nullable=True),
        sa.Column('first_seen_date', sa.Date(), nullable=True),
        sa.Column('last_seen_date', sa.Date(), nullable=True),
        now_column(),
        sa.UniqueConstraint('url_hash', name='uq_dim_page_url_hash'),
    )


def create_facts() -> None:
    """Create extended fact tables.
    Args:
        None (None): No arguments are required."""
    op.create_table(
        'fact_audience_demographics_daily',
        id_column('audience_daily_id'),
        *fact_columns(),
        sa.Column('audience_segment_id', sa.BigInteger(), sa.ForeignKey('dim_audience_segment.audience_segment_id'), nullable=False),
        num_column('traffic'),
        num_column('traffic_share', 10, 6),
        num_column('confidence_score', 10, 6),
        sa.UniqueConstraint('date_id', 'domain_id', 'country_id', 'audience_segment_id', 'source_file_id', name='uq_audience_daily_source'),
    )
    op.create_table(
        'fact_organic_keyword_daily',
        id_column('organic_keyword_daily_id'),
        *fact_columns(),
        sa.Column('keyword_id', sa.BigInteger(), sa.ForeignKey('dim_keyword.keyword_id'), nullable=False),
        sa.Column('page_id', sa.BigInteger(), sa.ForeignKey('dim_page.page_id'), nullable=True),
        num_column('position', 10, 4),
        num_column('previous_position', 10, 4),
        num_column('search_volume'),
        num_column('estimated_traffic'),
        num_column('traffic_share', 10, 6),
        num_column('keyword_difficulty', 10, 6),
        sa.Column('serp_features', postgresql.JSONB(), nullable=True),
        sa.UniqueConstraint('date_id', 'domain_id', 'country_id', 'keyword_id', 'source_file_id', name='uq_organic_keyword_source'),
    )
    op.create_table(
        'fact_paid_keyword_daily',
        id_column('paid_keyword_daily_id'),
        *fact_columns(),
        sa.Column('keyword_id', sa.BigInteger(), sa.ForeignKey('dim_keyword.keyword_id'), nullable=False),
        sa.Column('page_id', sa.BigInteger(), sa.ForeignKey('dim_page.page_id'), nullable=True),
        num_column('position', 10, 4),
        num_column('search_volume'),
        num_column('estimated_traffic'),
        num_column('traffic_share', 10, 6),
        num_column('cpc', 20, 6),
        num_column('estimated_cost'),
        num_column('competition', 10, 6),
        sa.Column('currency_code', sa.String(3), server_default='USD', nullable=False),
        sa.UniqueConstraint('date_id', 'domain_id', 'country_id', 'keyword_id', 'source_file_id', name='uq_paid_keyword_source'),
    )
    op.create_table(
        'fact_top_page_daily',
        id_column('top_page_daily_id'),
        *fact_columns(),
        sa.Column('page_id', sa.BigInteger(), sa.ForeignKey('dim_page.page_id'), nullable=False),
        num_column('estimated_traffic'),
        num_column('traffic_share', 10, 6),
        num_column('organic_traffic'),
        num_column('paid_traffic'),
        sa.Column('keywords_count', sa.Integer(), nullable=True),
        sa.Column('backlinks_count', sa.Integer(), nullable=True),
        sa.UniqueConstraint('date_id', 'domain_id', 'country_id', 'page_id', 'source_file_id', name='uq_top_page_source'),
    )
    op.create_table(
        'fact_ad_creative_daily',
        id_column('ad_creative_daily_id'),
        *fact_columns(),
        sa.Column('creative_hash', sa.Text(), nullable=False),
        sa.Column('headline', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('cta', sa.Text(), nullable=True),
        sa.Column('landing_page_id', sa.BigInteger(), sa.ForeignKey('dim_page.page_id'), nullable=True),
        sa.Column('ad_network', sa.Text(), nullable=True),
        num_column('estimated_spend'),
        num_column('estimated_traffic'),
        sa.Column('first_seen_date', sa.Date(), nullable=True),
        sa.Column('last_seen_date', sa.Date(), nullable=True),
        sa.UniqueConstraint('date_id', 'domain_id', 'country_id', 'creative_hash', 'source_file_id', name='uq_ad_creative_source'),
    )
    op.create_table(
        'fact_referring_domain_daily',
        id_column('referring_domain_daily_id'),
        *fact_columns(),
        sa.Column('referring_domain', sa.Text(), nullable=False),
        sa.Column('source_url', sa.Text(), nullable=True),
        sa.Column('target_url', sa.Text(), nullable=True),
        sa.Column('link_type', sa.String(50), nullable=True),
        sa.Column('anchor_text', sa.Text(), nullable=True),
        sa.Column('backlinks_count', sa.Integer(), nullable=True),
        num_column('authority_score', 10, 6),
        num_column('estimated_referral_traffic'),
        sa.UniqueConstraint('date_id', 'domain_id', 'country_id', 'referring_domain', 'source_file_id', name='uq_referring_domain_source'),
    )


def create_business() -> None:
    """Create business tables.
    Args:
        None (None): No arguments are required."""
    op.create_table(
        'business_assumptions',
        id_column('assumption_id'),
        sa.Column('project_id', sa.BigInteger(), sa.ForeignKey('projects.project_id'), nullable=False),
        sa.Column('country_id', sa.BigInteger(), sa.ForeignKey('dim_country.country_id'), nullable=True),
        sa.Column('currency_code', sa.String(3), server_default='EUR', nullable=False),
        num_column('visit_to_lead_rate', 10, 6),
        num_column('lead_to_client_rate', 10, 6),
        num_column('average_order_value', 20, 4),
        num_column('ltv', 20, 4),
        num_column('gross_margin', 10, 6),
        num_column('target_cac', 20, 4),
        num_column('monthly_budget', 20, 4),
        num_column('confidence_score', 10, 6),
        sa.Column('valid_from', sa.Date(), nullable=True),
        sa.Column('valid_to', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        now_column(),
        now_column('updated_at'),
    )
    op.create_table(
        'campaigns',
        id_column('campaign_id'),
        sa.Column('project_id', sa.BigInteger(), sa.ForeignKey('projects.project_id'), nullable=False),
        sa.Column('campaign_name', sa.Text(), nullable=False),
        sa.Column('channel_code', sa.String(50), nullable=True),
        sa.Column('country_id', sa.BigInteger(), sa.ForeignKey('dim_country.country_id'), nullable=True),
        sa.Column('status', sa.String(30), server_default='active', nullable=False),
        sa.Column('currency_code', sa.String(3), server_default='EUR', nullable=False),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        now_column(),
        now_column('updated_at'),
    )
    op.create_table(
        'campaign_performance_daily',
        id_column('campaign_performance_id'),
        sa.Column('campaign_id', sa.BigInteger(), sa.ForeignKey('campaigns.campaign_id'), nullable=False),
        sa.Column('project_id', sa.BigInteger(), sa.ForeignKey('projects.project_id'), nullable=False),
        sa.Column('date_id', sa.Integer(), sa.ForeignKey('dim_date.date_id'), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        num_column('impressions'),
        num_column('clicks'),
        num_column('visits'),
        num_column('spend'),
        num_column('leads'),
        num_column('clients'),
        num_column('revenue'),
        num_column('cac'),
        num_column('roas', 10, 6),
        num_column('roi', 10, 6),
        sa.Column('source_file_id', sa.BigInteger(), sa.ForeignKey('source_files.file_id'), nullable=True),
        sa.Column('run_id', sa.BigInteger(), sa.ForeignKey('ingestion_runs.run_id'), nullable=True),
        now_column(),
        sa.UniqueConstraint('campaign_id', 'date_id', name='uq_campaign_performance_daily'),
    )


def create_indexes() -> None:
    """Create indexes.
    Args:
        None (None): No arguments are required."""
    index_map = {
        'fact_audience_demographics_daily': [('ix_audience_country_date', ['country_id', 'date_id']), ('ix_audience_file', ['source_file_id'])],
        'fact_organic_keyword_daily': [('ix_organic_country_date', ['country_id', 'date_id']), ('ix_organic_keyword', ['keyword_id'])],
        'fact_paid_keyword_daily': [('ix_paid_country_date', ['country_id', 'date_id']), ('ix_paid_keyword', ['keyword_id'])],
        'fact_top_page_daily': [('ix_top_page_country_date', ['country_id', 'date_id']), ('ix_top_page_page', ['page_id'])],
        'fact_ad_creative_daily': [('ix_ad_country_date', ['country_id', 'date_id']), ('ix_ad_hash', ['creative_hash'])],
        'fact_referring_domain_daily': [('ix_ref_country_date', ['country_id', 'date_id']), ('ix_ref_domain', ['referring_domain'])],
        'business_assumptions': [('ix_assumptions_project', ['project_id']), ('ix_assumptions_country', ['country_id'])],
        'campaigns': [('ix_campaigns_project', ['project_id']), ('ix_campaigns_country', ['country_id'])],
        'campaign_performance_daily': [('ix_campaign_perf_project', ['project_id']), ('ix_campaign_perf_campaign_date', ['campaign_id', 'date_id'])],
    }
    for table_name, indexes in index_map.items():
        for index_name, columns in indexes:
            op.create_index(index_name, table_name, columns)


def upgrade() -> None:
    """Apply migration.
    Args:
        None (None): No arguments are required."""
    create_dimensions()
    create_facts()
    create_business()
    create_indexes()


def downgrade() -> None:
    """Rollback migration.
    Args:
        None (None): No arguments are required."""
    tables = [
        'campaign_performance_daily',
        'campaigns',
        'business_assumptions',
        'fact_referring_domain_daily',
        'fact_ad_creative_daily',
        'fact_top_page_daily',
        'fact_paid_keyword_daily',
        'fact_organic_keyword_daily',
        'fact_audience_demographics_daily',
        'dim_page',
        'dim_keyword',
        'dim_audience_segment',
    ]
    for table_name in tables:
        op.drop_table(table_name)
