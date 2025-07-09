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
from .console import console, error_console
from .enums import ScanResultOutputType
from .errors import APIError
from .models import ScanCreate, ScanStatus
from .scan_result_output import output_scan

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
    indent: Annotated[int, typer.Option(help="Indentation of the JSON output")] = 2,
):
    """Get scan by ID"""

    try:
        with get_client() as client:
            scan_result = get_scan_result.sync(scan_id=scan_id, client=client)
            output_scan(scan_result, output_file, ScanResultOutputType.JSON, indent)
    except APIError as e:
        error_console.print(f"{str(e)}")


@app.command(no_args_is_help=True)
def run(
    target: str,
    output_file: Annotated[
        str | None, typer.Option(help="File to write scan result to")
    ] = None,
    indent: Annotated[int, typer.Option(help="Indentation of the JSON output")] = 2,
):
    """Run a scan on a given target"""

    try:
        with get_client() as client:
            started_scan = run_scan.sync(client=client, body=ScanCreate(target=target))
            console.print(f"Scan started on {target}.")
            console.print(f"See live updates at {started_scan.html_result}.")

            progress_columns = [
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                TimeElapsedColumn(),
            ]

            with Progress(*progress_columns) as progress_bar:
                task_id = progress_bar.add_task("Scanning...")
                scan_progress = 0

                while True:
                    scan_result = get_scan_result.sync(
                        scan_id=started_scan.id, client=client
                    )
                    new_scan_progress = scan_result.scan_info.progress
                    scan_progress_diff = new_scan_progress - scan_progress
                    if scan_progress_diff != 0:
                        progress_bar.update(task_id, advance=scan_progress_diff)
                    scan_progress = new_scan_progress
                    if scan_result.scan_info.status == ScanStatus.FINISHED:
                        break
                    time.sleep(2)

        output_scan(scan_result, output_file, ScanResultOutputType.JSON, indent)

    except APIError as e:
        error_console.print(f"{str(e)}")
