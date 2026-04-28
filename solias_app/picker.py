from __future__ import annotations

from dataclasses import dataclass

from prompt_toolkit import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.formatted_text import FormattedText
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import HSplit, Layout, VSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl

from solias_app.command import Command

HEADERS = ("Abbr", "Description", "Args", "Command")
CMD_PREVIEW_MAX = 30
LAST_COL_PAD = 6


def _truncate(s: str, n: int) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"


@dataclass
class Row:
    abbr: str
    description: str
    args: str
    preview: str
    command: Command

    @classmethod
    def from_command(cls, c: Command) -> Row:
        return cls(
            abbr=c.abbr,
            description=c.description,
            args=c.args_summary(),
            preview=_truncate(c.command, CMD_PREVIEW_MAX),
            command=c,
        )

    def cells(self) -> tuple[str, str, str, str]:
        return (self.abbr, self.description, self.args, self.preview)

    def matches(self, q: str) -> bool:
        return any(q in c.lower() for c in self.cells())


class PickerState:
    def __init__(self, rows: list[Row]):
        self.rows = rows
        self.search = Buffer(on_text_changed=self._reset_index)
        self.index = 0
        self.popup = False

    def _reset_index(self, _):
        self.index = 0

    def filtered(self) -> list[Row]:
        q = self.search.text.lower()
        if not q:
            return self.rows
        return [r for r in self.rows if r.matches(q)]

    def selected(self) -> Row | None:
        rs = self.filtered()
        if not rs:
            return None
        if self.index >= len(rs):
            self.index = len(rs) - 1
        return rs[self.index]

    def move_up(self):
        self.index = max(0, self.index - 1)

    def move_down(self):
        self.index = min(max(0, len(self.filtered()) - 1), self.index + 1)

    def open_popup(self):
        if self.filtered():
            self.popup = True

    def close_popup(self):
        self.popup = False


class TableRenderer:
    def __init__(self, state: PickerState):
        self.state = state

    def __call__(self) -> FormattedText:
        rs = self.state.filtered()
        if self.state.index >= len(rs):
            self.state.index = max(0, len(rs) - 1)
        widths = self._col_widths(rs)
        frags: list[tuple[str, str]] = []
        frags.extend(self._header(widths))
        frags.extend(self._body(rs, widths))
        if self.state.popup and rs:
            frags.extend(self._popup(rs[self.state.index].command.command))
        frags.extend(self._footer())
        return FormattedText(frags)

    def _col_widths(self, rs: list[Row]) -> list[int]:
        w = [len(h) for h in HEADERS]
        for r in rs:
            for i, cell in enumerate(r.cells()):
                w[i] = max(w[i], len(cell))
        w[3] += LAST_COL_PAD
        return w

    def _header(self, widths):
        line = "  " + "  ".join(h.ljust(widths[i]) for i, h in enumerate(HEADERS))
        sep = "  " + "  ".join("─" * widths[i] for i in range(len(HEADERS)))
        return [("bold", line + "\n"), ("", sep + "\n")]

    def _body(self, rs, widths):
        if not rs:
            return [("italic", "  (no matches)\n")]
        out = []
        for i, r in enumerate(rs):
            line = "  ".join(c.ljust(widths[j]) for j, c in enumerate(r.cells()))
            style = "reverse" if i == self.state.index else ""
            prefix = "▶ " if i == self.state.index else "  "
            out.append((style, prefix + line + "\n"))
        return out

    def _popup(self, full):
        content_w = max(len(full), 8)
        total = content_w + 2
        return [
            ("", "\n"),
            ("ansicyan", "  ┌─ Command " + "─" * (total - 10) + "┐\n"),
            ("ansicyan", "  │ "),
            ("", full.ljust(content_w)),
            ("ansicyan", " │\n"),
            ("ansicyan", "  └" + "─" * total + "┘\n"),
        ]

    def _footer(self):
        hint = "↑/↓ navigate · → expand · type to filter · Enter select · Esc cancel"
        if self.state.popup:
            hint = "← close · " + hint
        return [("", "\n"), ("dim", hint + "\n")]


class Picker:
    def __init__(self, commands: list[Command]):
        self.state = PickerState([Row.from_command(c) for c in commands])
        self.renderer = TableRenderer(self.state)

    def run(self) -> Command | None:
        return Application(
            layout=self._layout(),
            key_bindings=self._key_bindings(),
            full_screen=False,
        ).run()

    def _layout(self) -> Layout:
        label = Window(FormattedTextControl([("bold", "Search: ")]), width=8, height=1)
        search = Window(BufferControl(buffer=self.state.search), height=1)
        table = Window(content=FormattedTextControl(self.renderer))
        return Layout(
            HSplit([VSplit([label, search]), table]),
            focused_element=search,
        )

    def _key_bindings(self) -> KeyBindings:
        kb = KeyBindings()
        kb.add("up")(self._on_up)
        kb.add("down")(self._on_down)
        kb.add("right")(self._on_right)
        kb.add("left")(self._on_left)
        kb.add("enter")(self._on_enter)
        kb.add("c-c")(self._on_cancel)
        kb.add("escape")(self._on_escape)
        return kb

    def _on_up(self, event):
        self.state.move_up()

    def _on_down(self, event):
        self.state.move_down()

    def _on_right(self, event):
        self.state.open_popup()

    def _on_left(self, event):
        self.state.close_popup()

    def _on_enter(self, event):
        row = self.state.selected()
        if row:
            event.app.exit(result=row.command)

    def _on_cancel(self, event):
        event.app.exit(result=None)

    def _on_escape(self, event):
        if self.state.popup:
            self.state.close_popup()
        else:
            event.app.exit(result=None)


def pick_command(commands: list[Command]) -> Command | None:
    return Picker(commands).run()
