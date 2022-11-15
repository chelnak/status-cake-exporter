import json
import logging
from time import sleep

from statuscake import ApiClient
from statuscake.apis import MaintenanceWindowsApi, UptimeApi
from statuscake.exceptions import ForbiddenException

logger = logging.getLogger("status_cake")


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

    def list_maintenance_windows(self):
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

        # TODO: Handle pre v1 maintenance api accounts gracefullyv

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

    def list_tests(self) -> list[dict]:
        api_client = self.__get_api_client()

        try:
            uptime_api: UptimeApi = UptimeApi(api_client)

            page = 1
            response = uptime_api.list_uptime_tests(page=page, limit=self.per_page)
            metadata = response["metadata"]
            logger.debug(
                f"Received {metadata['total_count']} tests across {metadata['page_count']} page(s)"
            )

            tests = response["data"]
            while page < metadata["page_count"]:
                page += 1
                logger.debug(f"Fetching page {page} of {metadata['page_count']}")
                paged_response = uptime_api.list_uptime_tests(
                    page=page, limit=self.per_page
                )
                tests.extend(paged_response["data"])

                sleep(1)  # respect the API rate limit

            return tests

        except Exception as e:
            logger.error(f"Error while fetching tests: {e}")
            raise e
