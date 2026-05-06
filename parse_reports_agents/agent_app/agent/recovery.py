from dataclasses import dataclass


@dataclass(frozen=True)
class RecoveryPlan:
    error_type: str
    action_name: str
    max_attempts: int


def recovery_plan(error_message: str) -> RecoveryPlan:
    """Build recovery plan.
    Args:
        error_message (str): Error message."""
    message = error_message.lower()
    if 'download' in message:
        return RecoveryPlan('download_timeout', 'scroll_and_retry', 2)
    if 'selector' in message or 'locator' in message:
        return RecoveryPlan('element_not_found', 'refresh_and_retry', 2)
    if 'login' in message:
        return RecoveryPlan('logged_out', 'login_again', 1)
    return RecoveryPlan('unknown_error', 'stop_with_status', 1)


def record_recovery(records: list[dict[str, str]], plan: RecoveryPlan) -> list[dict[str, str]]:
    """Record recovery action.
    Args:
        records (list[dict[str, str]]): Recovery records.
        plan (RecoveryPlan): Recovery plan."""
    records.append(
        {
            'error_type': plan.error_type,
            'action_name': plan.action_name,
            'max_attempts': str(plan.max_attempts),
        },
    )
    return records
