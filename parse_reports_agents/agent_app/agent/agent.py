from dataclasses import dataclass

from agent_app.agent.action_result import ActionResult, failure_result, success_result
from agent_app.agent.agent_context import AgentContext
from agent_app.agent.agent_state import record_task
from agent_app.agent.observation import empty_observation, observe_page
from agent_app.agent.tasks import AgentTask
from agent_app.agent_tools.tool_registry import call_tool


@dataclass
class Agent:
    context: AgentContext


def run_action(agent: Agent, tool_name: str, params: dict[str, object]) -> ActionResult:
    """Run agent action.
    Args:
        agent (Agent): Agent instance.
        tool_name (str): Tool name.
        params (dict[str, object]): Tool parameters."""
    if agent.context.settings.dry_run:
        return success_result('Dry run action planned', {'tool': tool_name, 'params': params})
    result = call_tool(agent.context.registry, tool_name, params)
    return result


def run_task(agent: Agent, task: AgentTask) -> ActionResult:
    """Run agent task.
    Args:
        agent (Agent): Agent instance.
        task (AgentTask): Agent task."""
    logger = agent.context.logger
    logger.info('Task started: %s', task.name)
    observation = empty_observation()
    if agent.context.page is not None:
        observation = observe_page(agent.context.page)
    logger.info('Observation received: %s %s', observation.url, observation.title)
    for action in task.actions:
        logger.info('Tool called: %s', action.tool_name)
        result = run_action(agent, action.tool_name, action.params)
        logger.info('Action result: %s %s', result.success, result.message)
        if not result.success:
            logger.error('Task failed: %s %s', task.name, result.error)
            return result
    record_task(agent.context.state, task.name)
    logger.info('Task completed: %s', task.name)
    return success_result('Task completed', {'task': task.name})


def run_tasks(agent: Agent, tasks: list[AgentTask]) -> ActionResult:
    """Run agent tasks.
    Args:
        agent (Agent): Agent instance.
        tasks (list[AgentTask]): Agent tasks."""
    for task in tasks:
        result = run_task(agent, task)
        if not result.success:
            return failure_result('Pipeline failed', result.error or result.message, {'task': task.name})
    return success_result('Pipeline completed', {'tasks': [task.name for task in tasks]})
