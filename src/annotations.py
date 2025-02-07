from typing import Any, Dict


class Header:
    """
    Header parameter annotation
    """

    def __init__(self, value: str, *, alias: str = None):
        self.value = value
        self.alias = alias


class Path:
    """
    Path parameter annotation
    """

    def __init__(self, value: str, *, alias: str = None):
        self.value = value
        self.alias = alias


class Query:
    """
    Query parameter annotation
    """

    def __init__(self, value: str, *, alias: str = None):
        self.value = value
        self.alias = alias


class Body:
    """
    Body parameter annotation
    """

    def __init__(self, value: str, *, alias: str = None):
        self.value = value
        self.alias = alias


class HeaderMap:
    """
    Header parameters annotation
    """

    def __init__(self, value: Dict[str, str]):
        self.value = value


class QueryMap:
    """
    Query parameters annotation
    """

    def __init__(self, value: Dict[str, str]):
        self.value = value


class BodyMap:
    """
    Body parameters annotation
    """

    def __init__(self, value: Dict[str, Any]):
        self.value = value
