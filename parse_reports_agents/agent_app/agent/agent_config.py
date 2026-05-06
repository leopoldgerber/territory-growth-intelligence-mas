import os
from dataclasses import dataclass
from importlib import import_module
from pathlib import Path

from agent_app.shared.module_adapter import include_modules


@dataclass(frozen=True)
class BrowserSettings:
    headless: bool
    window_size: tuple[int, int]
    timeout: int
    downloads_path: Path
    artifacts_path: Path
    storage_state_path: Path
    use_storage_state: bool
    save_screenshots: bool
    strict_downloads: bool


@dataclass(frozen=True)
class AgentSettings:
    app_settings: object
    browser_settings: BrowserSettings
    engine: str
    mode: str
    dry_run: bool
    resume: bool
    stop_after_first: bool


def load_env_file() -> bool:
    """Load local environment file.
    Args:
        None (None): No arguments are required."""
    try:
        dotenv_module = import_module('dotenv')
    except ImportError:
        return False
    dotenv_module.load_dotenv()
    return True


def read_bool(name: str, default: bool) -> bool:
    """Read boolean environment value.
    Args:
        name (str): Environment variable name.
        default (bool): Default value."""
    value = os.getenv(name)
    if value is None or value.strip() == '':
        return default
    return value.strip().lower() in ['1', 'true', 'yes', 'y']


def read_integer(name: str, default: int) -> int:
    """Read integer environment value.
    Args:
        name (str): Environment variable name.
        default (int): Default value."""
    value = os.getenv(name)
    if value is None or value.strip() == '':
        return default
    return int(value)


def read_path(name: str, default: Path) -> Path:
    """Read path environment value.
    Args:
        name (str): Environment variable name.
        default (Path): Default path."""
    value = os.getenv(name)
    if value is None or value.strip() == '':
        return default
    return Path(value)


def load_browser() -> BrowserSettings:
    """Load browser settings.
    Args:
        None (None): No arguments are required."""
    load_env_file()
    include_modules()
    from app.config.settings import load_settings

    app_settings = load_settings()
    artifacts_path = read_path('ARTIFACTS_PATH', Path.cwd() / 'artifacts')
    width = read_integer('BROWSER_WIDTH', 1600)
    height = read_integer('BROWSER_HEIGHT', 1600)
    browser_settings = BrowserSettings(
        headless=read_bool('BROWSER_HEADLESS', False),
        window_size=(width, height),
        timeout=read_integer('BROWSER_TIMEOUT', 30000),
        downloads_path=app_settings.downloads_path,
        artifacts_path=artifacts_path,
        storage_state_path=read_path('STORAGE_STATE_PATH', artifacts_path / 'storage_state.json'),
        use_storage_state=False,
        save_screenshots=read_bool('SAVE_SCREENSHOTS', True),
        strict_downloads=read_bool('STRICT_DOWNLOADS', False),
    )
    return browser_settings


def build_settings(
    engine: str,
    mode: str,
    dry_run: bool,
    resume: bool,
    use_storage_state: bool,
    stop_after_first: bool,
) -> AgentSettings:
    """Build agent settings.
    Args:
        engine (str): Pipeline engine.
        mode (str): Pipeline mode.
        dry_run (bool): Dry run flag.
        resume (bool): Resume flag.
        use_storage_state (bool): Storage state flag.
        stop_after_first (bool): Stop after first flag."""
    include_modules()
    from app.config.settings import load_settings

    app_settings = load_settings()
    browser_settings = load_browser()
    browser_settings = BrowserSettings(
        headless=browser_settings.headless,
        window_size=browser_settings.window_size,
        timeout=browser_settings.timeout,
        downloads_path=browser_settings.downloads_path,
        artifacts_path=browser_settings.artifacts_path,
        storage_state_path=browser_settings.storage_state_path,
        use_storage_state=use_storage_state,
        save_screenshots=browser_settings.save_screenshots,
        strict_downloads=browser_settings.strict_downloads,
    )
    agent_settings = AgentSettings(
        app_settings=app_settings,
        browser_settings=browser_settings,
        engine=engine,
        mode=mode,
        dry_run=dry_run,
        resume=resume,
        stop_after_first=stop_after_first,
    )
    return agent_settings
