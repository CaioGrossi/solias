from __future__ import annotations

import re
from dataclasses import dataclass, field
from string import Template

PLACEHOLDER_RE = re.compile(r"\$\{([a-zA-Z_][a-zA-Z0-9_]*)\}")


class ConfigError(Exception):
    pass


def placeholders_in(cmd: str) -> list[str]:
    seen: list[str] = []
    for name in PLACEHOLDER_RE.findall(cmd):
        if name not in seen:
            seen.append(name)
    return seen


@dataclass
class Arg:
    name: str
    default: str | None = None
    description: str | None = None

    @classmethod
    def from_dict(cls, d: dict) -> Arg:
        if not isinstance(d, dict) or "name" not in d:
            raise ConfigError(f"arg entry must have a 'name': {d!r}")
        return cls(
            name=d["name"],
            default=d.get("default"),
            description=d.get("description"),
        )


@dataclass
class Command:
    abbr: str
    description: str
    command: str
    args: list[Arg] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> Command:
        if not isinstance(d, dict):
            raise ConfigError(f"command entry must be an object: {d!r}")
        return cls(
            abbr=d.get("abbr", ""),
            description=d.get("description", ""),
            command=d.get("command", ""),
            args=[Arg.from_dict(a) for a in d.get("args", [])],
        )

    def placeholder_order(self) -> list[str]:
        ordered = [a.name for a in self.args]
        for name in placeholders_in(self.command):
            if name not in ordered:
                ordered.append(name)
        return ordered

    def arg_for(self, name: str) -> Arg | None:
        for a in self.args:
            if a.name == name:
                return a
        return None

    def args_summary(self) -> str:
        names = self.placeholder_order()
        if not names:
            return "-"
        parts = []
        for name in names:
            arg = self.arg_for(name)
            if arg and arg.default is not None:
                parts.append(f"{name}={arg.default}")
            else:
                parts.append(name)
        return ", ".join(parts)

    def resolve(self, values: dict[str, str]) -> str:
        return Template(self.command).safe_substitute(values)
