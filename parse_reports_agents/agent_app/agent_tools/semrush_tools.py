import time
from pathlib import Path
from typing import Any

from agent_app.agent.action_result import ActionResult, failure_result, success_result
from agent_app.agent.agent_config import AgentSettings
from agent_app.playwright_runtime import actions
from agent_app.playwright_runtime.downloads import DownloadRecord, add_download
from agent_app.playwright_runtime.locators import metric_button, month_button, semrush_locators


def login_semrush(page: Any, settings: AgentSettings) -> ActionResult:
    """Login to Semrush.
    Args:
        page (Any): Playwright page.
        settings (AgentSettings): Agent settings."""
    app_settings = settings.app_settings
    if app_settings.semrush_email == '' or app_settings.semrush_password == '':
        return failure_result('Semrush credentials missing', 'SEMRUSH_EMAIL and SEMRUSH_PASSWORD are required')
    locators = semrush_locators()
    email_result = actions.fill_input(page, locators.email_input, app_settings.semrush_email, settings.browser_settings.timeout)
    if not email_result.success:
        return email_result
    password_result = actions.fill_input(
        page,
        locators.password_input,
        app_settings.semrush_password,
        settings.browser_settings.timeout,
    )
    if not password_result.success:
        return password_result
    press_result = actions.press_key(page, locators.password_input, 'Enter', settings.browser_settings.timeout)
    return press_result


def search_domain(page: Any, domain: str, settings: AgentSettings) -> ActionResult:
    """Search Semrush domain.
    Args:
        page (Any): Playwright page.
        domain (str): Domain name.
        settings (AgentSettings): Agent settings."""
    locators = semrush_locators()
    clear_result = actions.click_element(page, locators.search_clear_button, 1500)
    selector = locators.search_input if clear_result.success else locators.first_search_input
    fill_result = actions.fill_input(page, selector, domain, settings.browser_settings.timeout)
    if not fill_result.success:
        return fill_result
    result = actions.press_key(page, selector, 'Enter', settings.browser_settings.timeout)
    time.sleep(2)
    return result


def traffic_page(page: Any, settings: AgentSettings) -> ActionResult:
    """Open traffic analytics.
    Args:
        page (Any): Playwright page.
        settings (AgentSettings): Agent settings."""
    locators = semrush_locators()
    result = actions.click_element(page, locators.traffic_analytics_link, settings.browser_settings.timeout)
    return result


def journey_page(page: Any, settings: AgentSettings) -> ActionResult:
    """Open journey tab.
    Args:
        page (Any): Playwright page.
        settings (AgentSettings): Agent settings."""
    locators = semrush_locators()
    actions.scroll_page(page, 900)
    result = actions.click_element(page, locators.journey_tab, settings.browser_settings.timeout)
    return result


def geo_page(page: Any, settings: AgentSettings) -> ActionResult:
    """Open geo tab.
    Args:
        page (Any): Playwright page.
        settings (AgentSettings): Agent settings."""
    locators = semrush_locators()
    actions.scroll_page(page, 900)
    result = actions.click_element(page, locators.geo_tab, settings.browser_settings.timeout)
    return result


def select_month(page: Any, month_name: str, year: int, settings: AgentSettings) -> ActionResult:
    """Select report month.
    Args:
        page (Any): Playwright page.
        month_name (str): Month name.
        year (int): Report year.
        settings (AgentSettings): Agent settings."""
    locators = semrush_locators()
    picker_result = actions.click_element(page, locators.month_picker, settings.browser_settings.timeout)
    if not picker_result.success:
        return picker_result
    month_result = actions.click_element(page, month_button(month_name, year), settings.browser_settings.timeout)
    if not month_result.success:
        return month_result
    apply_result = actions.click_element(page, locators.month_apply, settings.browser_settings.timeout)
    return apply_result


def save_download(
    page: Any,
    selector: str,
    output_path: Path,
    settings: AgentSettings,
    record: DownloadRecord,
) -> ActionResult:
    """Save browser download.
    Args:
        page (Any): Playwright page.
        selector (str): Download selector.
        output_path (Path): Output path.
        settings (AgentSettings): Agent settings.
        record (DownloadRecord): Download record."""
    result = actions.download_file(page, selector, output_path, settings.browser_settings.timeout)
    if not result.success:
        return result
    add_download(settings.browser_settings.downloads_path, record)
    return success_result('Download saved', {'path': str(output_path), 'report': record.report_name})


def export_metric(page: Any, metric_name: str, domain: str, settings: AgentSettings) -> ActionResult:
    """Export metric report.
    Args:
        page (Any): Playwright page.
        metric_name (str): Metric name.
        domain (str): Domain name.
        settings (AgentSettings): Agent settings."""
    locators = semrush_locators()
    button_result = actions.click_element(page, metric_button(metric_name), settings.browser_settings.timeout)
    if not button_result.success:
        return button_result
    export_result = actions.click_element(page, locators.traffic_chart_export, settings.browser_settings.timeout)
    if not export_result.success:
        return export_result
    output_path = settings.browser_settings.downloads_path / f'{domain}-{metric_name}.csv'
    record = DownloadRecord(domain=domain, report_name=metric_name, month_name='', file_path=str(output_path))
    result = save_download(page, locators.traffic_csv_option, output_path, settings, record)
    return result


def export_sources(page: Any, domain: str, settings: AgentSettings) -> ActionResult:
    """Export traffic sources.
    Args:
        page (Any): Playwright page.
        domain (str): Domain name.
        settings (AgentSettings): Agent settings."""
    locators = semrush_locators()
    actions.scroll_page(page, 1000)
    output_path = settings.browser_settings.downloads_path / f'{domain}-traffic_sources.csv'
    record = DownloadRecord(domain=domain, report_name='traffic_sources', month_name='', file_path=str(output_path))
    result = save_download(page, locators.traffic_sources_export, output_path, settings, record)
    return result


def export_journey(page: Any, domain: str, month_name: str, settings: AgentSettings) -> ActionResult:
    """Export journey sources.
    Args:
        page (Any): Playwright page.
        domain (str): Domain name.
        month_name (str): Month name.
        settings (AgentSettings): Agent settings."""
    locators = semrush_locators()
    output_path = settings.browser_settings.downloads_path / f'{domain}-journey-{month_name}.csv'
    record = DownloadRecord(domain=domain, report_name='journey_sources', month_name=month_name, file_path=str(output_path))
    result = save_download(page, locators.journey_csv_button, output_path, settings, record)
    return result


def export_geo(page: Any, domain: str, month_name: str, settings: AgentSettings) -> ActionResult:
    """Export traffic by country.
    Args:
        page (Any): Playwright page.
        domain (str): Domain name.
        month_name (str): Month name.
        settings (AgentSettings): Agent settings."""
    locators = semrush_locators()
    output_path = settings.browser_settings.downloads_path / f'{domain}-geo-{month_name}.csv'
    record = DownloadRecord(domain=domain, report_name='traffic_by_countries', month_name=month_name, file_path=str(output_path))
    result = save_download(page, locators.geo_csv_button, output_path, settings, record)
    return result
