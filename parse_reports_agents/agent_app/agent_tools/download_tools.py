from agent_app.agent.action_result import ActionResult, success_result
from agent_app.agent.agent_config import AgentSettings
from agent_app.agent.agent_state import AgentState
from agent_app.shared.module_adapter import include_modules


def process_reports_tool(settings: AgentSettings, state: AgentState, logger: object) -> ActionResult:
    """Process downloaded reports.
    Args:
        settings (AgentSettings): Agent settings.
        state (AgentState): Agent state.
        logger (object): Logger instance."""
    include_modules()
    from app.pipeline_runner import process_reports

    output_data = process_reports(settings.app_settings, state.progress, logger)
    evidence = {'reports': sorted(output_data.keys())}
    result = success_result('Downloaded reports processed', evidence)
    return result
