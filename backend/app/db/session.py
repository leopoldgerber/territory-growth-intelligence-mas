from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


def create_db_engine() -> object:
    """Create database engine.
    Args:
        None (None): No arguments are required."""
    settings = get_settings()
    engine = create_engine(settings.database_url, pool_pre_ping=True)
    return engine


engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session() -> Generator[Session, None, None]:
    """Get database session.
    Args:
        None (None): No arguments are required."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def check_database() -> bool:
    """Check database connection.
    Args:
        None (None): No arguments are required."""
    with engine.connect() as connection:
        connection.execute(text('SELECT 1'))
    return True


def check_migrations() -> bool:
    """Check migration state.
    Args:
        None (None): No arguments are required."""
    with engine.connect() as connection:
        result = connection.execute(text('SELECT version_num FROM alembic_version LIMIT 1'))
        row = result.first()
    return row is not None
