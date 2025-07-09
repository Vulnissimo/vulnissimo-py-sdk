"""Defines `Console` instances that are unique to an application instance"""

from rich.console import Console

console = Console()
error_console = Console(stderr=True, style="red")
