from pathlib import Path
from typing import Any

from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def build_options() -> Any:
    """Build Chrome options.
    Args:
        None (None): No arguments are required."""
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    return options


def create_driver(chromedriver_path: Path, window_size: tuple[int, int]) -> Any:
    """Create Chrome driver.
    Args:
        chromedriver_path (Path): Path to ChromeDriver.
        window_size (tuple[int, int]): Browser window size."""
    options = build_options()
    service = Service(executable_path=str(chromedriver_path))
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_window_size(window_size[0], window_size[1])
    return driver
