#!/usr/bin/env python3

import logging
from .base import get

logger = logging.getLogger(__name__)


def get_tests(apikey, username, tags=""):
    endpoint = "Tests"
    params = {
        "tags": tags
    }
    response = get(apikey, username, endpoint, params)
    logger.debug(f"Request response:\n{response.content}")

    return response


def get_test_details(apikey, username, test_id):
    endpoint = "Tests/Details/"
    params = {
        "TestID": test_id
    }

    response = get(apikey, username, endpoint, params)
    logger.debug(f"Request response:\n{response.content}")

    return response
