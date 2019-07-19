#!/usr/bin/env python3

import sys
import logging
from prometheus_client.core import GaugeMetricFamily
from status_cake_client import tests as t

logger = logging.getLogger("test_collector")


def parse_test_response(r):
    t = []
    for i in r.json():
        t.append(
            {
                "test_id": str(i['TestID']),
                "test_type": i['TestType'],
                "test_name": i['WebsiteName'],
                "test_url": i['WebsiteURL'],
                "test_status_int": str(1 if (i["Status"] == "Up") else 0)
            }
        )

    return t


def parse_test_details_response(r):
    t = []
    for i in r:
        t.append(
            {
                "test_id": str(i['TestID']),
                "test_status_string": i['Status'],
                "test_status_int": str(1 if (i["Status"] == "Up") else 0),
                "test_uptime_percent": str(i['Uptime']),
                "test_last_tested": i['LastTested'],
                "test_processing": i['Processing'],
                "test_down_times": str(i['DownTimes'])
            }
        )

    return t


class TestCollector(object):

    def __init__(self, username, api_key, tags):
        self.username = username
        self.api_key = api_key
        self.tags = tags

    def collect(self):

        logger.info("Collector started")

        try:

            tests = t.get_tests(self.api_key, self.username, self.tags)
            parsed_tests = parse_test_response(tests)

            test_id_list = [i['TestID'] for i in tests.json()]
            test_details = []
            for i in test_id_list:
                test_details.append(
                    t.get_test_details(self.api_key, self.username, i).json()
                )
            parsed_test_details = parse_test_details_response(test_details)

            # status_cake_test_info - gauge
            label_names = parsed_tests[0].keys()
            info_gauge = GaugeMetricFamily(
                "status_cake_test_info",
                "A basic listing of the tests under the current account.",
                labels=label_names)

            for i in parsed_tests:
                info_gauge.add_metric(i.values(), i["test_status_int"])

            yield info_gauge

            # status_cake_test_uptime_percent - gauge
            uptime_label_names = [
                "test_id"
            ]

            uptime_gauge = GaugeMetricFamily(
                "status_cake_test_uptime_percent",
                "Tests and their uptime percetage",
                labels=uptime_label_names)

            for i in parsed_test_details:
                uptime_gauge.add_metric(
                    [i["test_id"]], i["test_uptime_percent"])

            yield uptime_gauge

        except Exception as e:
            logger.error(e)
            sys.exit(1)

        logger.info("Collector finished")
