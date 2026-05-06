import time
from typing import Any

from selenium.webdriver.common.by import By

from app.semrush import selectors
from app.utils.retry import retry_action


def click_xpath(driver: Any, selector: str) -> Any:
    """Click XPath element.
    Args:
        driver (Any): Selenium driver.
        selector (str): XPath selector."""
    driver.find_element(By.XPATH, selector).click()
    return driver


def open_overview(driver: Any, attempts: int, pause: float) -> Any:
    """Open Domain Overview.
    Args:
        driver (Any): Selenium driver.
        attempts (int): Retry attempts.
        pause (float): Retry pause."""
    return retry_action(
        lambda: click_xpath(driver, selectors.DOMAIN_OVERVIEW_LINK),
        attempts,
        pause,
        'Domain Overview navigation failed',
    )


def open_traffic(driver: Any, attempts: int, pause: float) -> Any:
    """Open Traffic Analytics.
    Args:
        driver (Any): Selenium driver.
        attempts (int): Retry attempts.
        pause (float): Retry pause."""
    return retry_action(
        lambda: click_xpath(driver, selectors.TRAFFIC_ANALYTICS_LINK),
        attempts,
        pause,
        'Traffic Analytics navigation failed',
    )


def open_journey(driver: Any, attempts: int, pause: float) -> Any:
    """Open Journey tab.
    Args:
        driver (Any): Selenium driver.
        attempts (int): Retry attempts.
        pause (float): Retry pause."""
    return retry_action(
        lambda: click_xpath(driver, selectors.JOURNEY_TAB),
        attempts,
        pause,
        'Journey tab navigation failed',
    )


def open_geo(driver: Any, attempts: int, pause: float) -> Any:
    """Open Geo Distribution tab.
    Args:
        driver (Any): Selenium driver.
        attempts (int): Retry attempts.
        pause (float): Retry pause."""
    return retry_action(
        lambda: click_xpath(driver, selectors.GEO_TAB),
        attempts,
        pause,
        'Geo Distribution tab navigation failed',
    )


def choose_month(driver: Any, month_name: str, year: int) -> Any:
    """Choose report month.
    Args:
        driver (Any): Selenium driver.
        month_name (str): Month name.
        year (int): Calendar year."""
    click_xpath(driver, selectors.MONTH_PICKER)
    time.sleep(1)
    click_xpath(driver, selectors.month_button(month_name, year))
    time.sleep(1)
    click_xpath(driver, selectors.MONTH_APPLY)
    return driver
