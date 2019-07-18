#!/usr/bin/env python3

import sys
import logging
from prometheus_client.core import GaugeMetricFamily
from status_cake_client import tests

logger = logging.getLogger("test_collector")


def parse_test_response(r):
    tests = []
    for i in r.json():
        tests.append(
            {
                "test_id": str(i['TestID']),
                "test_type": i['TestType'],
                "test_name": i['WebsiteName'],
                "test_url": i['WebsiteURL'],
                "test_status": i['Status'],
                "test_uptime": str(i['Uptime'])
            }
        )

    return tests


class TestCollector(object):

    def __init__(self, username, api_key, tags):
        self.username = username
        self.api_key = api_key
        self.tags = tags

    def collect(self):

        logger.info("Collector started")

        try:

            response = tests.get_tests(self.api_key, self.username, self.tags)

            test_results = parse_test_response(response)

            label_names = test_results[0].keys()

            gauge = GaugeMetricFamily(
                "status_cake_tests",
                "A basic listing of the tests under the current account.",
                labels=label_names)

            for i in test_results:
                status = 1 if (i["test_status"] == "Up") else 0
                gauge.add_metric(i.values(), status)

            yield gauge

        except Exception as e:
            logger.error(e)
            sys.exit(1)

        logger.info("Collector finished")
