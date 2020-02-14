#!/usr/bin/env python3

import logging
from .base import get

logger = logging.getLogger(__name__)


def get_maintenance(apikey, username, state="ACT"):
    endpoint = "Maintenance"
    params = {
        "state": state
    }

    response = get(apikey, username, endpoint, params)

    return response
