from pathlib import Path

import pandas as pd


def check_file(file_path: Path) -> Path:
    """Check file exists.
    Args:
        file_path (Path): File path."""
    if not file_path.exists():
        raise FileNotFoundError(f'CSV file not found: {file_path}')
    return file_path


def read_csv(file_path: Path, separator: str = ',', encoding: str | None = None) -> pd.DataFrame:
    """Read CSV file.
    Args:
        file_path (Path): CSV file path.
        separator (str): CSV separator.
        encoding (str | None): File encoding."""
    check_file(file_path)
    read_params = {'sep': separator}
    if encoding is not None:
        read_params['encoding'] = encoding
    data = pd.read_csv(file_path, **read_params)
    return data


def overview_files(downloads_path: Path) -> list[Path]:
    """List overview files.
    Args:
        downloads_path (Path): Downloads directory."""
    overview_path = downloads_path / 'overview'
    file_list = sorted(overview_path.glob('*.csv'))
    return file_list


def metric_file(downloads_path: Path, domain: str, metric_name: str, first_month: str, last_month: str, year: str) -> Path:
    """Build metric file path.
    Args:
        downloads_path (Path): Downloads directory.
        domain (str): Domain name.
        metric_name (str): Metric name.
        first_month (str): First month.
        last_month (str): Last month.
        year (str): Year value."""
    filename = (
        f'Trend By Devices (domain={domain}, metric={metric_name}, '
        f'range={first_month} \u2013 {last_month} {year}, devices=all_devices,desktop,mobile).csv'
    )
    return downloads_path / filename


def sources_file(downloads_path: Path, domain: str, first_month: str, last_month: str, year: str) -> Path:
    """Build traffic sources file path.
    Args:
        downloads_path (Path): Downloads directory.
        domain (str): Domain name.
        first_month (str): First month.
        last_month (str): Last month.
        year (str): Year value."""
    filename = f'Traffic Sources by Type (domain={domain}, range={first_month} {year} \u2013 {last_month} {year}).csv'
    return downloads_path / filename


def journey_file(downloads_path: Path, domain: str, month_name: str, year: str) -> Path:
    """Build journey file path.
    Args:
        downloads_path (Path): Downloads directory.
        domain (str): Domain name.
        month_name (str): Month name.
        year (str): Year value."""
    filename = f'All Sources (date={month_name} {year}, target={domain}).csv'
    return downloads_path / filename


def traffic_file(downloads_path: Path, month_name: str, year: str, index: int) -> Path:
    """Build traffic countries file path.
    Args:
        downloads_path (Path): Downloads directory.
        month_name (str): Month name.
        year (str): Year value.
        index (int): Download file index."""
    suffix = '' if index == 0 else f' ({index})'
    filename = f'Traffic by Country (date={month_name} {year}, geoType=country){suffix}.csv'
    return downloads_path / filename


def backlinks_file(downloads_path: Path, domain: str, report_name: str) -> Path:
    """Build backlinks file path.
    Args:
        downloads_path (Path): Downloads directory.
        domain (str): Domain name.
        report_name (str): Report name."""
    return downloads_path / f'{domain}-{report_name}.csv'
