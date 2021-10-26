#!/usr/bin/env python3

import logging
from .base import get

logger = logging.getLogger(__name__)


def get_tests(use_v1_uptime_endpoints, apikey, username, tags=""):
    if use_v1_uptime_endpoints:
        page = 1
        endpoint = "uptime"
        params = {
            "tags": tags,
            "page": page
        }
        response = get(use_v1_uptime_endpoints, apikey, username, endpoint, params)
        tests = response.json()['data']
        while (page < (response.json()['metadata']['page_count'])):
            page += 1
            params["page"] = page
            response = get(use_v1_uptime_endpoints, apikey, username, endpoint, params)
            tests += response.json()['data']
    else:
        endpoint = "Tests"
        params = {
            "tags": tags
        }
        response = get(use_v1_uptime_endpoints, apikey, username, endpoint, params)
        tests = response.json()['data']
    logger.debug(f"Request response:\n{response.content}")

    return tests
