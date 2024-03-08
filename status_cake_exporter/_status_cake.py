import json
import logging
from time import sleep
from typing import Any

from statuscake import ApiClient, Configuration
from statuscake.apis import MaintenanceWindowsApi, UptimeApi
from statuscake.exceptions import ApiValueError, ForbiddenException, ApiException
from typing_extensions import NotRequired, TypedDict

logger = logging.getLogger("status_cake")


class DefaultPaginationParameters(TypedDict):
    """The default set of parameters used for pagination"""

    page: int
    limit: int


class PaginationParameters(TypedDict):
    """
    A generic type that is used as a hint for pagination args
    Consumers would inherit this type and add their own api parameters
    """

    pass


class ListUptimeTestParameters(PaginationParameters):
    """Parameters expected by the StatusCake API uptime endpoint"""

    tags: NotRequired[str]


class ListUptimeTestHistoryParameters(PaginationParameters):
    """Parameters expected by the StatusCake API uptime history endpoint"""

    limit: NotRequired[int]


class StatusCake:
    """
    A wrapper class for the StatusCake API client.
    """

    def __init__(self, host: str, api_key: str, per_page: int) -> None:
        """
        Args:
            host: [str] The host of the StatusCake API
            api_key: [str] The StatusCake API key
            per_page: [int] The number of results to return per page
        """
        self.host: str = host
        self.api_key: str = api_key
        self.per_page: int = int(per_page)

    def __get_api_client(self) -> ApiClient:
        """
        Returns an instance of the StatusCake API client

        Returns:
            ApiClient
        """
        return ApiClient(
            Configuration(host=self.host),
            header_name="Authorization",
            header_value=f"Bearer {self.api_key}",
        )

    def __paginate_response(
        self, func: Any, args: PaginationParameters | None
    ) -> list[dict[str, Any]]:
        """
        A helper function that will paginate through the response of a given function.

        Args:
            func: [Any] The function to call
            args: [PaginationParameters | None] The arguments to pass to the function

        Returns:
            list[dict[str, Any]]
        """
        params: DefaultPaginationParameters = {"page": 1, "limit": self.per_page}
        params = args | params if args else params

        def __retry_backoff(func, **kwargs):
            try:
                return func(**kwargs)
            except ApiException as e:
                if e.status == 429:
                    backoff=int(e.headers["x-ratelimit-reset"])
                    logger.debug(f"Hit statuscake API rate limit. Waiting {backoff} seconds before retrying...")
                    sleep(backoff)
                    return __retry_backoff(func, **kwargs)
                raise e

        response = __retry_backoff(func,**params)
        metadata = response["metadata"]
        logger.debug(
            f"Received {metadata['total_count']} tests across {metadata['page_count']} page(s)"
        )

        data = response["data"]
        while params["page"] < metadata["page_count"]:
            params["page"] += 1
            logger.debug(f"Fetching page {params['page']} of {metadata['page_count']}")
            paged_response = __retry_backoff(func,**params)
            data.extend(paged_response["data"])

            sleep(1)

        return data

    def list_maintenance_windows(self) -> list[dict[str, Any]]:
        """
        Returns a list of maintenance windows

        Returns:
            list[dict[str, Any]]

        Raises:
            Exception: If an error occurs while fetching the maintenance windows
            ForbiddenException: If the API key does not have the required permissions
            ApiValueError: If the API receives an invalid value
        """
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

        except ForbiddenException as e:
            if e.body:
                message = json.loads(e.body)["message"]
                if (
                    message
                    and "Your current plan has no access to this feature" in message
                ):
                    logger.warn(
                        (
                            "Your current plan has no access to this feature or your account is "
                            "using legacy maintenance windows. Skipping maintenance window check."
                        )
                    )
                    return []

            # re-raise here because it might be genuine.
            raise e

        except ApiValueError as e:
            if "Invalid value for `total_count`" in str(e):
                logger.debug(f"No maintenance windows were found: {e}.")
                return []

            raise e

        except Exception as e:
            logger.error(f"Error while fetching maintenance windows: {e}")
            raise e

    def list_tests(self, tags: str = "", enable_perf_metrics: bool = False) -> list[dict]:
        """
        Returns a list of tests

        Args:
            tags: [str] A comma separated list of tags to filter by.
            enable_perf_metrics: [bool] Enable collection of performance data.

        Returns:
            list[dict[str, Any]]

        Raises:
            Exception: If an error occurs while fetching the tests
            ApiValueError: If the tags parameter is invalid
        """
        api_client = self.__get_api_client()

        try:
            uptime_api: UptimeApi = UptimeApi(api_client)
            params = ListUptimeTestParameters(tags=tags) if tags else None
            response = self.__paginate_response(
                uptime_api.list_uptime_tests,
                params,
            )

            # Fetch the performance of each test and add it to the response
            if enable_perf_metrics:
                for test in response:
                    history = self.get_test_history(test["id"])
                    if history["data"]:
                        test["performance"] = history["data"][0]["performance"]
                    else:
                        logger.warning(f"No performance data found for test ID {test['id']}")

            logger.debug(response)
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

    def get_test_history(self, test_id: str) -> list[dict[str, Any]]:
        """
        Returns the history of a test

        Args:
            test_id: [str] The ID of the test

        Returns:
            list[dict[str, Any]]

        Raises:
            Exception: If an error occurs while fetching the test history
        """
        api_client = self.__get_api_client()

        try:
            uptime_api: UptimeApi = UptimeApi(api_client)
            params = ListUptimeTestHistoryParameters(limit=1)
            response = uptime_api.list_uptime_test_history(test_id, **params)
            return response

        except ApiException as e:
            if e.status == 429:
                backoff=int(e.headers["x-ratelimit-reset"])
                logger.debug(f"Hit statuscake API rate limit. Waiting {backoff} seconds before retrying...")
                sleep(backoff)
                return uptime_api.list_uptime_test_history(test_id, **params)

            raise e
        except Exception as e:
            logger.error(f"Error while fetching test history: {e}")
            raise e
