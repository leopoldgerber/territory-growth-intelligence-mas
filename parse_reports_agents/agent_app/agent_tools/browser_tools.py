from pathlib import Path
from typing import Any

from agent_app.agent.action_result import ActionResult
from agent_app.agent.agent_config import AgentSettings
from agent_app.playwright_runtime import actions


def open_url(page: Any, settings: AgentSettings) -> ActionResult:
    """Open configured URL.
    Args:
        page (Any): Playwright page.
        settings (AgentSettings): Agent settings."""
    result = actions.goto_page(page, settings.app_settings.semrush_url, settings.browser_settings.timeout)
    return result


def fill_field(page: Any, selector: str, value: str, settings: AgentSettings) -> ActionResult:
    """Fill browser field.
    Args:
        page (Any): Playwright page.
        selector (str): Element selector.
        value (str): Input value.
        settings (AgentSettings): Agent settings."""
    result = actions.fill_input(page, selector, value, settings.browser_settings.timeout)
    return result


def click_button(page: Any, selector: str, settings: AgentSettings) -> ActionResult:
    """Click browser button.
    Args:
        page (Any): Playwright page.
        selector (str): Element selector.
        settings (AgentSettings): Agent settings."""
    result = actions.click_element(page, selector, settings.browser_settings.timeout)
    return result


def scroll_window(page: Any, y_value: int) -> ActionResult:
    """Scroll browser window.
    Args:
        page (Any): Playwright page.
        y_value (int): Vertical scroll value."""
    result = actions.scroll_page(page, y_value)
    return result


def take_screenshot(page: Any, screenshot_path: Path) -> ActionResult:
    """Take browser screenshot.
    Args:
        page (Any): Playwright page.
        screenshot_path (Path): Screenshot path."""
    result = actions.save_screenshot(page, screenshot_path)
    return result
