from __future__ import annotations

import subprocess
import sys

from rich.console import Console

from solias_app.command import ConfigError
from solias_app.config import CONFIG_PATH, ensure_config_exists, load_config
from solias_app.picker import pick_command
from solias_app.prompts import prompt_args

CANCELLED = 130

console = Console()


def main() -> int:
    if ensure_config_exists():
        console.print(
            f"[yellow]Created seed config at {CONFIG_PATH}. "
            f"Edit it to register your own commands.[/yellow]"
        )

    try:
        commands = load_config()
    except ConfigError as e:
        console.print(f"[red]{e}[/red]")
        return 1

    if not commands:
        console.print(
            f"[yellow]No commands registered. Add some to {CONFIG_PATH}.[/yellow]"
        )
        return 0

    command = pick_command(commands)
    if command is None:
        return CANCELLED

    values = prompt_args(command)
    if values is None:
        return CANCELLED

    resolved = command.resolve(values)
    console.print(f"[dim]$ {resolved}[/dim]")
    return subprocess.run(resolved, shell=True).returncode


def run() -> None:
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(CANCELLED)
