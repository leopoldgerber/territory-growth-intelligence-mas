import logging
from pathlib import Path


def build_logger(log_path: Path) -> logging.Logger:
    """Build agent logger.
    Args:
        log_path (Path): Log file path."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger('parse_reports_agent')
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)
    return logger


def correlation_id(domain: str, report_name: str = '') -> str:
    """Build correlation id.
    Args:
        domain (str): Domain name.
        report_name (str): Report name."""
    parts = [domain.replace('.', '_')]
    if report_name != '':
        parts.append(report_name)
    value = '-'.join(parts)
    return value
