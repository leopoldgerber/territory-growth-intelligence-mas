import argparse
from pathlib import Path

from agent_app.agent.agent import Agent, run_tasks
from agent_app.agent.agent_config import AgentSettings, build_settings
from agent_app.agent.agent_context import AgentContext
from agent_app.agent.agent_logger import build_logger
from agent_app.agent.agent_state import create_state, save_state
from agent_app.agent.planner import build_plan
from agent_app.agent.policy import filter_tasks
from agent_app.agent_tools.registry_factory import build_registry
from agent_app.playwright_runtime.browser import close_browser, create_browser
from agent_app.shared.module_adapter import include_modules


REPORT_NAMES = ['visits', 'unique_users', 'duration', 'bounce_rate', 'traffic_sources']


def parse_arguments() -> argparse.Namespace:
    """Parse command arguments.
    Args:
        None (None): No arguments are required."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--engine', choices=['playwright-agent'], default='playwright-agent')
    parser.add_argument('--mode', choices=['download', 'process', 'full'], default='full')
    parser.add_argument('--start', type=int, default=None)
    parser.add_argument('--end', type=int, default=None)
    parser.add_argument('--amount', type=int, default=None)
    parser.add_argument('--months', type=int, default=None)
    parser.add_argument('--year', type=int, default=None)
    parser.add_argument('--headless', action='store_true')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--use-storage-state', action='store_true')
    parser.add_argument('--save-screenshots', action='store_true')
    parser.add_argument('--strict-downloads', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--stop-after-first', action='store_true')
    return parser.parse_args()


def update_settings(settings: AgentSettings, args: argparse.Namespace) -> AgentSettings:
    """Update settings from arguments.
    Args:
        settings (AgentSettings): Agent settings.
        args (argparse.Namespace): Command arguments."""
    app_settings = settings.app_settings
    browser_settings = settings.browser_settings
    start_index = app_settings.start_index if args.start is None else args.start
    domain_amount = app_settings.domain_amount if args.amount is None else args.amount
    end_index = args.end if args.end is not None else start_index + domain_amount
    report_months = app_settings.report_months if args.months is None else args.months
    report_year = app_settings.month_year if args.year is None else args.year
    updated_app = type(app_settings)(
        semrush_url=app_settings.semrush_url,
        semrush_email=app_settings.semrush_email,
        semrush_password=app_settings.semrush_password,
        chromedriver_path=app_settings.chromedriver_path,
        downloads_path=app_settings.downloads_path,
        domains_path=app_settings.domains_path,
        countries_path=app_settings.countries_path,
        output_path=app_settings.output_path,
        first_domain=app_settings.first_domain,
        domain_amount=domain_amount,
        start_index=start_index,
        end_index=end_index,
        report_months=report_months,
        month_year=report_year,
        retry_attempts=app_settings.retry_attempts,
        retry_pause=app_settings.retry_pause,
    )
    updated_browser = type(browser_settings)(
        headless=args.headless or browser_settings.headless,
        window_size=browser_settings.window_size,
        timeout=browser_settings.timeout,
        downloads_path=browser_settings.downloads_path,
        artifacts_path=browser_settings.artifacts_path,
        storage_state_path=browser_settings.storage_state_path,
        use_storage_state=args.use_storage_state or browser_settings.use_storage_state,
        save_screenshots=args.save_screenshots or browser_settings.save_screenshots,
        strict_downloads=args.strict_downloads or browser_settings.strict_downloads,
    )
    updated_settings = AgentSettings(
        app_settings=updated_app,
        browser_settings=updated_browser,
        engine=args.engine,
        mode=args.mode,
        dry_run=args.dry_run,
        resume=args.resume,
        stop_after_first=args.stop_after_first,
    )
    return updated_settings


def prepare_state(settings: AgentSettings) -> tuple[object, list[str], list[str]]:
    """Prepare domains and state.
    Args:
        settings (AgentSettings): Agent settings."""
    include_modules()
    from app.domains.domain_reader import read_domains, select_domains
    from app.processing.month_utils import build_months

    app_settings = settings.app_settings
    domains = read_domains(app_settings.domains_path, app_settings.start_index, app_settings.end_index)
    domain_list = select_domains(domains)
    month_list = build_months(app_settings.report_months)
    state = create_state(settings.mode, domain_list, month_list, REPORT_NAMES)
    return state, domain_list, month_list


def run_agent(settings: AgentSettings) -> object:
    """Run agent pipeline.
    Args:
        settings (AgentSettings): Agent settings."""
    logger = build_logger(settings.browser_settings.artifacts_path / 'agent.log')
    state, domain_list, month_list = prepare_state(settings)
    tasks = build_plan(
        settings.mode,
        domain_list,
        month_list,
        settings.app_settings.month_year,
        settings.app_settings.first_domain,
        settings.stop_after_first,
    )
    tasks = filter_tasks(tasks)
    runtime = None
    page = None
    if settings.mode in ['download', 'full'] and not settings.dry_run:
        runtime = create_browser(settings.browser_settings)
        page = runtime.page
    registry = build_registry(page, settings, state, logger)
    context = AgentContext(settings=settings, state=state, registry=registry, logger=logger, page=page)
    agent = Agent(context=context)
    result = run_tasks(agent, tasks)
    save_state(state, settings.browser_settings.artifacts_path / 'agent_state.json')
    if runtime is not None:
        close_browser(runtime, settings.browser_settings)
    logger.info('Agent finished: %s', result.success)
    return result


def main_window() -> object:
    """Run main window.
    Args:
        None (None): No arguments are required."""
    args = parse_arguments()
    settings = build_settings(
        args.engine,
        args.mode,
        args.dry_run,
        args.resume,
        args.use_storage_state,
        args.stop_after_first,
    )
    settings = update_settings(settings, args)
    result = run_agent(settings)
    return result


if __name__ == '__main__':
    pipeline_result = main_window()
