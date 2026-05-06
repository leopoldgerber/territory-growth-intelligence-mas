import os
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path


@dataclass(frozen=True)
class AppSettings:
    semrush_url: str
    semrush_email: str
    semrush_password: str
    chromedriver_path: Path
    downloads_path: Path
    domains_path: Path
    countries_path: Path
    output_path: Path
    first_domain: str
    domain_amount: int
    start_index: int
    end_index: int
    report_months: int
    month_year: int
    retry_attempts: int
    retry_pause: float


def load_env_file() -> bool:
    """Load local environment file.
    Args:
        None (None): No arguments are required."""
    try:
        dotenv_module = import_module('dotenv')
    except ImportError:
        return False
    dotenv_module.load_dotenv()
    return True


def read_integer(name: str, default: int) -> int:
    """Read integer environment value.
    Args:
        name (str): Environment variable name.
        default (int): Default value."""
    value = os.getenv(name)
    if value is None or value.strip() == '':
        return default
    return int(value)


def read_float(name: str, default: float) -> float:
    """Read float environment value.
    Args:
        name (str): Environment variable name.
        default (float): Default value."""
    value = os.getenv(name)
    if value is None or value.strip() == '':
        return default
    return float(value)


def read_path(name: str, default: Path) -> Path:
    """Read path environment value.
    Args:
        name (str): Environment variable name.
        default (Path): Default path."""
    value = os.getenv(name)
    if value is None or value.strip() == '':
        return default
    return Path(value)


def load_settings() -> AppSettings:
    """Load application settings.
    Args:
        None (None): No arguments are required."""
    load_env_file()
    downloads_path = read_path('DOWNLOADS_PATH', Path.home() / 'Downloads')
    domains_path = read_path('DOMAINS_PATH', downloads_path / 'domains.csv')
    countries_path = read_path('COUNTRIES_PATH', downloads_path / 'countries.csv')
    output_path = read_path('OUTPUT_PATH', Path.cwd() / 'output')
    domain_amount = read_integer('DOMAIN_AMOUNT', 5)
    start_index = read_integer('START_INDEX', 0)
    end_index = read_integer('END_INDEX', start_index + domain_amount)
    return AppSettings(
        semrush_url=os.getenv(
            'SEMRUSH_URL',
            'https://www.semrush.com/login/?src=header&redirect_to=%2Fanalytics%2Foverview%2F%3FsearchType%3Ddomain',
        ),
        semrush_email=os.getenv('SEMRUSH_EMAIL', ''),
        semrush_password=os.getenv('SEMRUSH_PASSWORD', ''),
        chromedriver_path=read_path('CHROMEDRIVER_PATH', Path('chromedriver.exe')),
        downloads_path=downloads_path,
        domains_path=domains_path,
        countries_path=countries_path,
        output_path=output_path,
        first_domain=os.getenv('FIRST_DOMAIN', 'www.google.com'),
        domain_amount=domain_amount,
        start_index=start_index,
        end_index=end_index,
        report_months=read_integer('REPORT_MONTHS', 8),
        month_year=read_integer('MONTH_YEAR', 2022),
        retry_attempts=read_integer('RETRY_ATTEMPTS', 3),
        retry_pause=read_float('RETRY_PAUSE', 2.0),
    )
