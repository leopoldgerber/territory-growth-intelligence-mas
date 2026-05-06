import random
import time
from typing import Any

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from app.semrush import selectors
from app.utils.retry import retry_action


def submit_domain(driver: Any, selector: str, domain: str, timeout: int) -> Any:
    """Submit domain search.
    Args:
        driver (Any): Selenium driver.
        selector (str): Search input selector.
        domain (str): Domain name.
        timeout (int): Wait timeout."""
    search = driver.find_element(By.XPATH, selector)
    search.send_keys(domain)
    WebDriverWait(driver, timeout).until(lambda browser: search.get_attribute('value') == domain)
    search.submit()
    return driver


def first_search(driver: Any, domain: str) -> Any:
    """Run first search.
    Args:
        driver (Any): Selenium driver.
        domain (str): Domain name."""
    time.sleep(random.randrange(4, 8, 1))
    submit_domain(driver, selectors.FIRST_SEARCH_INPUT, domain, random.randrange(4, 8, 1))
    time.sleep(random.randrange(10, 15, 1))
    return driver


def domain_search(driver: Any, domain: str, attempts: int, pause: float) -> Any:
    """Run domain search.
    Args:
        driver (Any): Selenium driver.
        domain (str): Domain name.
        attempts (int): Retry attempts.
        pause (float): Retry pause."""
    def search_existing() -> Any:
        cross = driver.find_element(By.XPATH, selectors.SEARCH_CLEAR_BUTTON)
        cross.click()
        time.sleep(random.randrange(2, 5, 1))
        return submit_domain(driver, selectors.SEARCH_INPUT, domain, random.randrange(2, 5, 1))

    def search_fallback() -> Any:
        return submit_domain(driver, selectors.FIRST_SEARCH_INPUT, domain, random.randrange(4, 8, 1))

    def search_action() -> Any:
        try:
            return search_existing()
        except Exception:
            return search_fallback()

    driver = retry_action(search_action, attempts, pause, 'Domain search failed')
    time.sleep(random.randrange(10, 15, 1))
    return driver
