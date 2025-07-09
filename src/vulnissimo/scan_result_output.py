"""Classes and functions for outputting a scan result"""

import json
from abc import ABC, abstractmethod

from rich.prompt import Prompt

from .console import console, error_console
from .enums import ScanResultOutputType
from .models import ScanResult


class Outputter(ABC):
    """Output the result of a scan"""

    @abstractmethod
    def output(self, scan_result: ScanResult) -> None:
        """Output the result of a scan"""


class JsonConsoleOutputter(Outputter):
    """Output the result of a scan to the console in JSON format"""

    def __init__(self, indent: int):
        self.indent = indent

    def output(self, scan_result: ScanResult) -> None:
        console.print_json(scan_result.model_dump_json(), indent=self.indent)


class PrettyConsoleOutputter(Outputter):
    """Output the result of a scan to the console in Pretty format"""

    def output(self, scan_result: ScanResult) -> None:
        console.print("[yellow]NOT IMPLEMENTED[/yellow]")


class JsonFileOutputter(Outputter):
    """Output the result of a scan to a file in JSON format"""

    def __init__(self, output_file: str, indent: int):
        self.output_file = output_file
        self.indent = indent

    def output(self, scan_result: ScanResult) -> None:
        while True:
            try:
                with open(self.output_file, "w+", encoding="UTF-8") as f:
                    json.dump(
                        scan_result.model_dump(mode="json"), f, indent=self.indent
                    )
                console.print(f"Scan result was written to {self.output_file}.")
                return
            except PermissionError as e:
                error_console.print(f"Could not open file for writing: {e.strerror}.")
                self.output_file = Prompt.ask(
                    "Enter another file name for writing"
                    " (or leave empty to write the scan result to the console)"
                )


class PrettyFileOutputter(Outputter):
    """Output the result of a scan to a file in Pretty format"""

    def __init__(self, output_file: str):
        self.output_file = output_file

    def output(self, scan_result: ScanResult) -> None:
        console.print("[yellow]NOT IMPLEMENTED[/yellow]")


class OutputterFactory:
    """Factory for an `Outputter`"""

    def create_outputter(
        self,
        output_file: str | None,
        output_type: ScanResultOutputType,
        indent: int,
    ) -> Outputter:
        """Obtain an `Outputter`"""

        if output_file is None:
            if output_type == ScanResultOutputType.JSON:
                return JsonConsoleOutputter(indent)
            elif output_type == ScanResultOutputType.PRETTY:
                return PrettyConsoleOutputter()
        else:
            if output_type == ScanResultOutputType.JSON:
                return JsonFileOutputter(output_file, indent)
            elif output_type == ScanResultOutputType.PRETTY:
                return PrettyFileOutputter(output_file)


def output_scan(
    scan_result: ScanResult,
    output_file: str | None,
    output_type: ScanResultOutputType,
    indent: int,
):
    """
    If `output_file` is provided, write the scan to `output_file`. Else, print it to the console
    """

    factory = OutputterFactory()
    outputter = factory.create_outputter(output_file, output_type, indent)
    outputter.output(scan_result)
