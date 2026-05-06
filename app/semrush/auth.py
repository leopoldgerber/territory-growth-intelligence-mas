import random
import time
from typing import Any

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from app.semrush import selectors
from app.utils.retry import retry_action


def fill_field(driver: Any, field_id: str, value: str, timeout: int) -> Any:
    """Fill input field.
    Args:
        driver (Any): Selenium driver.
        field_id (str): Input field ID.
        value (str): Input value.
        timeout (int): Wait timeout."""
    field = WebDriverWait(driver, timeout).until(
        expected_conditions.presence_of_element_located((By.ID, field_id)),
    )
    field.send_keys(value)
    WebDriverWait(driver, timeout).until(lambda browser: field.get_attribute('value') == value)
    return field


def login_semrush(driver: Any, email: str, password: str, attempts: int, pause: float) -> Any:
    """Login to Semrush.
    Args:
        driver (Any): Selenium driver.
        email (str): Semrush email.
        password (str): Semrush password.
        attempts (int): Retry attempts.
        pause (float): Retry pause."""
    if email == '' or password == '':
        raise ValueError('Semrush credentials are not configured')

    def submit_login() -> Any:
        time.sleep(random.randrange(2, 5, 1))
        email_field = fill_field(driver, selectors.EMAIL_INPUT, email, random.randrange(2, 5, 1))
        time.sleep(random.randrange(2, 5, 1))
        fill_field(driver, selectors.PASSWORD_INPUT, password, random.randrange(2, 5, 1))
        time.sleep(random.randrange(10, 16, 2))
        email_field.submit()
        return driver

    return retry_action(submit_login, attempts, pause, 'Semrush login failed')
