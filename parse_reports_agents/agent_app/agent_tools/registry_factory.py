from typing import Any

from agent_app.agent.agent_config import AgentSettings
from agent_app.agent.agent_state import AgentState
from agent_app.agent_tools.browser_tools import open_url
from agent_app.agent_tools.download_tools import process_reports_tool
from agent_app.agent_tools.semrush_tools import (
    export_geo,
    export_journey,
    export_metric,
    export_sources,
    geo_page,
    journey_page,
    login_semrush,
    search_domain,
    select_month,
    traffic_page,
)
from agent_app.agent_tools.tool_registry import ToolRegistry, register_tool


def build_registry(page: Any, settings: AgentSettings, state: AgentState, logger: object) -> ToolRegistry:
    """Build tool registry.
    Args:
        page (Any): Playwright page.
        settings (AgentSettings): Agent settings.
        state (AgentState): Agent state.
        logger (object): Logger instance."""
    registry = ToolRegistry()
    register_tool(registry, 'open_url', lambda: open_url(page, settings))
    register_tool(registry, 'login_to_semrush', lambda: login_semrush(page, settings))
    register_tool(registry, 'search_domain', lambda domain: search_domain(page, domain, settings))
    register_tool(registry, 'go_to_traffic_analytics', lambda: traffic_page(page, settings))
    register_tool(registry, 'go_to_journey_tab', lambda: journey_page(page, settings))
    register_tool(registry, 'go_to_geo_distribution_tab', lambda: geo_page(page, settings))
    register_tool(registry, 'set_month', lambda month_name, year: select_month(page, month_name, year, settings))
    register_tool(
        registry,
        'export_metric_report',
        lambda metric_name, domain: export_metric(page, metric_name, domain, settings),
    )
    register_tool(registry, 'export_traffic_sources', lambda domain: export_sources(page, domain, settings))
    register_tool(
        registry,
        'export_journey_sources',
        lambda domain, month_name: export_journey(page, domain, month_name, settings),
    )
    register_tool(
        registry,
        'export_traffic_by_country',
        lambda domain, month_name: export_geo(page, domain, month_name, settings),
    )
    register_tool(registry, 'process_downloaded_reports', lambda: process_reports_tool(settings, state, logger))
    return registry
