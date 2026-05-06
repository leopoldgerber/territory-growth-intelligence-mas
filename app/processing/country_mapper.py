from pathlib import Path

import pandas as pd


def read_countries(countries_path: Path) -> pd.DataFrame:
    """Read countries dictionary.
    Args:
        countries_path (Path): Countries CSV path."""
    countries = pd.read_csv(
        countries_path,
        engine='python',
        encoding='cp1251',
        sep=';',
        quotechar='"',
        on_bad_lines='skip',
    )
    countries = countries.rename(columns={'short': 'country'})
    return countries


def merge_countries(traffic_data: pd.DataFrame, countries: pd.DataFrame) -> pd.DataFrame:
    """Merge countries data.
    Args:
        traffic_data (pd.DataFrame): Traffic by countries report.
        countries (pd.DataFrame): Countries dictionary."""
    merged_data = pd.merge(traffic_data, countries, on='country', how='left')
    return merged_data


def country_lists(traffic_data: pd.DataFrame) -> dict[str, pd.Series]:
    """Build country lists.
    Args:
        traffic_data (pd.DataFrame): Traffic by countries report."""
    return {
        'countries_ru_list': traffic_data['name'].drop_duplicates(),
        'countries_en_list': traffic_data['english'].drop_duplicates(),
        'countries_location_ru_list': traffic_data['location'].drop_duplicates(),
        'calendar': traffic_data['month_year'].drop_duplicates(),
    }
