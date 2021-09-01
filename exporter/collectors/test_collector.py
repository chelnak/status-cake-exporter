#!/usr/bin/env python3

import sys
import logging
from prometheus_client.core import GaugeMetricFamily
from status_cake_client import tests as t
from status_cake_client import maintenance as m

logger = logging.getLogger("test_collector")

def parse_test_response(r, m):
    t = []
    try:
        tests = r.json()
    except Exception as e:
        logger.error(f"Could not parse test data, exception: {e}")
        logger.error(f"Test data was:\n{r}")
        sys.exit(1)
    for i in tests:
        t.append(
            {
                "test_id": str(i['TestID']),
                "test_type": i['TestType'],
                "test_name": i['WebsiteName'],
                "test_url": i['WebsiteURL'],
                "test_status_int": str(1 if (i["Status"] == "Up") else 0),
                "test_uptime_percent": str(i['Uptime']),
                "maintenance_status_int": str(1 if (str(i["TestID"])) in m else 0)
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

        logger.info("Collector started.")

        try:

            maintenance = m.get_maintenance(self.api_key, self.username)
            try:
                maintenance_data = maintenance.json()['data']
            except Exception as e:
                logger.error(f"Could not parse maintenace data, exception: {e}")
                logger.error(f"Data was:\n{maintenance}")
                sys.exit(1)
            logger.debug(f"Maintenance response:\n{maintenance_data}")

            # Grab the test_ids from the response
            m_test_id_list = [i['all_tests'] for i in maintenance_data]

            # Flatten the test_ids into a list
            m_test_id_flat_list = [item for sublist in m_test_id_list for item in sublist]
            logger.info(f"Found {len(m_test_id_flat_list)} tests that are in maintenance.")

            tests = t.get_tests(self.api_key, self.username, self.tags)
            parsed_tests = parse_test_response(tests, m_test_id_flat_list)
            logger.info(f"Publishing {len(parsed_tests)} tests.")

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
                "Tests and their uptime percentage",
                labels=uptime_label_names)

            for i in parsed_tests:
                uptime_gauge.add_metric(
                    [i["test_id"]], i["test_uptime_percent"])

            yield uptime_gauge

        except Exception as e:
            logger.error(e)
            sys.exit(1)

        logger.info("Collector finished.")
