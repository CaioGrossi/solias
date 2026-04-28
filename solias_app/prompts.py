from __future__ import annotations

import questionary

from solias_app.command import Command


def prompt_args(command: Command) -> dict[str, str] | None:
    values: dict[str, str] = {}
    for name in command.placeholder_order():
        arg = command.arg_for(name)
        default = (arg.default if arg else None) or ""
        desc = arg.description if arg else None
        label = f"{name} ({desc})" if desc else name
        answer = questionary.text(label, default=str(default)).ask()
        if answer is None:
            return None
        values[name] = answer
    return values
