import inspect
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Dict, get_type_hints, Union
from urllib.parse import urljoin

import httpx

from src.annotations import Body, BodyMap, Header, HeaderMap, Path, Query, QueryMap


@dataclass
class RequestContent:
    path: Dict[str, str]
    query: Dict[str, str]
    headers: Dict[str, str]
    body: Dict[str, Any]
    url: str


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
    ) -> RequestContent:
        sig = inspect.signature(func)

        content = RequestContent(
            path=dict(),
            query=dict(),
            headers=self._get_default_headers(),
            body=dict(),
            url=str()
        )

        bound_args = sig.bind(self, *args, **kwargs)
        bound_args.apply_defaults()

        for param_name, param_value in bound_args.arguments.items():
            if param_name == "self":
                continue

            param_type = sig.parameters[param_name].annotation

            if param_type == Path:
                content.path[param_value.alias or param_name] = param_value.value
            elif param_type == Query:
                content.query[param_value.alias or param_name] = param_value.value
            elif param_type == Header:
                content.headers[param_value.alias or param_name] = param_value.value
            elif param_type == Body:
                content.body[param_value.alias or param_name] = param_value.value

            if param_type == QueryMap:
                content.query.update(param_value.value)
            elif param_type == HeaderMap:
                content.headers.update(param_value.value)
            elif param_type == BodyMap:
                content.body.update(param_value.value)

        content.url = urljoin(self.base_url, endpoint.format(**content.path))

        return content

    def _send_request(
        self,
        method: str,
        content: RequestContent,
    ) -> httpx.Response:
        response = self.client.request(
            method=method,
            url=content.url,
            params=content.query,
            headers=content.headers,
            json=content.body
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
        content = self._prepare_request_data(func, endpoint, *args, **kwargs)
        response = self._send_request(method, content)
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
