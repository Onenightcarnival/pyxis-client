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

    def _make_request(
        self,
        method: str,
        endpoint: str,
        response_handler: Callable,
        func: Callable,
        *args, **kwargs
    ):
        sig = inspect.signature(func)
        hints = get_type_hints(func)
        return_type = hints.get("return")

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

        response = self.client.request(
            method=method,
            url=urljoin(self.base_url, endpoint.format(**path_params)),
            params=query_params,
            headers=headers,
            json=body
        )

        if response_handler:
            response_handler(response)

        data = response.json()
        if return_type:
            # List[Model]
            if getattr(return_type, '__origin__', None) is list:
                model_type = return_type.__args__[0]
                return [model_type.parse_obj(item) for item in data]
            # Single Model
            else:
                return return_type.parse_obj(data)

        return data

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
