import random
import time
from typing import Any


def scroll_down(driver: Any, max_height: int = 2000) -> Any:
    """Scroll page down.
    Args:
        driver (Any): Selenium driver.
        max_height (int): Maximum scroll height."""
    current_height = 0
    while current_height < max_height:
        next_height = random.randrange(current_height + 50, current_height + 400, 50)
        driver.execute_script(f'window.scrollTo({current_height},{next_height});')
        current_height = next_height
        time.sleep(random.randrange(1, 3, 1))
    return driver


def scroll_top(driver: Any) -> Any:
    """Scroll page to top.
    Args:
        driver (Any): Selenium driver."""
    driver.execute_script('window.scrollTo(0,0);')
    return driver
