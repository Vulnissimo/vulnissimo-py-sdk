"""The Vulnissimo client"""

import time

from pydantic import AnyUrl

from .api import get_scan_result, run_scan
from .client import AuthenticatedClient, Client
from .models import ScanCreate, ScanResult, ScanStatus, ScanType

VULNISSIMO_BASE_URL = "https://api.vulnissimo.io"


class Vulnissimo:
    """The Vulnissimo client"""

    def __init__(self, api_token: str | None = None):
        self.api_token = api_token

    def __is_authenticated(self):
        return self.api_token is not None

    def __get_client(self):
        if self.__is_authenticated():
            return AuthenticatedClient(VULNISSIMO_BASE_URL, self.api_token)
        return Client(VULNISSIMO_BASE_URL)

    def run_scan(
        self,
        target: str,
        type: ScanType | None = ScanType.PASSIVE,
        is_private: bool | None = None,
    ) -> ScanResult:
        """
        Run a scan with Vulnissimo and wait for it to finish.

        Parameters:
            target (str): the URL to scan
            type (ScanType): the scan type, either Passive or Active
            is_private: whether the scan will or will not be visible in the Vulnissimo web platform.
                If not set, then it will be set to `True` if you have initialized Vulnissimo with an
                API token, otherwise it will be set to `False`.
        """

        if is_private is None:
            is_private = self.__is_authenticated()

        body = ScanCreate(target=AnyUrl(target), type=type, is_private=is_private)
        scan = None

        with self.__get_client() as client:
            created_scan = run_scan.sync(client=client, body=body)

            while True:
                scan = get_scan_result.sync(scan_id=created_scan.id, client=client)
                if scan.scan_info.status == ScanStatus.FINISHED:
                    break

                time.sleep(2)

            return scan

    def start_scan(
        self,
        target: str,
        type: ScanType | None = ScanType.PASSIVE,
        is_private: bool | None = None,
    ) -> ScanResult:
        """
        Start a scan with Vulnissimo.

        Parameters:
            target (str): the URL to scan
            type (ScanType): the scan type, either Passive or Active
            is_private: whether the scan will or will not be visible in the Vulnissimo web platform.
                If not set, then it will be set to `True` if you have initialized Vulnissimo with an
                API token, otherwise it will be set to `False`.
        """

        if is_private is None:
            is_private = self.__is_authenticated()

        body = ScanCreate(target=AnyUrl(target), type=type, is_private=is_private)

        with self.__get_client() as client:
            created_scan = run_scan.sync(client=client, body=body)
            return get_scan_result.sync(scan_id=created_scan.id, client=client)

    def poll(self, scan: ScanResult) -> ScanResult:
        """Fetch new data for a scan."""

        with self.__get_client() as client:
            return get_scan_result.sync(scan_id=scan.id, client=client)
