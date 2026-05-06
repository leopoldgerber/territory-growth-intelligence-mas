import time
from collections.abc import Callable
from typing import TypeVar


ResultType = TypeVar('ResultType')


def retry_action(action: Callable[[], ResultType], attempts: int, pause: float, error_message: str) -> ResultType:
    """Run action with retries.
    Args:
        action (Callable[[], ResultType]): Callable action.
        attempts (int): Attempts count.
        pause (float): Pause between attempts.
        error_message (str): Error message."""
    last_error = None
    for _ in range(attempts):
        try:
            return action()
        except Exception as error:
            last_error = error
            time.sleep(pause)
    raise RuntimeError(error_message) from last_error
