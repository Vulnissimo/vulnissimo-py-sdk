"""Contains some shared types for properties"""

from collections.abc import MutableMapping
from http import HTTPStatus
from typing import Generic, Optional, TypeVar

from attrs import define

T = TypeVar("T")


@define
class Response(Generic[T]):
    """A response from an endpoint"""

    status_code: HTTPStatus
    content: bytes
    headers: MutableMapping[str, str]
    parsed: Optional[T]


__all__ = ["Response"]
