#!/usr/bin/env python3

import logging
from .base import get
import time

logger = logging.getLogger(__name__)


def get_tests(use_v1_uptime_endpoints, timeout, apikey, username, tags=""):
    tests = []
    if use_v1_uptime_endpoints:
        page = 1
        endpoint = "uptime"
        params = {
            "tags": tags,
            "page": page
        }
        response = get(use_v1_uptime_endpoints, apikey, username, endpoint, params)
        if response is not None:
            tests = response.json()['data']
        time.sleep(timeout)
        logger.debug("Total page count " + str(response.json()['metadata']['page_count']))
        while (page < (response.json()['metadata']['page_count'])):
            page += 1
            params["page"] = page
            response = get(use_v1_uptime_endpoints, apikey, username, endpoint, params)
            if response is not None and response != "":
                tests += response.json()['data']
            time.sleep(timeout)
    else:
        endpoint = "Tests"
        params = {
            "tags": tags

        }
        response = get(use_v1_uptime_endpoints, apikey, username, endpoint, params)
        if response is not None and response != "":
            tests += response.json()['data']

    if response is not None:
        logger.debug(f"Request response:\n{response.content}")

    return tests
