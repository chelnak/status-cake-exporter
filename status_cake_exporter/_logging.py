import logging
import sys


def configure_logging(log_level: str) -> None:
    root_logger = logging.getLogger()

    log_levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warn": logging.WARN,
        "error": logging.ERROR,
    }

    if log_level not in log_levels:
        raise ValueError(f"Invalid log level: {log_level}")

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_levels[log_level])
    handler.setFormatter(formatter)

    root_logger.setLevel(log_levels[log_level])
    root_logger.addHandler(handler)
