from pathlib import Path
from typing import Any

from agent_app.agent.action_result import ActionResult, failure_result, success_result


def goto_page(page: Any, url: str, timeout: int) -> ActionResult:
    """Open browser page.
    Args:
        page (Any): Playwright page.
        url (str): Target URL.
        timeout (int): Timeout milliseconds."""
    try:
        page.goto(url, timeout=timeout)
        page.wait_for_load_state('domcontentloaded', timeout=timeout)
    except Exception as error:
        return failure_result('Open URL failed', str(error), {'url': url})
    return success_result('URL opened', {'url': url})


def fill_input(page: Any, selector: str, value: str, timeout: int) -> ActionResult:
    """Fill page input.
    Args:
        page (Any): Playwright page.
        selector (str): Element selector.
        value (str): Input value.
        timeout (int): Timeout milliseconds."""
    try:
        page.locator(selector).fill(value, timeout=timeout)
    except Exception as error:
        return failure_result('Fill input failed', str(error), {'selector': selector})
    return success_result('Input filled', {'selector': selector})


def click_element(page: Any, selector: str, timeout: int, force: bool = False) -> ActionResult:
    """Click page element.
    Args:
        page (Any): Playwright page.
        selector (str): Element selector.
        timeout (int): Timeout milliseconds.
        force (bool): Force click flag."""
    try:
        page.locator(selector).click(timeout=timeout, force=force)
    except Exception as error:
        try:
            page.locator(selector).scroll_into_view_if_needed(timeout=timeout)
            page.locator(selector).click(timeout=timeout, force=True)
        except Exception:
            return failure_result('Click failed', str(error), {'selector': selector})
    return success_result('Element clicked', {'selector': selector})


def press_key(page: Any, selector: str, key: str, timeout: int) -> ActionResult:
    """Press element key.
    Args:
        page (Any): Playwright page.
        selector (str): Element selector.
        key (str): Keyboard key.
        timeout (int): Timeout milliseconds."""
    try:
        page.locator(selector).press(key, timeout=timeout)
    except Exception as error:
        return failure_result('Press key failed', str(error), {'selector': selector, 'key': key})
    return success_result('Key pressed', {'selector': selector, 'key': key})


def wait_selector(page: Any, selector: str, timeout: int) -> ActionResult:
    """Wait for selector.
    Args:
        page (Any): Playwright page.
        selector (str): Element selector.
        timeout (int): Timeout milliseconds."""
    try:
        page.wait_for_selector(selector, timeout=timeout)
    except Exception as error:
        return failure_result('Selector wait failed', str(error), {'selector': selector})
    return success_result('Selector found', {'selector': selector})


def scroll_page(page: Any, y_value: int) -> ActionResult:
    """Scroll page.
    Args:
        page (Any): Playwright page.
        y_value (int): Vertical scroll value."""
    try:
        page.evaluate(f'window.scrollTo(0, {y_value})')
    except Exception as error:
        return failure_result('Scroll failed', str(error), {'y': y_value})
    return success_result('Page scrolled', {'y': y_value})


def save_screenshot(page: Any, screenshot_path: Path) -> ActionResult:
    """Save page screenshot.
    Args:
        page (Any): Playwright page.
        screenshot_path (Path): Screenshot path."""
    try:
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(screenshot_path), full_page=True)
    except Exception as error:
        return failure_result('Screenshot failed', str(error), {'path': str(screenshot_path)})
    return success_result('Screenshot saved', {'path': str(screenshot_path)})


def download_file(page: Any, selector: str, output_path: Path, timeout: int) -> ActionResult:
    """Download file.
    Args:
        page (Any): Playwright page.
        selector (str): Element selector.
        output_path (Path): Output file path.
        timeout (int): Timeout milliseconds."""
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with page.expect_download(timeout=timeout) as download_info:
            page.locator(selector).click(timeout=timeout)
        download = download_info.value
        download.save_as(str(output_path))
    except Exception as error:
        return failure_result('Download failed', str(error), {'selector': selector, 'path': str(output_path)})
    return success_result('File downloaded', {'path': str(output_path)})
