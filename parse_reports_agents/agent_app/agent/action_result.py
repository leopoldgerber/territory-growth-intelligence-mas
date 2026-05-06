from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ActionResult:
    success: bool
    message: str
    evidence: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    screenshot_path: Path | None = None


def success_result(message: str, evidence: dict[str, Any] | None = None) -> ActionResult:
    """Build success action result.
    Args:
        message (str): Result message.
        evidence (dict[str, Any] | None): Result evidence."""
    result = ActionResult(success=True, message=message, evidence=evidence or {})
    return result


def failure_result(
    message: str,
    error: str,
    evidence: dict[str, Any] | None = None,
    screenshot_path: Path | None = None,
) -> ActionResult:
    """Build failure action result.
    Args:
        message (str): Result message.
        error (str): Error message.
        evidence (dict[str, Any] | None): Result evidence.
        screenshot_path (Path | None): Screenshot path."""
    result = ActionResult(
        success=False,
        message=message,
        evidence=evidence or {},
        error=error,
        screenshot_path=screenshot_path,
    )
    return result
