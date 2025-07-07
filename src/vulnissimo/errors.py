"""Contains shared errors types that can be raised from API functions"""

from http import HTTPStatus

from pydantic import BaseModel

from .models import ExceptionResponseData


class APIError(Exception):
    """Base class for errors returned by the Vulnissimo API"""

    def __init__(self, status_code: HTTPStatus, *args):
        self.status_code = status_code

        super().__init__(*args)


class ClientError(APIError):
    """Base class for when a call to the Vulnissimo API returns a 4xx status code"""

    def __init__(self, status_code: HTTPStatus, data: BaseModel, *args):
        self.data = data

        super().__init__(status_code, *args)


class BadRequestError(ClientError):
    """Raised when a call to the Vulnissimo API returns 400 Bad Request"""

    def __init__(self, data: ExceptionResponseData):
        super().__init__(
            HTTPStatus.BAD_REQUEST,
            data,
            f"API Error: 400 Bad Request\nResponse data: {data.model_dump_json()}",
        )


class UnauthorizedError(ClientError):
    """Raised when a call to the Vulnissimo API returns 401 Unauthorized"""

    def __init__(self, data: ExceptionResponseData):
        super().__init__(
            HTTPStatus.UNAUTHORIZED,
            data,
            f"API Error: 401 Unauthorized\nResponse data: {data.model_dump_json()}",
        )


class NotFoundError(ClientError):
    """Raised when a call to the Vulnissimo API returns 404 Not Found"""

    def __init__(self, data: ExceptionResponseData):
        super().__init__(
            HTTPStatus.NOT_FOUND,
            data,
            f"API Error: 404 Not Found\nResponse data: {data.model_dump_json()}",
        )


class UnprocessableEntityError(ClientError):
    """Raised when a call to the Vulnissimo API returns 422 Unprocessable Entity"""

    def __init__(self, data: ExceptionResponseData):
        super().__init__(
            HTTPStatus.NOT_FOUND,
            data,
            f"API Error: 422 Unprocessable Entity\nResponse data: {data.model_dump_json()}",
        )


class UnexpectedStatusError(APIError):
    """Raised when a call to the Vulnissimo API returns an undocumented status code"""

    def __init__(self, status_code: HTTPStatus, data: bytes):
        self.data = data

        super().__init__(
            status_code,
            f"Unexpected API Client error\n\nStatus code: {status_code}\n\nResponse data:\n{data.decode()}",
        )


class ServerError(APIError):
    """Raised when a call to the Vulnissimo API returns a 5xx status code"""

    def __init__(self, status_code: HTTPStatus, data: bytes):
        self.data = bytes

        super().__init__(
            status_code,
            f"API Server error\n\nStatus code: {status_code}\n\nResponse data:\n{data.decode()}",
        )


__all__ = [
    "ClientError",
    "NotFoundError",
    "UnprocessableEntityError",
    "UnexpectedStatusError",
    "ServerError",
]
