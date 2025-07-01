"""Custom exceptions thrown by the API client."""


class StartScanException(Exception):
    def __init__(self, status_code: int, error_msg: str):
        self.status_code = status_code
        self.error_msg = error_msg
