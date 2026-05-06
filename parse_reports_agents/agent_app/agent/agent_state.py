import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from agent_app.shared.module_adapter import include_modules


@dataclass
class AgentState:
    mode: str
    domain_list: list[str]
    month_list: list[str]
    current_domain: str = ''
    current_section: str = ''
    current_month: str = ''
    attempts: dict[str, int] = field(default_factory=dict)
    downloaded_files: list[str] = field(default_factory=list)
    errors: dict[str, str] = field(default_factory=dict)
    completed_tasks: list[str] = field(default_factory=list)
    recovery_actions: list[dict[str, str]] = field(default_factory=list)
    progress: object | None = None


def create_state(mode: str, domain_list: list[str], month_list: list[str], report_names: list[str]) -> AgentState:
    """Create agent state.
    Args:
        mode (str): Run mode.
        domain_list (list[str]): Domain names.
        month_list (list[str]): Month names.
        report_names (list[str]): Report names."""
    include_modules()
    from app.utils.progress_tracker import create_progress

    progress = create_progress(report_names, month_list)
    state = AgentState(mode=mode, domain_list=domain_list, month_list=month_list, progress=progress)
    return state


def state_dict(state: AgentState) -> dict[str, Any]:
    """Convert state to dictionary.
    Args:
        state (AgentState): Agent state."""
    data = asdict(state)
    return data


def save_state(state: AgentState, state_path: Path) -> Path:
    """Save state to JSON.
    Args:
        state (AgentState): Agent state.
        state_path (Path): Output path."""
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state_dict(state), indent=2), encoding='utf-8')
    return state_path


def load_state(state_path: Path) -> dict[str, Any]:
    """Load state from JSON.
    Args:
        state_path (Path): State path."""
    data = json.loads(state_path.read_text(encoding='utf-8'))
    return data


def record_task(state: AgentState, task_name: str) -> AgentState:
    """Record completed task.
    Args:
        state (AgentState): Agent state.
        task_name (str): Completed task name."""
    state.completed_tasks.append(task_name)
    return state
