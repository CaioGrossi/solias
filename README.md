# solias

<video src="media/video.mp4" controls></video>

Personal CLI command launcher. Run `solias`, browse a table of registered commands, pick one with arrow keys, fill in any placeholders, and it runs in your shell. Build with Claude Code Opus 4.6

## Install

```bash
cd /Users/caio.grossi/Documents/solias
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

Then symlink onto your PATH (pointing at the venv-aware launcher):

```bash
echo "alias solias='$PWD/.venv/bin/python $PWD/solias.py'" >> ~/.zshrc
source ~/.zshrc
```

## Configure

Commands live in `~/.soliasrc` (JSON array). On first run a seed file is created.

```json
[
  {
    "abbr": "bd",
    "description": "Build dev for given countries",
    "command": "nu dev bd --countries ${countries}",
    "args": [
      { "name": "countries", "default": "BR", "description": "Comma-separated country codes" }
    ]
  }
]
```

- `abbr` — short label (column 1).
- `description` — column 2.
- `command` — full shell command; use `${name}` for placeholders.
- `args` — list of placeholders to prompt for; each may have `default` and `description`.

## Use

```bash
solias
```

Pick a row with the arrow keys, hit Enter, fill in args (defaults shown), and the resolved command runs in your shell.
