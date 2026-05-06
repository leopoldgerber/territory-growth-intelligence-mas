from dataclasses import dataclass
from typing import Any

from agent_app.agent.agent_config import BrowserSettings


@dataclass
class BrowserRuntime:
    playwright: Any
    browser: Any
    context: Any
    page: Any


def create_browser(settings: BrowserSettings) -> BrowserRuntime:
    """Create Playwright browser.
    Args:
        settings (BrowserSettings): Browser settings."""
    from playwright.sync_api import sync_playwright

    settings.downloads_path.mkdir(parents=True, exist_ok=True)
    settings.artifacts_path.mkdir(parents=True, exist_ok=True)
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(headless=settings.headless)
    context_params = {
        'accept_downloads': True,
        'viewport': {'width': settings.window_size[0], 'height': settings.window_size[1]},
    }
    if settings.use_storage_state and settings.storage_state_path.exists():
        context_params['storage_state'] = str(settings.storage_state_path)
    context = browser.new_context(**context_params)
    context.set_default_timeout(settings.timeout)
    page = context.new_page()
    runtime = BrowserRuntime(playwright=playwright, browser=browser, context=context, page=page)
    return runtime


def close_browser(runtime: BrowserRuntime, settings: BrowserSettings) -> bool:
    """Close Playwright browser.
    Args:
        runtime (BrowserRuntime): Browser runtime.
        settings (BrowserSettings): Browser settings."""
    if settings.use_storage_state:
        settings.storage_state_path.parent.mkdir(parents=True, exist_ok=True)
        runtime.context.storage_state(path=str(settings.storage_state_path))
    runtime.context.close()
    runtime.browser.close()
    runtime.playwright.stop()
    return True
