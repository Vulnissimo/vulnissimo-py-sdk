"""The CLI module for Vulnissimo."""

import json
import time
from typing import Annotated
from uuid import UUID

import typer
from rich import print as rich_print
from rich import print_json
from rich.progress import (
    BarColumn,
    Progress,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.prompt import Prompt

from .api import get_scan_result, run_scan
from .client import Client
from .errors import APIError
from .models import ScanCreate, ScanResult, ScanStatus

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
            scan = get_scan_result.sync(scan_id=scan_id, client=client)
            output_scan(scan, output_file, indent)
    except APIError as e:
        rich_print(f"[red]{str(e)}[/red]")


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
            rich_print(f"Scan started on {target}.")
            rich_print(f"See live updates at {started_scan.html_result}.")

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
                    scan = get_scan_result.sync(scan_id=started_scan.id, client=client)
                    new_scan_progress = scan.scan_info.progress
                    scan_progress_diff = new_scan_progress - scan_progress
                    if scan_progress_diff != 0:
                        progress_bar.update(task_id, advance=scan_progress_diff)
                    scan_progress = new_scan_progress
                    if scan.scan_info.status == ScanStatus.FINISHED:
                        break
                    time.sleep(2)

        output_scan(scan, output_file, indent)

    except APIError as e:
        rich_print(f"[red]{str(e)}[/red]")


def output_scan(scan: ScanResult, output_file: str | None, indent: int):
    """
    If `output_file` is provided, write the scan to `output_file`. Else, print it to the console
    """

    while True:
        if not output_file:
            print_json(scan.model_dump_json(), indent=indent)
            return

        try:
            with open(output_file, "w+", encoding="UTF-8") as f:
                json.dump(scan.model_dump(mode="json"), f, indent=indent)
            rich_print(f"Scan result was written to {output_file}.")
            return
        except PermissionError as e:
            rich_print(f"[red]Could not open file for writing: {e.strerror}.[/red]")
            output_file = Prompt.ask(
                "Enter another file name for writing"
                " (or leave empty to write the scan result to the console)"
            )
