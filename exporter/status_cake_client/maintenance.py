#!/usr/bin/env python3

import logging
import requests
import sys

from .base import get

logger = logging.getLogger(__name__)


def get_maintenance(apikey, username, state="ACT"):
    endpoint = "Maintenance"
    params = {
        "state": state
    }

    try:
        response = get(apikey, username, endpoint, params)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            logger.info("Currently no active maintenance.")
            response = e.response
        else:
            logger.error(e)
            sys.exit(1)

    logger.debug(f"Request response:\n{response.content}")
    return response
