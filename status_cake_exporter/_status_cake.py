import json
import logging
from time import sleep
from typing import Any

from statuscake import ApiClient
from statuscake.apis import MaintenanceWindowsApi, UptimeApi
from statuscake.exceptions import ApiValueError, ForbiddenException
from typing_extensions import NotRequired, TypedDict

from ._status_cake_legacy import (
    NotFoundException,
    PaymentRequiredException,
    StatusCakeLegacyApiClient,
)

logger = logging.getLogger("status_cake")


# The default set of parameters used for pagination
class DefaultPaginationParameters(TypedDict):
    page: int
    limit: int


# A generic type that is used as a hint for pagination args
# Consumers would inherit this type and add their own api parameters
class PaginationParameters(TypedDict):
    pass


# Parameters expected by the StatusCake API uptime endpoint
class ListUptimeTestParameters(PaginationParameters):
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

    def __get_legacy_api_client(self) -> StatusCakeLegacyApiClient:
        return StatusCakeLegacyApiClient(
            self.username,
            self.api_key,
        )

    def __list_legacy_mainenance_windows(self) -> list[dict[str, Any]]:
        api_client = self.__get_legacy_api_client()

        try:
            response: list[dict[str, Any]] = api_client.list_maintenance_windows()
            return response
        except PaymentRequiredException:
            logger.warn(
                "Your current plan has no access to this feature. Skipping maintenance window check."
            )
            return []

        except NotFoundException:
            logger.debug("No maintenance windows recieved.")
            return []

    def __paginate_response(
        self, func: Any, args: PaginationParameters | None
    ) -> list[dict[str, Any]]:
        params: DefaultPaginationParameters = {"page": 1, "limit": self.per_page}
        args = args | params if args else params

        response = func(**params)
        metadata = response["metadata"]
        logger.debug(
            f"Received {metadata['total_count']} tests across {metadata['page_count']} page(s)"
        )

        data = response["data"]
        while params["page"] < metadata["page_count"]:
            params["page"] += 1
            logger.debug(f"Fetching page {params['page']} of {metadata['page_count']}")
            paged_response = func(**params)
            data.extend(paged_response["data"])

            sleep(1)

        return data

    def list_maintenance_windows(self) -> list[dict[str, Any]]:
        api_client = self.__get_api_client()

        try:
            maintenance_window_api: MaintenanceWindowsApi = MaintenanceWindowsApi(
                api_client
            )

            response = self.__paginate_response(
                maintenance_window_api.list_maintenance_windows,
                None,
            )
            return response

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
            params = ListUptimeTestParameters(tags=tags) if tags else None
            response = self.__paginate_response(
                uptime_api.list_uptime_tests,
                params,
            )
            return response

        # https://github.com/StatusCakeDev/statuscake-py/issues/8
        except ApiValueError as e:
            if "Invalid value for `total_count`" in str(e):
                logger.debug(f"No tests were found with the given tags '{tags}'.")
                return []

            raise e

        except Exception as e:
            logger.error(f"Error while fetching tests: {e}")
            raise e
