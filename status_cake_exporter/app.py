import logging
import os
import sys
import time

import typer
from prometheus_client import REGISTRY, start_http_server

from ._logging import configure_logging
from ._test_collector import TestCollector


def exporter(
    username: str = typer.Option(
        "",
        help="Username for the account. This is only required for legacy accounts.",
        envvar="USERNAME",
    ),
    api_key: str = typer.Option(..., help="API Key for the account.", envvar="API_KEY"),
    tags: str = typer.Option(
        "",
        help="A comma separated list of tags used to filter tests returned from the api",
        envvar="TAGS",
    ),
    log_level: str = typer.Option(
        "info",
        help="The log level of the application. Value can be one of {debug, info, warn, error}",
        envvar="LOG_LEVEL",
    ),
    port: int = typer.Option(8000, envvar="PORT"),
):

    try:
        configure_logging(log_level)
        logger = logging.getLogger(__name__)

        logger.info(f"Starting web server on port: {port}")
        start_http_server(port)

        logger.info("Registering collectors.")
        test_collector = TestCollector(username, api_key, tags)
        REGISTRY.register(test_collector)

        while True:
            time.sleep(1)

    except BrokenPipeError:
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)
    finally:
        sys.stdout.flush()


def run():
    typer.run(exporter)
