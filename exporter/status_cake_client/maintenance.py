#!/usr/bin/env python3

import logging
import requests
import sys

from .base import get

logger = logging.getLogger(__name__)


def get_maintenance(use_v1_maintenance_windows_endpoints, apikey, username):
    if use_v1_maintenance_windows_endpoints:
        endpoint = "maintenance-windows"
        params = {
        "state": "active"
    }
    else:
        endpoint = "Maintenance"
        params = {
        "state": "ACT"
    }

    try:
        response = get(use_v1_maintenance_windows_endpoints, apikey, username, endpoint, params)
    except requests.exceptions.HTTPError as e:
        if not(use_v1_maintenance_windows_endpoints) and e.response.status_code == 404:
            logger.info("Currently no active maintenance.")
            response = e.response
        else:
            logger.error(e)
            sys.exit(1)

    logger.debug(f"Request response:\n{response.content}")
    return response
