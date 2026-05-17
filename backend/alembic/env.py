from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import get_settings
from app.db.base import Base


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def database_url() -> str:
    """Build migration database URL.
    Args:
        None (None): No arguments are required."""
    settings = get_settings()
    return settings.database_url


def run_offline() -> None:
    """Run migrations offline.
    Args:
        None (None): No arguments are required."""
    context.configure(
        url=database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_online() -> None:
    """Run migrations online.
    Args:
        None (None): No arguments are required."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration['sqlalchemy.url'] = database_url()
    connectable = engine_from_config(
        configuration,
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_offline()
else:
    run_online()
