from agent_app.agent.tasks import AgentTask


def validate_policy(task: AgentTask) -> bool:
    """Validate task policy.
    Args:
        task (AgentTask): Agent task."""
    allowed_tools = set(task.allowed_tools)
    action_tools = {action.tool_name for action in task.actions}
    is_valid = action_tools.issubset(allowed_tools)
    return is_valid


def filter_tasks(tasks: list[AgentTask]) -> list[AgentTask]:
    """Filter policy-safe tasks.
    Args:
        tasks (list[AgentTask]): Agent tasks."""
    valid_tasks = [task for task in tasks if validate_policy(task)]
    return valid_tasks
