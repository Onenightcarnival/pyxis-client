import inspect
from functools import wraps
from typing import Callable, Dict, get_type_hints, Union
from urllib.parse import urljoin

import httpx


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
        default_headers: Dict[str, Union[str, Callable]] = None,
        *args, **kwargs
    ):
        self.base_url = base_url
        self.encoding = encoding
        self.default_headers = default_headers or dict()
        self.client = httpx.Client(*args, **kwargs)

    def _get_default_headers(self) -> Dict[str, str]:
        headers = dict()
        for key, value in self.default_headers.items():
            headers[key] = value() if callable(value) else value
        return headers

    def _prepare_request_data(
        self,
        func: Callable,
        endpoint: str,
        *args, **kwargs
    ):
        sig = inspect.signature(func)

        path_params = dict()
        query_params = dict()
        headers = self._get_default_headers()
        body = None

        bound_args = sig.bind(self, *args, **kwargs)
        bound_args.apply_defaults()

        for param_name, param_value in bound_args.arguments.items():
            if param_name == "self":
                continue

            param_type = sig.parameters[param_name].annotation
            if param_type == Path:
                path_params[param_name] = param_value
            elif param_type == Query:
                query_params[param_name] = param_value
            elif param_type == Header:
                headers[param_name] = param_value
            elif param_type == Body:
                body = param_value

        url = urljoin(self.base_url, endpoint.format(**path_params))

        return url, headers, query_params, body

    def _send_request(
        self,
        method: str,
        url: str,
        headers: dict,
        query_params: dict,
        body: dict
    ) -> httpx.Response:
        response = self.client.request(
            method=method,
            url=url,
            params=query_params,
            headers=headers,
            json=body
        )
        return response

    @staticmethod
    def _handle_response(
        response: httpx.Response,
        func: Callable,
        response_handler: Callable
    ):
        if response_handler:
            response_handler(response)

        data = response.json()

        hints = get_type_hints(func)
        return_type = hints.get("return")

        if return_type:
            # List[Model]（e.g. List[Repo]）
            if getattr(return_type, '__origin__', None) is list:
                model_type = return_type.__args__[0]
                return [model_type.parse_obj(item) for item in data]
            else:
                # Model.parse_obj(data)
                return return_type.parse_obj(data)
        return data

    def _make_request(
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

        response = self._send_request(method, url, headers, query_params, body)

        return self._handle_response(response, func, response_handler)

    @classmethod
    def get(cls, endpoint: str, response_handler: Callable = None):
        """
        Decorator for HTTP GET methods
        """

        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                return self._make_request(
                    "GET", endpoint, response_handler, func, *args, **kwargs
                )

            return wrapper

        return decorator

    @classmethod
    def post(cls, endpoint: str, response_handler: Callable = None):
        """
        Decorator for HTTP POST methods
        """

        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                return self._make_request(
                    "POST", endpoint, response_handler, func, *args, **kwargs
                )

            return wrapper

        return decorator

    @classmethod
    def put(cls, endpoint: str, response_handler: Callable = None):
        """
        Decorator for HTTP PUT methods
        """

        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                return self._make_request(
                    "PUT", endpoint, response_handler, func, *args, **kwargs
                )

            return wrapper

        return decorator

    @classmethod
    def delete(cls, endpoint: str, response_handler: Callable = None):
        """
        Decorator for HTTP DELETE methods
        """

        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                return self._make_request(
                    "DELETE", endpoint, response_handler, func, *args, **kwargs
                )

            return wrapper

        return decorator


class AsyncBaseClient(BaseClient):
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
        self.client = httpx.AsyncClient(*args, **kwargs)

    async def _send_async_request(
        self,
        method: str,
        url: str,
        headers: dict,
        query_params: dict,
        body: dict
    ) -> httpx.Response:
        response = await self.client.request(
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
