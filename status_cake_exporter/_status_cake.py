import json
import logging

from statuscake import ApiClient
from statuscake.apis import MaintenanceWindowsApi, UptimeApi
from statuscake.exceptions import ForbiddenException

logger = logging.getLogger(__name__)


class StatusCake:
    def __init__(self, username: str, api_key: str) -> None:
        self.username: str = username
        self.api_key: str = api_key

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
            maintenance_windows = (
                maintenance_window_api.list_maintenance_windows()
            )  # TODO: add pagination
            return maintenance_windows

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
            raise e

    def list_tests(self) -> list[dict]:
        api_client = self.__get_api_client()

        try:
            uptime_api: UptimeApi = UptimeApi(api_client)
            tests = uptime_api.list_uptime_tests()  # TODO: add pagination
            return tests["data"]

        except Exception as e:
            raise e
