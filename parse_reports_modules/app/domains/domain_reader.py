from pathlib import Path

import pandas as pd


def clean_domain(domain: str) -> str:
    """Clean domain value.
    Args:
        domain (str): Raw domain value."""
    clean_value = str(domain).strip()
    clean_value = clean_value.replace('https://www.', '')
    clean_value = clean_value.replace('http://www.', '')
    clean_value = clean_value.replace('https://', '')
    clean_value = clean_value.replace('http://', '')
    clean_value = clean_value.replace('/', '')
    return clean_value


def read_domains(domains_path: Path, start_index: int, end_index: int) -> pd.DataFrame:
    """Read domains from CSV.
    Args:
        domains_path (Path): Path to domains CSV file.
        start_index (int): First row index.
        end_index (int): Last row index."""
    domains = pd.read_csv(domains_path, sep=';')
    domains['domain'] = domains['domain'].apply(clean_domain)
    domains = domains.drop_duplicates(subset=['domain']).reset_index(drop=True)
    return domains.iloc[start_index:end_index].reset_index(drop=True)


def select_domains(domains: pd.DataFrame) -> list[str]:
    """Select domain names.
    Args:
        domains (pd.DataFrame): DataFrame with domain column."""
    return domains['domain'].dropna().astype(str).tolist()


def select_company(domains: pd.DataFrame) -> pd.DataFrame:
    """Select company values.
    Args:
        domains (pd.DataFrame): DataFrame with company column."""
    if 'company' not in domains.columns:
        return pd.DataFrame({'company': []})
    company = domains[['company']].drop_duplicates().reset_index(drop=True)
    return company
