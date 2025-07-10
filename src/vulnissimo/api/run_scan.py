"""Contains methods for running a scan on a target with Vulnissimo"""

from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from .. import errors
from ..client import AuthenticatedClient, Client
from ..models import ExceptionResponseData, HTTPValidationError, ScanCreate, ScanCreated
from ..types import Response


def _get_kwargs(
    *,
    body: ScanCreate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/scans",
        "params": params,
    }

    _kwargs["json"] = body.model_dump(mode="json")

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[ExceptionResponseData, HTTPValidationError, ScanCreated]]:
    status_code = HTTPStatus(response.status_code)

    if status_code == HTTPStatus.CREATED:
        return ScanCreated(**response.json())

    if 400 <= status_code < 500:
        if status_code == HTTPStatus.BAD_REQUEST:
            data = ExceptionResponseData(**response.json())
            raise errors.BadRequestError(data)
        if status_code == HTTPStatus.UNAUTHORIZED:
            data = ExceptionResponseData(**response.json())
            raise errors.UnauthorizedError(data)
        if status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
            data = HTTPValidationError(**response.json())
            raise errors.UnprocessableEntityError(**response.json())

    if status_code >= 500:
        raise errors.ServerError(status_code, response.content)

    raise errors.UnexpectedStatusError(status_code, response.content)


def _build_response(*, response: httpx.Response) -> Response[ScanCreated]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ScanCreate,
) -> Response[ScanCreated]:
    """Start scan

     Create a scan on a given target

    Raises:
        errors.BadRequestError: If Vulnissimo returns 400 Bad Request.
        errors.UnauthorizedError: If Vulnissimo returns 401 Unauthorized.
        errors.UnprocessableEntityError: If Vulnissimo returns 422 Unprocessable Entity.
        errors.ServerError: If Vulnissimo returns a 5xx status code.
        errors.UnexpectedStatusError: If Vulnissimo returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ScanCreate,
) -> ScanCreated:
    """Start scan

     Create a scan on a given target

    Raises:
        errors.BadRequestError: If Vulnissimo returns 400 Bad Request.
        errors.UnauthorizedError: If Vulnissimo returns 401 Unauthorized.
        errors.UnprocessableEntityError: If Vulnissimo returns 422 Unprocessable Entity.
        errors.ServerError: If Vulnissimo returns a 5xx status code.
        errors.UnexpectedStatusError: If Vulnissimo returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ScanCreate,
) -> Response[ScanCreated]:
    """Start scan

     Create a scan on a given target

    Raises:
        errors.BadRequestError: If Vulnissimo returns 400 Bad Request.
        errors.UnauthorizedError: If Vulnissimo returns 401 Unauthorized.
        errors.UnprocessableEntityError: If Vulnissimo returns 422 Unprocessable Entity.
        errors.ServerError: If Vulnissimo returns a 5xx status code.
        errors.UnexpectedStatusError: If Vulnissimo returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: ScanCreate,
) -> ScanCreated:
    """Start scan

     Create a scan on a given target

    Raises:
        errors.BadRequestError: If Vulnissimo returns 400 Bad Request.
        errors.UnauthorizedError: If Vulnissimo returns 401 Unauthorized.
        errors.UnprocessableEntityError: If Vulnissimo returns 422 Unprocessable Entity.
        errors.ServerError: If Vulnissimo returns a 5xx status code.
        errors.UnexpectedStatusError: If Vulnissimo returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
