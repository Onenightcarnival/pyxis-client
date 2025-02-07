from functools import wraps
from typing import Callable, Dict, Union

import httpx

from src.client import BaseClient


class AsyncClient(BaseClient):
    """
    Async declarative REST client based on httpx
    """

    def __init__(
        self,
        base_url: str,
        encoding: str = "utf-8",
        default_headers: Dict[str, Union[str, Callable]] = None,
        *args, **kwargs
    ):
        super().__init__(
            base_url=base_url,
            encoding=encoding,
            default_headers=default_headers,
            *args, **kwargs
        )
        self.async_client = httpx.AsyncClient(*args, **kwargs)

    async def _send_async_request(
        self,
        method: str,
        url: str,
        headers: dict,
        query_params: dict,
        body: dict
    ) -> httpx.Response:
        response = await self.async_client.request(
            method=method,
            url=url,
            params=query_params,
            headers=headers,
            json=body
        )
        return response

    async def _make_async_request(
        self,
        method: str,
        endpoint: str,
        response_handler: Callable,
        func: Callable,
        *args, **kwargs
    ):
        """
        prepare -> send -> handle
        """
        url, headers, query_params, body = self._prepare_request_data(
            func, endpoint, *args, **kwargs
        )

        response = await self._send_async_request(method, url, headers, query_params, body)

        return self._handle_response(response, func, response_handler)

    @classmethod
    def async_get(cls, endpoint: str, response_handler: Callable = None):
        """
        Async Decorator for HTTP GET methods
        """

        def decorator(func):
            @wraps(func)
            async def wrapper(self, *args, **kwargs):
                return await self._make_async_request(
                    "GET", endpoint, response_handler, func, *args, **kwargs
                )

            return wrapper

        return decorator

    @classmethod
    def async_post(cls, endpoint: str, response_handler: Callable = None):
        """
        Async Decorator for HTTP POST methods
        """

        def decorator(func):
            @wraps(func)
            async def wrapper(self, *args, **kwargs):
                return await self._make_async_request(
                    "POST", endpoint, response_handler, func, *args, **kwargs
                )

            return wrapper

        return decorator

    @classmethod
    def async_put(cls, endpoint: str, response_handler: Callable = None):
        """
        Async Decorator for HTTP PUT methods
        """

        def decorator(func):
            @wraps(func)
            async def wrapper(self, *args, **kwargs):
                return await self._make_async_request(
                    "PUT", endpoint, response_handler, func, *args, **kwargs
                )

            return wrapper

        return decorator

    @classmethod
    def async_delete(cls, endpoint: str, response_handler: Callable = None):
        """
        Async Decorator for HTTP DELETE methods
        """

        def decorator(func):
            @wraps(func)
            async def wrapper(self, *args, **kwargs):
                return await self._make_async_request(
                    "DELETE", endpoint, response_handler, func, *args, **kwargs
                )

            return wrapper

        return decorator
