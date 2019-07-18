#!/usr/bin/env python3

import logging
import requests

STATUS_CAKE_BASE_URL = "https://app.statuscake.com/API/"

logger = logging.getLogger(__name__)


def get(apikey, username, endpoint, params={}):

    request_url = "{base}{endpoint}".format(
        base=STATUS_CAKE_BASE_URL, endpoint=endpoint)

    logger.debug("Starting request: {request_url} {endpoint} {params}".format(
        request_url=request_url,
        endpoint=endpoint,
        params=params))

    headers = {
        "API": apikey,
        "Username": username
    }

    response = requests.get(url=request_url, params=params, headers=headers)
    response.raise_for_status()

    return response
