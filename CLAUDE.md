# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`solias` is a Python CLI that reads commands from `~/.soliasrc` (JSON), shows an interactive picker, prompts for any `${name}` placeholders, and runs the resolved string via `subprocess.run(..., shell=True)`.

## Commands

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python solias.py
```

No tests, linter, or build step exist.

## Architecture

`solias.py` at the root is a thin entry point that calls `solias_app.cli.run()`. All logic lives in the `solias_app/` package:

- `command.py` — `Command` and `Arg` dataclasses, `ConfigError`, and `placeholders_in()`. The `Command` model owns its derived behavior: `placeholder_order()` (declared args first, then any extra `${...}` found in the command), `args_summary()` (display string for the picker), and `resolve(values)` (`Template.safe_substitute`). All other modules consume typed `Command` objects, never raw dicts.
- `config.py` — `load_config()` parses `~/.soliasrc` and returns `list[Command]`, raising `ConfigError` on bad JSON or shape. `ensure_config_exists()` writes `SEED_CONFIG` on first run. No printing or `sys.exit` here — the CLI layer decides how to present errors.
- `picker.py` — three classes by responsibility: `PickerState` (rows, search buffer, selection index, popup flag, plus mutation methods), `TableRenderer` (state → `FormattedText`), and `Picker` (wires prompt_toolkit `Application`, `Layout`, key bindings). `Row.from_command` produces the display row; `pick_command()` is the public entry. Key bindings dispatch to `PickerState` mutators or `Application.exit()`.
- `prompts.py` — `prompt_args(Command)` walks `command.placeholder_order()` and uses questionary to collect values. Returns `None` on cancellation.
- `cli.py` — `main()` orchestrates: ensure config → load → pick → prompt → resolve → run. Owns the single `rich.Console` and the `CANCELLED = 130` exit code.

## Conventions

- Avoid nested function definitions; use methods on classes when state needs to be shared between handlers.
- Keep I/O modules (`config`, `picker`, `prompts`) free of `sys.exit` and user-facing printing — raise or return; let `cli.py` present.
- Substitution uses `safe_substitute`, so unfilled `${name}` tokens pass through unchanged rather than raising.
- Exit code 130 = user cancellation (Ctrl-C, Esc, or questionary returning `None`); subprocess return code is propagated otherwise.
