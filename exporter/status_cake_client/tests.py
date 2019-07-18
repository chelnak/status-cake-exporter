#!/usr/bin/env python3

import requests
import logging
from status_cake_client import STATUS_CAKE_BASE_URL


logger = logging.getLogger(__name__)


def get_tests(apikey, username, tags=""):
    endpoint = "Tests"
    request_url = "{base}{endpoint}".format(
        base=STATUS_CAKE_BASE_URL, endpoint=endpoint)

    logger.info("Sending request to {request_url}".format(
        request_url=request_url))

    headers = {
        "API": apikey,
        "Username": username
    }

    params = {
        "tags": tags
    }

    response = requests.get(url=request_url, params=params, headers=headers)
    response.raise_for_status()

    return response
