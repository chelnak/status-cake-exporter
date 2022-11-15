import json
import logging
from time import sleep
from typing import Any

from statuscake import ApiClient
from statuscake.apis import MaintenanceWindowsApi, UptimeApi
from statuscake.exceptions import ApiValueError, ForbiddenException
from typing_extensions import NotRequired, TypedDict

logger = logging.getLogger("status_cake")


# This keeps type checking happy
class ListUptimeTestParameters(TypedDict):
    page: int
    limit: int
    tags: NotRequired[str]


class StatusCake:
    def __init__(self, username: str, api_key: str, per_page: int) -> None:
        self.username: str = username
        self.api_key: str = api_key
        self.per_page: int = int(per_page)

    def __get_api_client(self) -> ApiClient:
        return ApiClient(
            header_name="Authorization",
            header_value=f"Bearer {self.api_key}",
        )

    def list_maintenance_windows(self) -> list[dict[str, Any]]:
        api_client = self.__get_api_client()

        try:
            maintenance_window_api: MaintenanceWindowsApi = MaintenanceWindowsApi(
                api_client
            )

            page = 1
            response = maintenance_window_api.list_maintenance_windows(
                page=page, limit=self.per_page
            )
            metadata = response["metadata"]
            logger.debug(
                f"Received {metadata['total_count']} tests across {metadata['page_count']} page(s)"
            )

            windows = response["data"]
            while page < metadata["page_count"]:
                page += 1
                logger.debug(f"Fetching page {page} of {metadata['page_count']}")
                paged_response = maintenance_window_api.list_maintenance_windows(
                    page=page, limit=self.per_page
                )
                windows.extend(paged_response["data"])

                sleep(1)

            return windows

        # TODO: Handle pre v1 maintenance api accounts gracefully
        # We should attempt to hit the v1 API first, and if that fails, fall back to the legacy API
        # but what exception should we catch here?

        except ForbiddenException as e:
            message = json.loads(e.body)["message"]
            if "Your current plan has no access to this feature" in message:
                logger.warn(
                    "Your current plan has no access to this feature. Skipping maintenance window check."
                )
                return []

            # re-raise here because it might be genuine.
            raise e

        except Exception as e:
            logger.error(f"Error while fetching maintenance windows: {e}")
            raise e

    def list_tests(self, tags: str = "") -> list[dict]:
        api_client = self.__get_api_client()

        try:
            uptime_api: UptimeApi = UptimeApi(api_client)

            params: ListUptimeTestParameters = {"page": 1, "limit": self.per_page}
            if tags:
                params["tags"] = tags

            logger.debug(f"params: {params}")
            response = uptime_api.list_uptime_tests(**params)

            metadata = response["metadata"]
            logger.debug(
                f"Received {metadata['total_count']} tests across {metadata['page_count']} page(s)"
            )

            tests = response["data"]
            while params["page"] < metadata["page_count"]:
                params["page"] += 1
                logger.debug(
                    f"Fetching page {params['page']} of {metadata['page_count']}"
                )
                paged_response = uptime_api.list_uptime_tests(**params)
                tests.extend(paged_response["data"])

                sleep(1)  # respect the API rate limit

            return tests

        # https://github.com/StatusCakeDev/statuscake-py/issues/8
        except ApiValueError as e:
            if "Invalid value for `total_count`" in str(e):
                logger.debug(f"No tests were found with the given tags '{tags}'.")
                return []

            raise e

        except Exception as e:
            logger.error(f"Error while fetching tests: {e}")
            raise e
