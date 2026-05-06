import argparse
import logging

from app.config.settings import AppSettings, load_settings
from app.domains.domain_reader import read_domains, select_company, select_domains
from app.processing import month_utils, report_transformer
from app.reports.excel_writer import write_excel
from app.utils.logging_utils import build_logger, log_success
from app.utils.progress_tracker import ProgressState, add_error, add_processed, create_progress


REPORT_NAMES = ['visits', 'unique_users', 'duration', 'bounce_rate', 'traffic_sources']


def parse_arguments() -> argparse.Namespace:
    """Parse command arguments.
    Args:
        None (None): No arguments are required."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['download', 'process', 'full'], default='full')
    parser.add_argument('--start', type=int, default=None)
    parser.add_argument('--end', type=int, default=None)
    parser.add_argument('--amount', type=int, default=None)
    parser.add_argument('--months', type=int, default=None)
    return parser.parse_args()


def update_settings(settings: AppSettings, args: argparse.Namespace) -> AppSettings:
    """Update settings from arguments.
    Args:
        settings (AppSettings): Application settings.
        args (argparse.Namespace): Command arguments."""
    start_index = settings.start_index if args.start is None else args.start
    domain_amount = settings.domain_amount if args.amount is None else args.amount
    if args.end is None:
        end_index = start_index + domain_amount
    else:
        end_index = args.end
    report_months = settings.report_months if args.months is None else args.months
    return AppSettings(
        semrush_url=settings.semrush_url,
        semrush_email=settings.semrush_email,
        semrush_password=settings.semrush_password,
        chromedriver_path=settings.chromedriver_path,
        downloads_path=settings.downloads_path,
        domains_path=settings.domains_path,
        countries_path=settings.countries_path,
        output_path=settings.output_path,
        first_domain=settings.first_domain,
        domain_amount=domain_amount,
        start_index=start_index,
        end_index=end_index,
        report_months=report_months,
        month_year=settings.month_year,
        retry_attempts=settings.retry_attempts,
        retry_pause=settings.retry_pause,
    )


def download_reports(settings: AppSettings, logger: logging.Logger) -> ProgressState:
    """Download Semrush reports.
    Args:
        settings (AppSettings): Application settings.
        logger (logging.Logger): Logger instance."""
    from app.browser.browser_driver import create_driver
    from app.semrush.auth import login_semrush
    from app.semrush.exporter import export_domain_reports
    from app.semrush.search import domain_search, first_search

    domains = read_domains(settings.domains_path, settings.start_index, settings.end_index)
    domain_list = select_domains(domains)
    month_list = month_utils.build_months(settings.report_months)
    progress = create_progress(REPORT_NAMES, month_list)
    driver = create_driver(settings.chromedriver_path, (1600, 1600))
    try:
        logger.info('Open Semrush')
        driver.get(settings.semrush_url)
        login_semrush(
            driver,
            settings.semrush_email,
            settings.semrush_password,
            settings.retry_attempts,
            settings.retry_pause,
        )
        first_search(driver, settings.first_domain)
        for domain in domain_list:
            try:
                logger.info('Start domain: %s', domain)
                domain_search(driver, domain, settings.retry_attempts, settings.retry_pause)
                progress = export_domain_reports(
                    driver,
                    domain,
                    month_list,
                    settings.month_year,
                    settings.retry_attempts,
                    settings.retry_pause,
                    progress,
                )
                progress = add_processed(progress, domain)
                log_success(logger, f'Domain completed: {domain}')
            except Exception as error:
                progress = add_error(progress, domain, str(error))
                logger.error('Domain failed: %s %s', domain, error)
    finally:
        driver.quit()
    return progress


def process_reports(settings: AppSettings, progress: ProgressState | None, logger: logging.Logger) -> dict[str, object]:
    """Process downloaded reports.
    Args:
        settings (AppSettings): Application settings.
        progress (ProgressState | None): Progress state.
        logger (logging.Logger): Logger instance."""
    domains = read_domains(settings.domains_path, settings.start_index, settings.end_index)
    domain_list = select_domains(domains)
    month_list = month_utils.build_months(settings.report_months)
    if progress is None:
        progress = create_progress(REPORT_NAMES, month_list)
        progress.processed_domains = domain_list
        progress.report_exports['traffic_sources'] = domain_list
        for month_name in month_list:
            progress.monthly_exports['journey_sources'][month_name] = domain_list
            progress.monthly_exports['traffic_by_countries'][month_name] = domain_list

    output_data = {
        'overview': report_transformer.parse_overview(settings.downloads_path, domains),
        'trend_by_devices': report_transformer.parse_metrics(
            settings.downloads_path,
            domain_list,
            domains,
            settings.report_months,
            settings.month_year,
        ),
        'traffic_sources': report_transformer.parse_sources(
            settings.downloads_path,
            domain_list,
            domains,
            settings.report_months,
            settings.month_year,
        ),
        'journey_sources': report_transformer.parse_journey(
            settings.downloads_path,
            progress,
            domains,
            settings.month_year,
        ),
    }
    traffic_countries, country_data = report_transformer.parse_countries(
        settings.downloads_path,
        settings.countries_path,
        progress,
        domains,
        settings.month_year,
    )
    output_data['traffic_countries'] = traffic_countries
    output_data.update(country_data)
    output_data['domains_list'] = domains[['domain']]
    output_data['company_list'] = select_company(domains)

    for report_name, data in output_data.items():
        if getattr(data, 'empty', False):
            logger.warning('Report has no data: %s', report_name)
        write_excel(data, settings.output_path / f'{report_name}.xlsx')
        logger.info('Saved report: %s', report_name)
    return output_data


def run_pipeline(settings: AppSettings, mode: str, logger: logging.Logger) -> dict[str, object] | ProgressState:
    """Run pipeline.
    Args:
        settings (AppSettings): Application settings.
        mode (str): Pipeline mode.
        logger (logging.Logger): Logger instance."""
    if mode == 'download':
        return download_reports(settings, logger)
    if mode == 'process':
        return process_reports(settings, None, logger)
    progress = download_reports(settings, logger)
    return process_reports(settings, progress, logger)


def main_window() -> object:
    """Run main window.
    Args:
        None (None): No arguments are required."""
    args = parse_arguments()
    settings = update_settings(load_settings(), args)
    logger = build_logger(settings.output_path / 'pipeline.log')
    result = run_pipeline(settings, args.mode, logger)
    return result


if __name__ == '__main__':
    pipeline_result = main_window()
