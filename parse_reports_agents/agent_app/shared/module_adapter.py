import sys
from pathlib import Path


def modules_path() -> Path:
    """Build modules project path.
    Args:
        None (None): No arguments are required."""
    current_path = Path(__file__).resolve()
    root_path = current_path.parents[3]
    module_path = root_path / 'parse_reports_modules'
    return module_path


def include_modules() -> Path:
    """Include shared modules path.
    Args:
        None (None): No arguments are required."""
    module_path = modules_path()
    module_value = str(module_path)
    if module_value not in sys.path:
        sys.path.insert(0, module_value)
    return module_path


include_modules()
