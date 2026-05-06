from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AgentAction:
    tool_name: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AgentTask:
    name: str
    expected_state: str
    allowed_tools: list[str]
    success_criteria: list[str]
    actions: list[AgentAction]
    retry_attempts: int = 1


def login_task() -> AgentTask:
    """Build login task.
    Args:
        None (None): No arguments are required."""
    task = AgentTask(
        name='LoginTask',
        expected_state='Semrush login page is open',
        allowed_tools=['open_url', 'login_to_semrush'],
        success_criteria=['Semrush session is available'],
        actions=[
            AgentAction('open_url', {}),
            AgentAction('login_to_semrush', {}),
        ],
    )
    return task


def initial_search(domain: str) -> AgentTask:
    """Build initial search task.
    Args:
        domain (str): First domain."""
    task = AgentTask(
        name='InitialSearchTask',
        expected_state='Semrush search is available',
        allowed_tools=['search_domain'],
        success_criteria=['Domain page is loaded'],
        actions=[AgentAction('search_domain', {'domain': domain})],
    )
    return task


def traffic_task(domain: str) -> AgentTask:
    """Build traffic export task.
    Args:
        domain (str): Domain name."""
    task = AgentTask(
        name=f'ExportTrafficAnalyticsTask:{domain}',
        expected_state='Traffic Analytics is open',
        allowed_tools=['search_domain', 'go_to_traffic_analytics', 'export_metric_report', 'export_traffic_sources'],
        success_criteria=['Traffic metrics and sources are downloaded'],
        actions=[
            AgentAction('search_domain', {'domain': domain}),
            AgentAction('go_to_traffic_analytics', {}),
            AgentAction('export_metric_report', {'metric_name': 'visits', 'domain': domain}),
            AgentAction('export_metric_report', {'metric_name': 'unique_users', 'domain': domain}),
            AgentAction('export_metric_report', {'metric_name': 'duration', 'domain': domain}),
            AgentAction('export_metric_report', {'metric_name': 'bounce_rate', 'domain': domain}),
            AgentAction('export_traffic_sources', {'domain': domain}),
        ],
    )
    return task


def journey_task(domain: str, month_list: list[str], year: int) -> AgentTask:
    """Build journey export task.
    Args:
        domain (str): Domain name.
        month_list (list[str]): Month names.
        year (int): Report year."""
    actions = [AgentAction('go_to_journey_tab', {})]
    for month_name in month_list:
        actions.append(AgentAction('set_month', {'month_name': month_name, 'year': year}))
        actions.append(AgentAction('export_journey_sources', {'domain': domain, 'month_name': month_name}))
    task = AgentTask(
        name=f'ExportJourneyTask:{domain}',
        expected_state='Journey tab is open',
        allowed_tools=['go_to_journey_tab', 'set_month', 'export_journey_sources'],
        success_criteria=['Journey CSV files are downloaded for each month'],
        actions=actions,
    )
    return task


def geo_task(domain: str, month_list: list[str], year: int) -> AgentTask:
    """Build geo export task.
    Args:
        domain (str): Domain name.
        month_list (list[str]): Month names.
        year (int): Report year."""
    actions = [AgentAction('go_to_geo_distribution_tab', {})]
    for month_name in month_list:
        actions.append(AgentAction('set_month', {'month_name': month_name, 'year': year}))
        actions.append(AgentAction('export_traffic_by_country', {'domain': domain, 'month_name': month_name}))
    task = AgentTask(
        name=f'ExportGeoDistributionTask:{domain}',
        expected_state='Geo Distribution tab is open',
        allowed_tools=['go_to_geo_distribution_tab', 'set_month', 'export_traffic_by_country'],
        success_criteria=['Geo CSV files are downloaded for each month'],
        actions=actions,
    )
    return task


def domain_tasks(domain: str, month_list: list[str], year: int) -> list[AgentTask]:
    """Build domain task list.
    Args:
        domain (str): Domain name.
        month_list (list[str]): Month names.
        year (int): Report year."""
    tasks = [
        traffic_task(domain),
        journey_task(domain, month_list, year),
        geo_task(domain, month_list, year),
    ]
    return tasks


def process_task() -> AgentTask:
    """Build processing task.
    Args:
        None (None): No arguments are required."""
    task = AgentTask(
        name='ProcessDownloadedReportsTask',
        expected_state='CSV files are available',
        allowed_tools=['process_downloaded_reports'],
        success_criteria=['Excel files are saved'],
        actions=[AgentAction('process_downloaded_reports', {})],
    )
    return task
