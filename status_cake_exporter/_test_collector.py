#!/usr/bin/env python3

import logging

from prometheus_client.core import GaugeMetricFamily
from prometheus_client.registry import Collector

from ._status_cake import StatusCake

logger = logging.getLogger("test_collector")


def get_uptime_status(status: str) -> str:
    """
    Helper method that returns the appropriate status string for the
    uptime metric.

    Args:
        status: [str] The status of the test

    Returns:
        str
    """
    return "1" if status == "up" else "0"


def get_test_maintenance_status(id: str, tests_in_maintenance: list[str]) -> str:
    """
    Helper method that returns the appropriate status string for the maintenance metric.

    Args:
        id: [str] The id of the test
        tests_in_maintenance: [list[str]] A list of tests that are in maintenance

    Returns:
        str
    """
    return "1" if id in tests_in_maintenance else "0"


def get_tests_in_maintenance(maintenance_windows: list[dict[str, str]]) -> list[str]:
    """
    Get a unique list of tests that are in maintenance

    Args:
        maintenance_windows: [list[dict[str, str]]] The list of maintenance windows

    Returns:
        list[str]
    """
    t: list[str] = []

    # Return early if there are no maintenance windows otherwise we get an index out of range error
    if len(maintenance_windows) == 0:
        return t

    for i in maintenance_windows:
        t.extend(i["tests"])

    return list(set(t)) if len(t) > 0 else []


def transform(
    tests: list[dict[str, str]], tests_in_maintenance: list[str]
) -> list[dict[str, str]]:
    """
    Transform the tests into a format that prometheus can consume

    Args:
        tests: [list[dict[str, str]]] The list of tests to transform
        tests_in_maintenance: [list[str]] The list of tests that are in maintenance

    Returns:
        list[dict[str, str]]
    """
    logger.info("Transforming uptime test response to prometheus metrics")
    t: list[dict[str, str]] = []

    for i in tests:
        logger.debug(f"Transforming test id: {i['id']}")
        t.append(
            {
                "test_id": str(i["id"]),
                "test_type": str(
                    i["test_type"]
                ),  # This is random but we get an ApiAttributeError if we don't do this.
                "test_name": i["name"],
                "test_url": i["website_url"],
                "test_status_int": get_uptime_status(i["status"]),
                "test_uptime_percent": str(i["uptime"]),
                "maintenance_status_int": get_test_maintenance_status(
                    i["id"], tests_in_maintenance
                ),
            }
        )
        logger.debug(f"Transformed test id: {i['id']}")

    logger.debug(f"Test transformation complete. Returning {len(t)} metrics")
    return t if len(t) > 0 else []


class TestCollector(Collector):
    """The collector subclass responsible for gathering test metrics from the StatusCake API."""

    def __init__(self, api_key: str, per_page: int, tags: str):
        """
        Args:
            api_key: [str] The StatusCake API key
            per_page: [int] The number of tests to return per page
            tags: [str] The tags to filter the tests by
        """
        self.api_key: str = api_key
        self.per_page: int = per_page
        self.tags: str = tags

    def collect(self):
        """
        Collects metrics from the StatusCake API and returns them to the Prometheus client.

        Yields:
            [Generator] The generator that yields the metrics to the Prometheus client.
        """
        statuscake = StatusCake(self.api_key, self.per_page)

        logger.info("Collector started.")

        try:
            logger.debug("Fetching maintenance windows")
            maintenance = statuscake.list_maintenance_windows()

            tests_in_maintenance = get_tests_in_maintenance(maintenance)
            logger.info(
                f"Found {len(tests_in_maintenance)} tests that are in maintenance."
            )

            logger.debug("Fetching uptime tests")
            tests = statuscake.list_tests(self.tags)

            metrics = transform(tests, tests_in_maintenance)
            if len(metrics) == 0:
                logger.info("There are no test metrics to publish.")
                return

            # status_cake_test_info - gauge
            logger.info(f"Publishing {len(metrics)} test metric(s).")
            info_gauge = GaugeMetricFamily(
                "status_cake_test_info",
                "A basic listing of the tests under the current account.",
                labels=list(metrics[0].keys()),
            )

            for i in metrics:
                info_gauge.add_metric(list(i.values()), float(i["test_status_int"]))

            yield info_gauge

            # status_cake_test_uptime_percent - gauge
            logger.info(f"Publishing {len(metrics)} uptime metric(s).")
            uptime_gauge = GaugeMetricFamily(
                "status_cake_test_uptime_percent",
                "Tests and their uptime percentage",
                labels=["test_id"],
            )

            for i in metrics:
                uptime_gauge.add_metric([i["test_id"]], float(i["test_uptime_percent"]))

            yield uptime_gauge

        except Exception as e:
            # This should stop the expoter from crashing if there is an error.
            logger.fatal(f"A fatal error occurred: {e}")

        finally:
            logger.info("Collector finished.")
