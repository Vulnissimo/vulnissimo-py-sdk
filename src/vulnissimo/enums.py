"""Enums used throughout the package"""

from enum import Enum


class ScanResultOutputType(Enum):
    """All possible output types for a scan result"""

    PRETTY = "pretty"
    JSON = "json"
