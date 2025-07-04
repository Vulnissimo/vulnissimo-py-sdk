"""Contains methods for getting a scan result from the Vulnissimo API"""

from http import HTTPStatus
from typing import Any, Union
from uuid import UUID

import httpx

from .. import errors
from ..client import AuthenticatedClient, Client
from ..models import ExceptionResponseData, HTTPValidationError, ScanResult
from ..types import Response


def _get_kwargs(
    scan_id: UUID,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params = {k: v for k, v in params.items() if v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": f"/scans/{scan_id}",
        "params": params,
    }

    return _kwargs


def _parse_response(*, response: httpx.Response) -> ScanResult:
    status_code = HTTPStatus(response.status_code)

    if status_code == HTTPStatus.OK:
        return ScanResult(**response.json())

    if 400 <= status_code < 500:
        if status_code == HTTPStatus.NOT_FOUND:
            data = ExceptionResponseData(**response.json())
            raise errors.NotFoundError(data)
        if status_code == HTTPStatus.UNPROCESSABLE_ENTITY:
            data = HTTPValidationError(**response.json())
            raise errors.UnprocessableEntityError(data)

    if status_code >= 500:
        raise errors.ServerError(status_code, response.content)

    raise errors.UnexpectedStatusError(status_code, response.content)


def _build_response(*, response: httpx.Response) -> Response[ScanResult]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    scan_id: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[ScanResult]:
    """
    Get scan result

     View a scan result by its ID

    Args:
        scan_id (UUID):

    Raises:
        errors.NotFoundError: If Vulnissimo returns 404 Not Found.
        errors.UnprocessableEntityError: If Vulnissimo returns 422 Unprocessable Entity.
        errors.ServerError: If Vulnissimo returns a 5xx status code.
        errors.UnexpectedStatusError: If Vulnissimo returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.
    """

    kwargs = _get_kwargs(
        scan_id=scan_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    scan_id: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
) -> ScanResult:
    """
    Get scan result

     View a scan result by its ID

    Raises:
        errors.NotFoundError: If Vulnissimo returns 404 Not Found.
        errors.UnprocessableEntityError: If Vulnissimo returns 422 Unprocessable Entity.
        errors.ServerError: If Vulnissimo returns a 5xx status code.
        errors.UnexpectedStatusError: If Vulnissimo returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.
    """

    return sync_detailed(
        scan_id=scan_id,
        client=client,
    ).parsed


async def asyncio_detailed(
    scan_id: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
) -> Response[ScanResult]:
    """
    Get scan result

     View a scan result by its ID

    Raises:
        errors.NotFoundError: If Vulnissimo returns 404 Not Found.
        errors.UnprocessableEntityError: If Vulnissimo returns 422 Unprocessable Entity.
        errors.ServerError: If Vulnissimo returns a 5xx status code.
        errors.UnexpectedStatusError: If Vulnissimo returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.
    """

    kwargs = _get_kwargs(
        scan_id=scan_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(response=response)


async def asyncio(
    scan_id: UUID,
    *,
    client: Union[AuthenticatedClient, Client],
) -> ScanResult:
    """
    Get scan result

     View a scan result by its ID

    Raises:
        errors.NotFoundError: If Vulnissimo returns 404 Not Found.
        errors.UnprocessableEntityError: If Vulnissimo returns 422 Unprocessable Entity.
        errors.ServerError: If Vulnissimo returns a 5xx status code.
        errors.UnexpectedStatusError: If Vulnissimo returns an undocumented status code.
        httpx.TimeoutException: If the request takes longer than Client.timeout.
    """

    return (
        await asyncio_detailed(
            scan_id=scan_id,
            client=client,
        )
    ).parsed
