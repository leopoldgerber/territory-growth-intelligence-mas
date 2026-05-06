from dataclasses import dataclass


@dataclass(frozen=True)
class LocatorSet:
    email_input: str
    password_input: str
    first_search_input: str
    search_input: str
    search_clear_button: str
    traffic_analytics_link: str
    journey_tab: str
    geo_tab: str
    month_picker: str
    month_apply: str
    traffic_chart_export: str
    traffic_csv_option: str
    traffic_sources_export: str
    journey_csv_button: str
    geo_csv_button: str


def semrush_locators() -> LocatorSet:
    """Build Semrush locators.
    Args:
        None (None): No arguments are required."""
    locators = LocatorSet(
        email_input='#email',
        password_input='#password',
        first_search_input='xpath=//*[@class="___SValue_12tss-red-team _size_l_12tss-red-team"]',
        search_input='xpath=//*[@class="srf-searchbar__form__input js-searchbar-input"]',
        search_clear_button='xpath=//*[@class="srf-icon"]',
        traffic_analytics_link='xpath=//a[contains(@data-test,"seo_traffic_analytics")]',
        journey_tab='xpath=//button[contains(@data-test,"reportTab journey")]',
        geo_tab='xpath=//button[contains(@data-test,"reportTab geo")]',
        month_picker='xpath=//a[@data-ui-name="MonthRangePicker.Trigger"]',
        month_apply='xpath=//div[@data-ui-name="Dropdown.Popper"]//button[@data-test="selector-apply"]',
        traffic_chart_export='xpath=//*[@id="chartOverviewVisitsHistory"]//button',
        traffic_csv_option='xpath=//div[contains(@class,"SDropdownMenuItem")][2]',
        traffic_sources_export='xpath=//button[contains(@class, "SButton")]',
        journey_csv_button='xpath=//button[contains(@data-test, "csv-button")]',
        geo_csv_button='xpath=//div[contains(@data-test,"geoDistributionList")]//button',
    )
    return locators


def metric_button(metric_name: str) -> str:
    """Build metric button locator.
    Args:
        metric_name (str): Metric name."""
    values = {
        'visits': 'visits',
        'unique_users': 'users',
        'duration': 'time_on_site',
        'bounce_rate': 'bounce_rate',
    }
    value = values[metric_name]
    selector = f'xpath=//*[@id="chartOverviewVisitsHistory"]//button[@value="{value}"]'
    return selector


def month_button(month_name: str, year: int) -> str:
    """Build month button locator.
    Args:
        month_name (str): Month name.
        year (int): Report year."""
    selector = f'xpath=//button[@aria-label="{month_name} 1, {year}"]'
    return selector
