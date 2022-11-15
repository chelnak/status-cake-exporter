import logging
from typing import Any

import requests

logger = logging.getLogger("status_cake_legacy")


class PaymentRequiredException(Exception):
    pass


class NotFoundException(Exception):
    pass


class StatusCakeLegacyApiClient:
    def __init__(self, username: str, api_key: str) -> None:
        self.api_key = api_key
        self.username = username
        self.base_url = "https://app.statuscake.com/API/"

    def __get(self, endpoint: str, params: dict[str, str]) -> requests.Response:
        url = f"{self.base_url}{endpoint}"

        logger.debug(f"Fetching {url} with params: {params}")
        response = requests.get(url, auth=(self.username, self.api_key), params=params)
        response.raise_for_status()

        logger.debug(f"Response: {response.content}")
        return response

    def list_maintenance_windows(self) -> list[dict[str, Any]]:
        try:
            response: requests.Response = self.__get("Maintenance", {"state": "ACT"})
            return response.json()["data"]

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise NotFoundException(e)
            elif e.response.status_code == 402:
                raise PaymentRequiredException(e)

            raise e
