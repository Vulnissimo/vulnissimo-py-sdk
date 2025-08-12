"""The CLI module for Vulnissimo."""

import time
from typing import Annotated
from uuid import UUID

import typer
from rich.progress import (
    BarColumn,
    Progress,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)

from .api import get_scan_result, run_scan
from .client import Client
from .console import default_console, error_console
from .enums import ScanResultOutputType
from .errors import APIError
from .models import ScanCreate, ScanResult, ScanStatus
from .scan_result_output import OutputterFactory

app = typer.Typer(no_args_is_help=True)


def get_client():
    """Get a basic client for the Vulnissimo api"""

    return Client(base_url="https://api.vulnissimo.io")


@app.command(no_args_is_help=True)
def get(
    scan_id: UUID,
    output_file: Annotated[
        str | None, typer.Option(help="File to write scan result to")
    ] = None,
    output_type: Annotated[
        ScanResultOutputType, typer.Option(help="Scan output type")
    ] = ScanResultOutputType.PRETTY,
    indent: Annotated[
        int,
        typer.Option(
            help="Indentation of the output (only applicable to JSON outputs)"
        ),
    ] = 2,
):
    """Get scan by ID"""

    try:
        with get_client() as client:
            scan_result = get_scan_result.sync(scan_id=scan_id, client=client)

            factory = OutputterFactory()
            outputter = factory.create_outputter(output_file, output_type, indent)
            outputter.output(scan_result)
    except APIError as e:
        error_console.print(f"[ERROR] {str(e)}")


@app.command(no_args_is_help=True)
def run(
    target: str,
    output_file: Annotated[
        str | None, typer.Option(help="File to write scan result to")
    ] = None,
    output_type: Annotated[
        ScanResultOutputType, typer.Option(help="Scan output type")
    ] = ScanResultOutputType.PRETTY,
    indent: Annotated[
        int,
        typer.Option(
            help="Indentation of the output (only applicable to JSON outputs)"
        ),
    ] = 2,
):
    """Run a scan on a given target"""

    try:
        with get_client() as client:
            started_scan = run_scan.sync(client=client, body=ScanCreate(target=target))
            default_console.print(f"[INFO] Scan started on {target}")
            default_console.print(f"[INFO] Scan ID: {started_scan.id}")
            default_console.print(
                f"[INFO] See live updates at {started_scan.html_result}"
            )

            progress_columns = [
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
            ]

            with Progress(*progress_columns) as progress:
                task_id = progress.add_task("Scanning...")
                prev_scan_result: ScanResult | None = None

                while True:
                    scan_result = get_scan_result.sync(
                        scan_id=started_scan.id, client=client
                    )

                    if scan_result.scan_info.redirect_url is not None and (
                        prev_scan_result is None
                        or prev_scan_result.scan_info.redirect_url is None
                    ):
                        progress.console.print(
                            f"[INFO] Target URL redirected to {scan_result.scan_info.redirect_url}"
                        )

                    progress.update(task_id, completed=scan_result.scan_info.progress)

                    if scan_result.scan_info.status == ScanStatus.FINISHED:
                        break

                    prev_scan_result = scan_result

                    time.sleep(2)

        default_console.print("[INFO] Scan complete.")

        factory = OutputterFactory()
        outputter = factory.create_outputter(output_file, output_type, indent)
        outputter.output(scan_result)

    except APIError as e:
        error_console.print(f"[ERROR] {str(e)}")
