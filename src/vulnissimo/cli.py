"""The CLI module for Vulnissimo."""

import json
import time
from typing import Annotated
from uuid import UUID

import typer
from rich import print as rich_print, print_json
from rich.progress import (
    BarColumn,
    Progress,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.prompt import Prompt

from .api import get_scan_info, run_scan
from .exceptions import StartScanException

app = typer.Typer(no_args_is_help=True)


@app.command(no_args_is_help=True)
def get(
    scan_id: UUID,
    output_file: Annotated[
        str | None, typer.Option(help="File to write scan result to")
    ] = None,
):
    """Get scan by ID"""
    scan = get_scan_info(scan_id)
    output_scan(scan, output_file)


@app.command(no_args_is_help=True)
def run(
    target: str,
    output_file: Annotated[
        str | None, typer.Option(help="File to write scan result to")
    ] = None,
):
    """Run a scan on a given target"""

    try:
        started_scan = run_scan(target)
        rich_print(f"Scan started on {target}.")
        rich_print(f"See live updates at https://vulnissimo.io/scans/{started_scan['id']}.")

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
                scan = get_scan_info(started_scan["id"])
                new_scan_progress = scan["scan_info"]["progress"]
                scan_progress_diff = new_scan_progress - scan_progress
                if scan_progress_diff != 0:
                    progress_bar.update(task_id, advance=scan_progress_diff)
                scan_progress = new_scan_progress
                if scan["scan_info"]["status"] == "finished":
                    break
                time.sleep(2)

        output_scan(scan, output_file)

    except StartScanException as e:
        rich_print(
            f"[red bold]Could not start scan:[/red bold] {e.status_code}: {e.error_msg}"
        )


def output_scan(scan: dict, output_file: str | None):
    """
    If `output_file` is provided, write the scan to `output_file`. Else, print it to the console
    """

    while True:
        if not output_file:
            print_json(json.dumps(scan))
            return

        try:
            with open(output_file, "w+", encoding="UTF-8") as f:
                json.dump(scan, f, indent=4)
            rich_print(f"Scan result was written to {output_file}.")
            return
        except PermissionError as e:
            rich_print(f"[red]Could not open file for writing: {e.strerror}.[/red]")
            output_file = Prompt.ask(
                "Enter another file name for writing"
                " (or leave empty to write the scan result to the console)"
            )
