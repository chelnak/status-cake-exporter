#!/usr/bin/env python3

import sys
import logging


def configure_logging(log_level):

    root_logger = logging.getLogger()

    log_levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warn": logging.WARN,
        "error": logging.ERROR,
    }

    root_logger.setLevel(log_levels.get(log_level))
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_levels.get(log_level))
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
