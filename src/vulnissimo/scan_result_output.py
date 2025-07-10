"""Classes and functions for outputting a scan result"""

import json
from abc import ABC, abstractmethod
from datetime import timezone
from uuid import UUID

from rich.columns import Columns
from rich.console import Console, Group
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from .console import default_console, error_console
from .enums import ScanResultOutputType
from .models import Recon, RiskLevel, ScanInfo, ScanResult, ScanStatus, Vulnerability


class Outputter(ABC):
    """Output the result of a scan"""

    @abstractmethod
    def output(self, scan_result: ScanResult) -> None:
        """Output the result of a scan"""

    def _get_color_by_risk_level(self, risk_level: RiskLevel) -> str:
        if risk_level == RiskLevel.CRITICAL:
            return "red"
        if risk_level == RiskLevel.HIGH:
            return "dark_orange"
        if risk_level == RiskLevel.MEDIUM:
            return "yellow1"
        if risk_level == RiskLevel.LOW:
            return "dodger_blue2"
        return "green"


class PrettyOutputter(Outputter):
    """Output the result of a scan in pretty format"""

    def _get_scan_info_panel(self, scan_info: ScanInfo, scan_id: UUID) -> Panel:
        scan_risk_level = scan_info.risk_level

        scan_info_table = Table(show_header=False, box=None, highlight=True)
        scan_info_table.add_column(justify="right")
        scan_info_table.add_column()

        scan_info_table.add_row(
            "Target",
            (
                str(scan_info.target)
                + (" (redirect)" if scan_info.redirect_url is not None else "")
            ),
        )
        scan_info_table.add_row(
            "Scanned target",
            str(scan_info.redirect_url) or str(scan_info.target),
        )
        scan_info_table.add_row(
            "Started at",
            scan_info.created_at.replace(tzinfo=timezone.utc)
            .astimezone()
            .strftime("%Y-%m-%d %H:%M:%S %Z"),
        )
        scan_info_table.add_row(
            "Status",
            Text(
                scan_info.status.value.capitalize()
                + (
                    f" ({scan_info.progress}%)"
                    if scan_info.status == ScanStatus.RUNNING
                    else ""
                ),
                style=None,
            ),
        )
        scan_info_table.add_row(
            "Overall risk level",
            Text(
                scan_risk_level.value.capitalize(),
                style=self._get_color_by_risk_level(scan_risk_level),
            ),
        )
        scan_info_table.add_row("Type", scan_info.type.value.capitalize())
        scan_info_table.add_row(
            "Visibility", "Private" if scan_info.is_private else "Public"
        )
        scan_info_table.add_row("Scan ID", str(scan_id))

        return Panel(scan_info_table, title="Scan Info", expand=False)

    def _get_recon_panel(self, recon: Recon) -> Panel:
        ip_info_table = Table(title="IP Info", show_header=False, expand=True)
        ip_info_table.add_column(justify="right")
        ip_info_table.add_column()

        for ip_info in recon.ip_info:
            ip_info_table.add_row("IP address", ip_info.ip_address)
            ip_info_table.add_row("Country", ip_info.country.upper())
            ip_info_table.add_row("Network name", ip_info.network_name)
            ip_info_table.add_row("ASN", ip_info.asn)
            ip_info_table.add_section()

        ports_table = Table(title="Ports", expand=True)
        ports_table.add_column("Port", justify="right")
        ports_table.add_column("Protocol")
        ports_table.add_column("Service")
        ports_table.add_column("Product")

        for port in recon.ports:
            ports_table.add_row(
                str(port.port),
                "TCP",
                port.service,
                port.product + (f" {port.version}" if port.version is not None else ""),
            )

        web_technologies_table = Table(title="Web Technologies", expand=True)
        web_technologies_table.add_column("Software", justify="right")
        web_technologies_table.add_column("Category")

        for tech in recon.web_technologies:
            web_technologies_table.add_row(
                tech.name + (f" {tech.version}" if tech.version is not None else ""),
                tech.category,
            )

        return Panel(
            Group(ip_info_table, Text(), ports_table, Text(), web_technologies_table),
            title="Recon",
            expand=False,
            padding=(1, 1, 0, 1),
        )


class JsonConsoleOutputter(Outputter):
    """Output the result of a scan to the console in JSON format"""

    def __init__(self, indent: int):
        self.indent = indent

    def output(self, scan_result: ScanResult) -> None:
        default_console.print_json(scan_result.model_dump_json(), indent=self.indent)


class PrettyConsoleOutputter(PrettyOutputter):
    """Output the result of a scan to the console in Pretty format"""

    def output(self, scan_result: ScanResult) -> None:
        default_console.print()
        default_console.rule(
            title=f"{scan_result.scan_info.target} Vulnerability Scan Result"
        )
        default_console.print()
        default_console.print(
            self._get_scan_info_panel(scan_result.scan_info, scan_result.id)
        )
        default_console.print()
        default_console.print(self._get_recon_panel(scan_result.recon))

        if scan_result.scan_info.status == ScanStatus.RUNNING:
            default_console.print()
            default_console.print(
                f"[yellow][WARNING] The scan is still running (currently at {scan_result.scan_info.progress}%). "
                f"Run vulnissimo get {scan_result.id} again to get the full result when it is ready.[yellow]"
            )


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
                default_console.print(
                    f"[INFO] Scan result was written to {self.output_file}."
                )
                return
            except PermissionError as e:
                error_console.print(
                    f"[ERROR] Could not open file for writing: {e.strerror}."
                )
                self.output_file = Prompt.ask(
                    "Enter another file name for writing"
                    " (or leave empty to write the scan result to the console)"
                )


class PrettyFileOutputter(PrettyOutputter):
    """Output the result of a scan to a file in Pretty format"""

    def __init__(self, output_file: str):
        self.output_file = output_file

    def output(self, scan_result: ScanResult) -> None:
        while True:
            try:
                with open(self.output_file, "w+", encoding="UTF-8") as f:
                    file_console = Console(file=f)

                    file_console.print(
                        self._get_scan_info_panel(scan_result.scan_info, scan_result.id)
                    )
                    file_console.print()
                    file_console.print(self._get_recon_panel(scan_result.recon))

                if scan_result.scan_info.status == ScanStatus.RUNNING:
                    default_console.print()
                    default_console.print(
                        "[yellow][WARNING] The scan is still running"
                        f" (currently at {scan_result.scan_info.progress}%). "
                        f"Run vulnissimo get {scan_result.id} again"
                        " to get the full result when it is ready.[yellow]"
                    )

                default_console.print(
                    f"[INFO] Scan result was written to {self.output_file}."
                )

                return
            except PermissionError as e:
                error_console.print(
                    f"[ERROR] Could not open file for writing: {e.strerror}."
                )
                self.output_file = Prompt.ask(
                    "Enter another file name for writing"
                    " (or leave empty to write the scan result to the console)"
                )


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
