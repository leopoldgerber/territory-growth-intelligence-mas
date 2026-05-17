from pathlib import Path


REPORT_TYPES = {
    'traffic_countries_daily.xlsx': 'traffic_countries_daily',
    'trend_by_devices_daily.xlsx': 'domain_device_daily',
    'traffic_sources_daily.xlsx': 'domain_channel_daily',
    'journey_sources_daily.xlsx': 'domain_journey_source_daily',
    'calendar_daily.xlsx': 'calendar_daily',
    'domains_list.xlsx': 'domains_list',
    'company_list.xlsx': 'company_list',
    'countries_en_list.xlsx': 'countries_en_list',
    'countries_ru_list.xlsx': 'countries_ru_list',
    'countries_location_ru_list.xlsx': 'countries_location_ru_list',
    'audience_demographics_daily.xlsx': 'audience_demographics_daily',
    'demographics_daily.xlsx': 'audience_demographics_daily',
    'organic_keywords_daily.xlsx': 'organic_keywords_daily',
    'paid_keywords_daily.xlsx': 'paid_keywords_daily',
    'ppc_keywords_daily.xlsx': 'paid_keywords_daily',
    'top_pages_daily.xlsx': 'top_pages_daily',
    'ads_creatives_daily.xlsx': 'ads_creatives_daily',
    'ad_creatives_daily.xlsx': 'ads_creatives_daily',
    'backlinks_daily.xlsx': 'backlinks_daily',
    'referring_domains_daily.xlsx': 'referring_domains_daily',
    'campaign_performance_daily.xlsx': 'campaign_performance_daily',
}

REQUIRED_COLUMNS = {
    'traffic_countries_daily': ['date', 'domain', 'company', 'country', 'traffic'],
    'domain_device_daily': ['date', 'domain', 'company', 'visits_devices', 'visits_desktop', 'visits_mobile'],
    'domain_channel_daily': ['date', 'domain', 'company', 'direct', 'referral', 'paid', 'social', 'search'],
    'domain_journey_source_daily': ['date', 'domain', 'company', 'source type', 'traffic type', 'traffic'],
    'audience_demographics_daily': ['date', 'domain', 'segment'],
    'organic_keywords_daily': ['date', 'domain', 'keyword'],
    'paid_keywords_daily': ['date', 'domain', 'keyword'],
    'top_pages_daily': ['date', 'domain', 'url'],
    'ads_creatives_daily': ['date', 'domain'],
    'backlinks_daily': ['date', 'domain', 'referring domain'],
    'referring_domains_daily': ['date', 'domain', 'referring domain'],
    'campaign_performance_daily': ['date'],
}


def normalize_columns(columns: list[str]) -> list[str]:
    """Normalize column names.
    Args:
        columns (list[str]): Source column names."""
    normalized_columns = [str(column).strip().lower() for column in columns]
    return normalized_columns


def detect_type(file_path: Path) -> str:
    """Detect report type.
    Args:
        file_path (Path): Excel file path."""
    file_name = file_path.name.lower()
    report_type = REPORT_TYPES.get(file_name)
    if report_type is None:
        matched_type = next(
            (known_type for known_name, known_type in REPORT_TYPES.items() if file_name.endswith(f'_{known_name}')),
            'unknown',
        )
        return matched_type
    return report_type


def validate_columns(report_type: str, columns: list[str]) -> list[str]:
    """Validate required columns.
    Args:
        report_type (str): Detected report type.
        columns (list[str]): Excel column names."""
    normalized_columns = normalize_columns(columns)
    required_columns = REQUIRED_COLUMNS.get(report_type, [])
    missing_columns = [column for column in required_columns if column not in normalized_columns]
    return missing_columns
