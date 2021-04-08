#!/usr/bin/env python3

import logging
import requests

STATUS_CAKE_BASE_URL = "https://app.statuscake.com/API/"

logger = logging.getLogger(__name__)


def get(apikey, username, endpoint, params={}):

    request_url = f"{STATUS_CAKE_BASE_URL}{endpoint}"

    logger.debug(f"Starting request: {request_url} {endpoint} {params}")

    headers = {
        "API": apikey,
        "Username": username
    }

    response = requests.get(url=request_url, params=params, headers=headers)
    response.raise_for_status()
    logger.debug(f"Request response:\n{response.content}")

    return response
