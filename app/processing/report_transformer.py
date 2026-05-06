from pathlib import Path

import pandas as pd

from app.processing import country_mapper, file_parser, month_utils
from app.utils.progress_tracker import ProgressState


METRIC_FILES = {
    'visits': 'visits',
    'unique_users': 'users',
    'duration': 'time_on_site',
    'bounce_rate': 'bounce_rate',
}

METRIC_COLUMNS = {
    'visits': {
        'all_devices': 'visits',
        'desktop': 'desktop',
        'mobile': 'mobile',
    },
    'unique_users': {
        'all_devices': 'unique',
        'desktop': 'desktop_unique',
        'mobile': 'mobile_unique',
    },
    'duration': {
        'all_devices': 'duration',
        'desktop': 'desktop_duration',
        'mobile': 'mobile_duration',
    },
    'bounce_rate': {
        'all_devices': 'bounce',
        'desktop': 'desktop_bounce_rate',
        'mobile': 'mobile_bounce_rate',
    },
}


def standardize_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Standardize report columns.
    Args:
        data (pd.DataFrame): Report data."""
    standardized_data = data.copy()
    standardized_data.columns = (
        standardized_data.columns
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(' ', '_', regex=False)
    )
    return standardized_data


def numeric_series(data: pd.Series) -> pd.Series:
    """Convert values to numeric series.
    Args:
        data (pd.Series): Source values."""
    clean_data = data.astype(str).str.replace('%', '', regex=False).str.replace(',', '.', regex=False)
    numeric_data = pd.to_numeric(clean_data, errors='coerce').fillna(0)
    return numeric_data


def calculate_metrics(data: pd.DataFrame) -> pd.DataFrame:
    """Calculate compatible metric fields.
    Args:
        data (pd.DataFrame): Wide metric data."""
    calculated_data = data.copy()
    required_columns = [
        'visits',
        'desktop',
        'mobile',
        'bounce',
        'desktop_bounce_rate',
        'mobile_bounce_rate',
    ]
    for column_name in required_columns:
        if column_name not in calculated_data.columns:
            calculated_data[column_name] = 0
        calculated_data[column_name] = numeric_series(calculated_data[column_name])
    calculated_data['all_bounce'] = round((calculated_data['visits'] * calculated_data['bounce']) / 100)
    calculated_data['all_no_bounce'] = calculated_data['visits'] - calculated_data['all_bounce']
    calculated_data['desktop_bounce'] = round(
        (calculated_data['desktop'] * calculated_data['desktop_bounce_rate']) / 100,
    )
    calculated_data['mobile_bounce'] = round(
        (calculated_data['mobile'] * calculated_data['mobile_bounce_rate']) / 100,
    )
    return calculated_data


def parse_domain_metrics(
    downloads_path: Path,
    domain: str,
    first_month: str,
    last_month: str,
    year: str,
) -> pd.DataFrame:
    """Parse domain metric reports.
    Args:
        downloads_path (Path): Downloads directory.
        domain (str): Domain name.
        first_month (str): First month.
        last_month (str): Last month.
        year (str): Year value."""
    domain_data = pd.DataFrame()
    for output_name, metric_name in METRIC_FILES.items():
        file_path = file_parser.metric_file(downloads_path, domain, metric_name, first_month, last_month, year)
        if not file_path.exists():
            continue
        metric_data = file_parser.read_csv(file_path)
        metric_data = metric_data.rename(columns={'Unnamed: 0': 'month'})
        metric_data = standardize_columns(metric_data)
        metric_data = metric_data.rename(columns=METRIC_COLUMNS[output_name])
        keep_columns = ['month', *METRIC_COLUMNS[output_name].values()]
        metric_data = metric_data[[column_name for column_name in keep_columns if column_name in metric_data.columns]]
        if domain_data.empty:
            domain_data = metric_data
        else:
            domain_data = pd.merge(domain_data, metric_data, on='month', how='outer')
    if domain_data.empty:
        return domain_data
    domain_data['domain'] = domain
    domain_data = domain_data.fillna(0)
    domain_data = calculate_metrics(domain_data)
    return domain_data


def merge_domains(data: pd.DataFrame, domains: pd.DataFrame) -> pd.DataFrame:
    """Merge domains data.
    Args:
        data (pd.DataFrame): Report data.
        domains (pd.DataFrame): Domains data."""
    if 'domain' not in data.columns:
        return data
    merged_data = pd.merge(data, domains, on='domain', how='left')
    return merged_data


def normalize_months(data: pd.DataFrame, report_year: int | None = None) -> pd.DataFrame:
    """Normalize month fields.
    Args:
        data (pd.DataFrame): Report data.
        report_year (int | None): Report year."""
    if 'month' not in data.columns:
        return data
    normalized_data = data.copy()
    parsed_months = pd.to_datetime(normalized_data['month'], errors='coerce')
    normalized_data['month_number'] = parsed_months.dt.month.astype('Int64').astype('string')
    missing_months = normalized_data['month_number'].isna()
    normalized_data.loc[missing_months, 'month_number'] = normalized_data.loc[
        missing_months,
        'month',
    ].astype(str).str[:3].apply(month_utils.month_number).astype('string')
    if report_year is None:
        normalized_data['year'] = parsed_months.dt.year.astype('Int64').astype('string')
    else:
        normalized_data['year'] = str(report_year)
    normalized_data['month'] = normalized_data['month_number'].apply(month_utils.month_abbr)
    normalized_data['month_year'] = (
        pd.to_datetime(normalized_data['month_number'] + ' ' + normalized_data['year'])
    ).dt.strftime('%d.%m.%Y')
    return normalized_data


def parse_overview(downloads_path: Path, domains: pd.DataFrame) -> pd.DataFrame:
    """Parse overview reports.
    Args:
        downloads_path (Path): Downloads directory.
        domains (pd.DataFrame): Domains data."""
    overview_temp = []
    for file_path in file_parser.overview_files(downloads_path):
        data = file_parser.read_csv(file_path, separator=';')
        data.columns = data.columns.str.lower()
        overview_temp.append(data)
    if len(overview_temp) == 0:
        return pd.DataFrame()
    overview_data = pd.concat(overview_temp, axis=0, ignore_index=True)
    overview_data = merge_domains(overview_data, domains)
    return overview_data


def parse_backlinks(downloads_path: Path, domain_list: list[str], report_name: str) -> pd.DataFrame:
    """Parse backlinks reports.
    Args:
        downloads_path (Path): Downloads directory.
        domain_list (list[str]): Domain names.
        report_name (str): Backlinks report name."""
    backlinks_temp = []
    for domain in domain_list:
        file_path = file_parser.backlinks_file(downloads_path, domain, report_name)
        data = file_parser.read_csv(file_path, separator=';')
        data.columns = data.columns.str.lower()
        data['domain'] = domain
        backlinks_temp.append(data)
    if len(backlinks_temp) == 0:
        return pd.DataFrame()
    backlinks_data = pd.concat(backlinks_temp, axis=0, ignore_index=True)
    return backlinks_data


def parse_metrics(
    downloads_path: Path,
    domain_list: list[str],
    domains: pd.DataFrame,
    month_amount: int,
    report_year: int,
) -> pd.DataFrame:
    """Parse metric reports.
    Args:
        downloads_path (Path): Downloads directory.
        domain_list (list[str]): Domain names.
        domains (pd.DataFrame): Domains data.
        month_amount (int): Count of months.
        report_year (int): Report year."""
    first_month, last_month, year = month_utils.metric_period(month_amount, report_year=report_year)
    metric_temp = []
    for domain in domain_list:
        domain_metrics = parse_domain_metrics(downloads_path, domain, first_month, last_month, year)
        if not domain_metrics.empty:
            metric_temp.append(domain_metrics)
    if len(metric_temp) == 0:
        return pd.DataFrame()
    metric_data = pd.concat(metric_temp, axis=0, ignore_index=True)
    metric_data = merge_domains(metric_data, domains)
    metric_data = normalize_months(metric_data, report_year)
    return metric_data


def parse_sources(
    downloads_path: Path,
    domain_list: list[str],
    domains: pd.DataFrame,
    month_amount: int,
    report_year: int,
) -> pd.DataFrame:
    """Parse traffic sources reports.
    Args:
        downloads_path (Path): Downloads directory.
        domain_list (list[str]): Domain names.
        domains (pd.DataFrame): Domains data.
        month_amount (int): Count of months.
        report_year (int): Report year."""
    first_month, last_month, year = month_utils.metric_period(month_amount, report_year=report_year)
    sources_temp = []
    for domain in domain_list:
        file_path = file_parser.sources_file(downloads_path, domain, first_month, last_month, year)
        if not file_path.exists():
            continue
        data = file_parser.read_csv(file_path)
        data = data.rename(columns={'Unnamed: 0': 'month'})
        data.columns = data.columns.str.lower()
        data['domain'] = domain
        sources_temp.append(data)
    if len(sources_temp) == 0:
        return pd.DataFrame()
    sources_data = pd.concat(sources_temp, axis=0, ignore_index=True)
    sources_data = sources_data.fillna(0)
    sources_data = merge_domains(sources_data, domains)
    sources_data = normalize_months(sources_data, report_year)
    return sources_data


def parse_journey(
    downloads_path: Path,
    progress: ProgressState,
    domains: pd.DataFrame,
    report_year: int,
) -> pd.DataFrame:
    """Parse journey reports.
    Args:
        downloads_path (Path): Downloads directory.
        progress (ProgressState): Progress state.
        domains (pd.DataFrame): Domains data.
        report_year (int): Report year."""
    journey_temp = []
    year = str(report_year)
    for month_name, domain_list in progress.monthly_exports.get('journey_sources', {}).items():
        for domain in domain_list:
            file_path = file_parser.journey_file(downloads_path, domain, month_name, year)
            if not file_path.exists():
                continue
            data = file_parser.read_csv(file_path)
            data.columns = data.columns.str.lower()
            data['domain'] = domain
            data['month'] = month_name
            data['year'] = year
            journey_temp.append(data)
    if len(journey_temp) == 0:
        return pd.DataFrame()
    journey_data = pd.concat(journey_temp, axis=0, ignore_index=True).fillna(0)
    journey_data = merge_domains(journey_data, domains)
    journey_data['month_number'] = journey_data['month'].apply(month_utils.month_number).astype('string')
    journey_data['month_year'] = journey_data.apply(
        lambda row: month_utils.add_month_year(row['month'], str(row['year'])),
        axis=1,
    )
    return journey_data


def parse_countries(
    downloads_path: Path,
    countries_path: Path,
    progress: ProgressState,
    domains: pd.DataFrame,
    report_year: int,
) -> tuple[pd.DataFrame, dict[str, pd.Series]]:
    """Parse traffic countries reports.
    Args:
        downloads_path (Path): Downloads directory.
        countries_path (Path): Countries CSV path.
        progress (ProgressState): Progress state.
        domains (pd.DataFrame): Domains data.
        report_year (int): Report year."""
    traffic_temp = []
    year = str(report_year)
    for month_name, domain_list in progress.monthly_exports.get('traffic_by_countries', {}).items():
        for index, domain in enumerate(domain_list):
            file_path = file_parser.traffic_file(downloads_path, month_name, year, index)
            if not file_path.exists():
                continue
            data = pd.read_csv(file_path, sep='","|""|,|"', engine='python')
            data = data[data.columns.drop(list(data.filter(regex='Unnamed')))]
            data.columns = data.columns.str.lower()
            data['domain'] = domain
            data['month'] = month_name
            data['year'] = year
            traffic_temp.append(data)
    if len(traffic_temp) == 0:
        return pd.DataFrame(), {}
    traffic_data = pd.concat(traffic_temp, axis=0, ignore_index=True)
    countries = country_mapper.read_countries(countries_path)
    traffic_data = country_mapper.merge_countries(traffic_data, countries)
    traffic_data = transform_countries(traffic_data)
    traffic_data = merge_domains(traffic_data, domains)
    country_data = country_mapper.country_lists(traffic_data)
    return traffic_data, country_data


def transform_countries(traffic_data: pd.DataFrame) -> pd.DataFrame:
    """Transform countries report.
    Args:
        traffic_data (pd.DataFrame): Traffic countries data."""
    transformed_data = traffic_data.copy()
    transformed_data['bounce rate'] = transformed_data['bounce rate'].str.rstrip('%').astype(float)
    transformed_data['traffic_no_bounce'] = round(
        transformed_data['traffic'] - ((transformed_data['traffic'] * transformed_data['bounce rate']) / 100),
    )
    transformed_data['traffic_bounce'] = round((transformed_data['traffic'] * transformed_data['bounce rate']) / 100)
    transformed_data['desktop share'] = transformed_data['desktop share'].apply(
        lambda value: '0%' if str(value) == '<\xa00.01%' else value,
    )
    transformed_data['mobile share'] = transformed_data['mobile share'].apply(
        lambda value: '0%' if str(value) == '<\xa00.01%' else value,
    )
    transformed_data['desktop share'] = transformed_data['desktop share'].str.rstrip('%').astype(float)
    transformed_data['mobile share'] = transformed_data['mobile share'].str.rstrip('%').astype(float)
    transformed_data['desktop'] = round(
        (transformed_data['unique visitors'] * transformed_data['desktop share']) / 100,
    )
    transformed_data['mobile'] = round(
        (transformed_data['unique visitors'] * transformed_data['mobile share']) / 100,
    )
    transformed_data['month_number'] = transformed_data['month'].apply(month_utils.month_number).astype('string')
    transformed_data['month_year'] = transformed_data.apply(
        lambda row: month_utils.add_month_year(row['month'], str(row['year'])),
        axis=1,
    )
    return transformed_data
