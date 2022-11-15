import logging
import os
import sys
import time

import typer
from prometheus_client import REGISTRY, start_http_server

from ._logging import configure_logging
from ._test_collector import TestCollector

logger = logging.getLogger("exporter")


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
    items_per_page=typer.Option(
        25,
        help="The number of items that the api will return on a page. This is a global option.",
        envvar="ITEMS_PER_PAGE",
    ),
):

    try:
        configure_logging(log_level)

        logger.info(f"Starting web server on port: {port}")
        start_http_server(port)

        logger.info("Registering collectors.")
        test_collector = TestCollector(username, api_key, items_per_page, tags)
        REGISTRY.register(test_collector)

        while True:
            time.sleep(1)

    except BrokenPipeError:
        logger.fatal("Broken pipe error. Exiting.")
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)
    except Exception as e:
        logger.fatal(f"An unhandled exception occured: {e}")
        exit(1)
    finally:
        logger.debug("Shutting down.")
        sys.stdout.flush()


def run():
    typer.run(exporter)
