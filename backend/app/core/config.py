from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = 'Territory Growth Intelligence MAS'
    app_env: str = 'local'
    debug: bool = True
    backend_host: str = '0.0.0.0'
    backend_port: int = 8000
    postgres_host: str = 'postgres'
    postgres_port: int = 5432
    postgres_db: str = 'tgi_db'
    postgres_user: str = 'tgi_user'
    postgres_password: str = 'tgi_password'
    frontend_url: str = 'http://localhost:5173'
    cors_origins: str = 'http://localhost:5173'
    upload_storage_path: str = 'uploads'
    max_upload_size_mb: int = 50
    auth_secret_key: str = 'change-me-local-secret'
    access_token_minutes: int = 60
    refresh_token_days: int = 14
    redis_url: str = 'redis://redis:6379/0'
    celery_broker_url: str = 'redis://redis:6379/0'
    celery_result_backend: str = 'redis://redis:6379/1'
    log_level: str = 'INFO'
    log_json: bool = True
    sentry_dsn: str = ''
    sentry_environment: str = 'local'
    metrics_enabled: bool = True
    worker_ping_enabled: bool = True
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    @property
    def cors_origin_list(self) -> list[str]:
        """Build CORS origins.
        Args:
            self (Settings): Application settings."""
        items = [item.strip() for item in self.cors_origins.split(',') if item.strip() != '']
        return items if len(items) > 0 else [self.frontend_url]

    @property
    def database_url(self) -> str:
        """Build database URL.
        Args:
            self (Settings): Application settings."""
        return (
            f'postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}'
            f'@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}'
        )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings.
    Args:
        None (None): No arguments are required."""
    settings = Settings()
    return settings
