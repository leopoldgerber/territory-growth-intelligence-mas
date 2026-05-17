"""create_auth_project_tables

Revision ID: 20260516_0014
Revises: 20260516_0013
Create Date: 2026-05-16 00:00:00
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = '20260516_0014'
down_revision = '20260516_0013'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply migration.
    Args:
        None (None): No arguments are required."""
    op.create_table(
        'users',
        sa.Column('user_id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('email', sa.Text(), nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('full_name', sa.Text(), nullable=True),
        sa.Column('status', sa.String(30), server_default='active', nullable=False),
        sa.Column('is_superadmin', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_unique_constraint('uq_users_email', 'users', ['email'])
    op.create_table(
        'projects',
        sa.Column('project_id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('project_name', sa.Text(), nullable=False),
        sa.Column('project_slug', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('own_company_id', sa.BigInteger(), sa.ForeignKey('dim_company.company_id'), nullable=True),
        sa.Column('default_currency_code', sa.String(3), server_default='EUR', nullable=False),
        sa.Column('status', sa.String(30), server_default='active', nullable=False),
        sa.Column('settings', postgresql.JSONB(), nullable=True),
        sa.Column('created_by_user_id', sa.BigInteger(), sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_unique_constraint('uq_projects_slug', 'projects', ['project_slug'])
    op.create_table(
        'project_members',
        sa.Column('project_member_id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('project_id', sa.BigInteger(), sa.ForeignKey('projects.project_id'), nullable=False),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('role', sa.String(30), nullable=False),
        sa.Column('status', sa.String(30), server_default='active', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_unique_constraint('uq_project_members_user', 'project_members', ['project_id', 'user_id'])
    op.create_table(
        'project_competitors',
        sa.Column('project_competitor_id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('project_id', sa.BigInteger(), sa.ForeignKey('projects.project_id'), nullable=False),
        sa.Column('company_id', sa.BigInteger(), sa.ForeignKey('dim_company.company_id'), nullable=True),
        sa.Column('domain_id', sa.BigInteger(), sa.ForeignKey('dim_domain.domain_id'), nullable=False),
        sa.Column('competitor_tier', sa.String(50), server_default='unknown', nullable=False),
        sa.Column('priority', sa.String(30), server_default='medium', nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_unique_constraint('uq_project_competitors_domain', 'project_competitors', ['project_id', 'domain_id'])
    op.create_table(
        'project_target_countries',
        sa.Column('project_target_country_id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('project_id', sa.BigInteger(), sa.ForeignKey('projects.project_id'), nullable=False),
        sa.Column('country_id', sa.BigInteger(), sa.ForeignKey('dim_country.country_id'), nullable=False),
        sa.Column('status', sa.String(50), server_default='watchlist', nullable=False),
        sa.Column('strategic_priority', sa.String(30), server_default='medium', nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.create_unique_constraint('uq_project_target_countries_country', 'project_target_countries', ['project_id', 'country_id'])
    op.create_table(
        'refresh_tokens',
        sa.Column('refresh_token_id', sa.BigInteger(), sa.Identity(), primary_key=True),
        sa.Column('user_id', sa.BigInteger(), sa.ForeignKey('users.user_id'), nullable=False),
        sa.Column('token_hash', sa.Text(), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )
    op.add_column('workflow_runs', sa.Column('project_id', sa.BigInteger(), sa.ForeignKey('projects.project_id'), nullable=True))
    op.add_column('agent_runs', sa.Column('project_id', sa.BigInteger(), sa.ForeignKey('projects.project_id'), nullable=True))
    op.add_column('report_snapshots', sa.Column('project_id', sa.BigInteger(), sa.ForeignKey('projects.project_id'), nullable=True))
    op.add_column('budget_strategy_runs', sa.Column('project_id', sa.BigInteger(), sa.ForeignKey('projects.project_id'), nullable=True))
    op.add_column('saved_summaries', sa.Column('project_id', sa.BigInteger(), sa.ForeignKey('projects.project_id'), nullable=True))
    op.add_column('anomaly_events', sa.Column('project_id', sa.BigInteger(), sa.ForeignKey('projects.project_id'), nullable=True))
    op.create_index('idx_project_members_project', 'project_members', ['project_id'])
    op.create_index('idx_project_competitors_project', 'project_competitors', ['project_id'])
    op.create_index('idx_project_target_countries_project', 'project_target_countries', ['project_id'])
    op.create_index('idx_workflow_runs_project', 'workflow_runs', ['project_id'])


def downgrade() -> None:
    """Rollback migration.
    Args:
        None (None): No arguments are required."""
    op.drop_index('idx_workflow_runs_project', table_name='workflow_runs')
    op.drop_index('idx_project_target_countries_project', table_name='project_target_countries')
    op.drop_index('idx_project_competitors_project', table_name='project_competitors')
    op.drop_index('idx_project_members_project', table_name='project_members')
    op.drop_column('anomaly_events', 'project_id')
    op.drop_column('saved_summaries', 'project_id')
    op.drop_column('budget_strategy_runs', 'project_id')
    op.drop_column('report_snapshots', 'project_id')
    op.drop_column('agent_runs', 'project_id')
    op.drop_column('workflow_runs', 'project_id')
    op.drop_table('refresh_tokens')
    op.drop_table('project_target_countries')
    op.drop_table('project_competitors')
    op.drop_table('project_members')
    op.drop_table('projects')
    op.drop_table('users')
