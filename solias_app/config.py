from __future__ import annotations

import json
from pathlib import Path

from solias_app.command import Command, ConfigError

CONFIG_PATH = Path.home() / ".soliasrc"

SEED_CONFIG = [
    {
        "abbr": "hello",
        "description": "Greet someone by name",
        "command": "echo hello ${name}",
        "args": [
            {"name": "name", "default": "world", "description": "Who to greet"}
        ],
    }
]


def ensure_config_exists() -> bool:
    if CONFIG_PATH.exists():
        return False
    CONFIG_PATH.write_text(json.dumps(SEED_CONFIG, indent=2) + "\n")
    return True


def load_config() -> list[Command]:
    try:
        data = json.loads(CONFIG_PATH.read_text())
    except json.JSONDecodeError as e:
        raise ConfigError(f"Invalid JSON in {CONFIG_PATH}: {e}") from e
    if not isinstance(data, list):
        raise ConfigError(f"{CONFIG_PATH} must contain a JSON array.")
    return [Command.from_dict(d) for d in data]
