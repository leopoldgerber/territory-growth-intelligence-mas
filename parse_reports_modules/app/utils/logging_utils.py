import logging
from pathlib import Path


def build_logger(log_path: Path | None = None) -> logging.Logger:
    """Build application logger.
    Args:
        log_path (Path | None): Optional path to log file."""
    logger = logging.getLogger('territory_growth')
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    if log_path is not None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    return logger


def log_success(logger: logging.Logger, message: str) -> logging.Logger:
    """Log success message.
    Args:
        logger (logging.Logger): Logger instance.
        message (str): Message text."""
    logger.info('SUCCESS: %s', message)
    return logger
