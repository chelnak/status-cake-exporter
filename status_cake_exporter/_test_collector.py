#!/usr/bin/env python3

import logging

from prometheus_client.core import GaugeMetricFamily
from prometheus_client.registry import Collector

from ._status_cake import StatusCake

logger = logging.getLogger("test_collector")


def transform(
    tests: list[dict[str, str]], tests_in_maintenance: list[str]
) -> list[dict[str, str]] | None:
    t: list[dict[str, str]] = []
    for i in tests:
        t.append(
            {
                "test_id": str(i["id"]),
                "test_type": str(
                    i["test_type"]
                ),  # This is random but we get an ApiAttributeError if we don't do this.
                "test_name": i["name"],
                "test_url": i["website_url"],
                "test_status_int": str(1 if (i["status"] == "up") else 0),
                "test_uptime_percent": str(i["uptime"]),
                "maintenance_status_int": str(
                    1 if (str(i["id"])) in tests_in_maintenance else 0
                ),
            }
        )

        return t if len(t) > 0 else []


class TestCollector(Collector):
    def __init__(self, username: str, api_key: str, tags: str):
        self.username: str = username
        self.api_key: str = api_key
        self.tags: str = tags

    def collect(self):

        statuscake = StatusCake(self.username, self.api_key)

        logger.info("Collector started.")

        try:
            maintenance = statuscake.list_maintenance_windows()
            logger.debug(f"Maintenance response: {maintenance}")

            tests_in_maintenance = [i["id"] for i in maintenance]
            logger.info(
                f"Found {len(tests_in_maintenance)} tests that are in maintenance."
            )

            tests = statuscake.list_tests()
            metrics = transform(tests, tests_in_maintenance)
            if metrics is None:
                logger.info("There are no test metrics to publish.")
                return

            # status_cake_test_info - gauge
            logger.info(f"Publishing {len(metrics)} test metrics.")
            info_gauge = GaugeMetricFamily(
                "status_cake_test_info",
                "A basic listing of the tests under the current account.",
                labels=list(metrics[0].keys()),
            )

            for i in metrics:
                info_gauge.add_metric(list(i.values()), float(i["test_status_int"]))

            yield info_gauge

            # status_cake_test_uptime_percent - gauge
            logger.info(f"Publishing {len(metrics)} uptime metrics.")
            uptime_gauge = GaugeMetricFamily(
                "status_cake_test_uptime_percent",
                "Tests and their uptime percentage",
                labels=["test_id"],
            )

            for i in metrics:
                uptime_gauge.add_metric([i["test_id"]], float(i["test_uptime_percent"]))

            yield uptime_gauge

            logger.info("Collector finished.")

        except Exception as e:
            logger.error(e)
