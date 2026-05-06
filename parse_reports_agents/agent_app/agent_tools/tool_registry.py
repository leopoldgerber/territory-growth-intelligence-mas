from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from agent_app.agent.action_result import ActionResult, failure_result


ToolHandler = Callable[..., ActionResult]


@dataclass
class ToolRegistry:
    tools: dict[str, ToolHandler] = field(default_factory=dict)


def register_tool(registry: ToolRegistry, name: str, handler: ToolHandler) -> ToolRegistry:
    """Register tool handler.
    Args:
        registry (ToolRegistry): Tool registry.
        name (str): Tool name.
        handler (ToolHandler): Tool handler."""
    registry.tools[name] = handler
    return registry


def call_tool(registry: ToolRegistry, name: str, params: dict[str, Any]) -> ActionResult:
    """Call registered tool.
    Args:
        registry (ToolRegistry): Tool registry.
        name (str): Tool name.
        params (dict[str, Any]): Tool parameters."""
    handler = registry.tools.get(name)
    if handler is None:
        return failure_result('Tool not found', f'Unknown tool: {name}', {'tool': name})
    try:
        result = handler(**params)
    except Exception as error:
        return failure_result('Tool failed', str(error), {'tool': name})
    return result


def tool_names(registry: ToolRegistry) -> list[str]:
    """List registered tools.
    Args:
        registry (ToolRegistry): Tool registry."""
    names = sorted(registry.tools)
    return names
