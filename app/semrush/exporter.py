import time
from typing import Any

from app.semrush import navigation, selectors
from app.utils.progress_tracker import ProgressState, add_export, add_month_export
from app.utils.retry import retry_action
from app.utils.scroll_utils import scroll_down, scroll_top


TRAFFIC_METRICS = {
    'visits': selectors.VISITS_BUTTON,
    'unique_users': selectors.USERS_BUTTON,
    'duration': selectors.DURATION_BUTTON,
    'bounce_rate': selectors.BOUNCE_BUTTON,
}


def click_export(driver: Any, button_selector: str, csv_selector: str) -> Any:
    """Click export controls.
    Args:
        driver (Any): Selenium driver.
        button_selector (str): Export button selector.
        csv_selector (str): CSV option selector."""
    navigation.click_xpath(driver, button_selector)
    time.sleep(2)
    navigation.click_xpath(driver, csv_selector)
    time.sleep(2)
    return driver


def export_metric(driver: Any, metric_name: str, attempts: int, pause: float) -> Any:
    """Export traffic metric.
    Args:
        driver (Any): Selenium driver.
        metric_name (str): Metric name.
        attempts (int): Retry attempts.
        pause (float): Retry pause."""
    def export_action() -> Any:
        navigation.click_xpath(driver, TRAFFIC_METRICS[metric_name])
        time.sleep(2)
        return click_export(driver, selectors.TRAFFIC_CHART_EXPORT, selectors.TRAFFIC_CSV_OPTION)

    return retry_action(export_action, attempts, pause, f'{metric_name} export failed')


def export_sources(driver: Any, attempts: int, pause: float) -> Any:
    """Export traffic sources.
    Args:
        driver (Any): Selenium driver.
        attempts (int): Retry attempts.
        pause (float): Retry pause."""
    return retry_action(
        lambda: click_export(driver, selectors.TRAFFIC_SOURCES_EXPORT, selectors.TRAFFIC_CSV_OPTION),
        attempts,
        pause,
        'Traffic sources export failed',
    )


def export_journey(driver: Any, attempts: int, pause: float) -> Any:
    """Export journey sources.
    Args:
        driver (Any): Selenium driver.
        attempts (int): Retry attempts.
        pause (float): Retry pause."""
    return retry_action(
        lambda: navigation.click_xpath(driver, selectors.JOURNEY_CSV_BUTTON),
        attempts,
        pause,
        'Journey sources export failed',
    )


def export_geo(driver: Any, attempts: int, pause: float) -> Any:
    """Export geo distribution.
    Args:
        driver (Any): Selenium driver.
        attempts (int): Retry attempts.
        pause (float): Retry pause."""
    return retry_action(
        lambda: navigation.click_xpath(driver, selectors.GEO_CSV_BUTTON),
        attempts,
        pause,
        'Geo distribution export failed',
    )


def export_domain_reports(
    driver: Any,
    domain: str,
    month_list: list[str],
    year: int,
    attempts: int,
    pause: float,
    progress: ProgressState,
) -> ProgressState:
    """Export reports for domain.
    Args:
        driver (Any): Selenium driver.
        domain (str): Domain name.
        month_list (list[str]): Month names.
        year (int): Calendar year.
        attempts (int): Retry attempts.
        pause (float): Retry pause.
        progress (ProgressState): Progress state."""
    navigation.open_traffic(driver, attempts, pause)
    scroll_top(driver)
    for metric_name in TRAFFIC_METRICS:
        export_metric(driver, metric_name, attempts, pause)
        progress = add_export(progress, metric_name, domain)
    scroll_down(driver, 900)
    export_sources(driver, attempts, pause)
    progress = add_export(progress, 'traffic_sources', domain)
    scroll_top(driver)
    navigation.open_journey(driver, attempts, pause)
    scroll_down(driver, 1200)
    for month_name in month_list:
        navigation.choose_month(driver, month_name, year)
        export_journey(driver, attempts, pause)
        progress = add_month_export(progress, 'journey_sources', month_name, domain)
    scroll_top(driver)
    navigation.open_geo(driver, attempts, pause)
    scroll_down(driver, 1200)
    for month_name in month_list:
        navigation.choose_month(driver, month_name, year)
        export_geo(driver, attempts, pause)
        progress = add_month_export(progress, 'traffic_by_countries', month_name, domain)
    return progress
