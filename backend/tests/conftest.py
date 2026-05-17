from collections.abc import Generator
from pathlib import Path
import sys

import pytest


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


@pytest.fixture
def root_dir() -> Generator[Path, None, None]:
    """Provide root dir.
    Args:
        None (None): No arguments are required."""
    yield ROOT_DIR
