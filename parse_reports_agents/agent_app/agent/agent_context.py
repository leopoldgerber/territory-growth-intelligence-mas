from dataclasses import dataclass
from logging import Logger
from typing import Any

from agent_app.agent.agent_config import AgentSettings
from agent_app.agent.agent_state import AgentState
from agent_app.agent_tools.tool_registry import ToolRegistry


@dataclass
class AgentContext:
    settings: AgentSettings
    state: AgentState
    registry: ToolRegistry
    logger: Logger
    page: Any | None = None
    browser_context: Any | None = None
