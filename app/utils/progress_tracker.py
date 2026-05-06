from dataclasses import dataclass, field


@dataclass
class ProgressState:
    processed_domains: list[str] = field(default_factory=list)
    report_exports: dict[str, list[str]] = field(default_factory=dict)
    monthly_exports: dict[str, dict[str, list[str]]] = field(default_factory=dict)
    errors: dict[str, str] = field(default_factory=dict)


def create_progress(report_names: list[str], month_list: list[str]) -> ProgressState:
    """Create progress state.
    Args:
        report_names (list[str]): Report names.
        month_list (list[str]): Month names."""
    report_exports = {report_name: [] for report_name in report_names}
    monthly_exports = {
        report_name: {month: [] for month in month_list}
        for report_name in ['journey_sources', 'traffic_by_countries']
    }
    return ProgressState(report_exports=report_exports, monthly_exports=monthly_exports)


def add_processed(progress: ProgressState, domain: str) -> ProgressState:
    """Add processed domain.
    Args:
        progress (ProgressState): Progress state.
        domain (str): Domain name."""
    progress.processed_domains.append(domain)
    return progress


def add_export(progress: ProgressState, report_name: str, domain: str) -> ProgressState:
    """Add report export.
    Args:
        progress (ProgressState): Progress state.
        report_name (str): Report name.
        domain (str): Domain name."""
    progress.report_exports.setdefault(report_name, []).append(domain)
    return progress


def add_month_export(progress: ProgressState, report_name: str, month: str, domain: str) -> ProgressState:
    """Add monthly export.
    Args:
        progress (ProgressState): Progress state.
        report_name (str): Report name.
        month (str): Month name.
        domain (str): Domain name."""
    progress.monthly_exports.setdefault(report_name, {})
    progress.monthly_exports[report_name].setdefault(month, []).append(domain)
    return progress


def add_error(progress: ProgressState, domain: str, message: str) -> ProgressState:
    """Add domain error.
    Args:
        progress (ProgressState): Progress state.
        domain (str): Domain name.
        message (str): Error message."""
    progress.errors[domain] = message
    return progress
