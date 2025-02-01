from typing import Any, Callable, Dict, Union


class Header:
    """
    Header parameter annotation
    """
    pass


class Path:
    """
    Path parameter annotation
    """
    pass


class Query:
    """
    Query parameter annotation
    """
    pass


class Body:
    """
    Body parameter annotation
    """
    pass


class BaseClient:
    """
    Sync declarative REST client based on httpx
    """

    def __init__(
        self,
        base_url: str,
        encoding: str = "utf-8",
        default_headers: Dict[str, Union[str, Callable]] = None
    ):
        self.base_url = base_url
        self.encoding = encoding
        self.default_headers = default_headers

    def _extract_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        pass

    def _extract_body(self, body: Dict[str, Any]) -> Dict[str, str]:
        pass

    def _extract_query(self, query: Dict[str, str]) -> Dict[str, str]:
        pass

    def _extract_path(self, path: Dict[str, str]) -> Dict[str, str]:
        pass

    def _make_request(self):
        pass

    @classmethod
    def get(
        cls,
        endpoint: str,
        response_handler: Callable = None
    ):
        """
        Decorator for HTTP GET requests that converts response body to Pydantic models
        """
        pass

    @classmethod
    def post(
        cls,
        endpoint: str,
        response_handler: Callable = None
    ):
        """
        Decorator for HTTP POST requests that converts response to Pydantic models
        """
        pass

    @classmethod
    def put(
        cls,
        endpoint: str,
        response_handler: Callable = None
    ):
        """
        Decorator for HTTP PUT requests that converts response to Pydantic models
        """
        pass

    @classmethod
    def delete(
        cls,
        endpoint: str,
        response_handler: Callable = None
    ):
        """
        Decorator for HTTP DELETE requests that converts response to Pydantic models
        """
        pass
