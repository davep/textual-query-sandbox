"""A simple textual CSS query sandbox."""

from __future__ import annotations

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Button, Input, Pretty

class Playground(Vertical, inherit_css=False):
    """The playground container."""

    BORDER_TITLE = "Playground"

    DEFAULT_CSS = """
    Playground {
        border: panel cornflowerblue;
        height: 2fr;
    }
    """

class QuerySandboxApp(App[None]):
    """A Textual CSS query sandbox application."""

    CSS = """
    Input {
        width: 1fr;
    }

    #input {
        height: 4;
    }

    Playground * {
        margin: 1;
        border: panel red 40%;
    }

    .hit {
        border: panel green !important;
        background: green 10%;
    }

    Pretty {
        margin-top: 1;
        height: 1fr;
        border: panel cornflowerblue;
        padding: 1;
    }
    """

    @staticmethod
    def t(widget: Widget, title: str | None = None) -> Widget:
        """Add a title to a widget.

        Args:
            widget: The widget to name.
            title: The optional title to give the widget.

        Returns:
            The widget.
        """
        border_title = title
        if title is None:
            border_title = widget.__class__.__name__
            if widget.id is not None:
                border_title = f"{border_title}#{widget.id}"
            if widget.classes:
                border_title = f"{border_title}.{'.'.join(widget.classes)}"
        widget.border_title = border_title
        return widget

    def compose(self) -> ComposeResult:
        """Compose the DOM for the application."""
        with Horizontal(id="input"):
            yield Input()
            yield Button("Query")
        with Playground():
            with self.t(Vertical(id="one", classes="foo bar")):
                with self.t(Vertical(id="two")):
                    with self.t(Horizontal(id="three", classes="baz")):
                        for n in range(3):
                            yield self.t(Vertical(id=f"three-{n}", classes=f"wibble wobble-{n}"))
                    with self.t(Vertical(id="four")):
                        yield self.t(Vertical(id="innermost", classes="foo baz"))
        yield self.t(Pretty([]), "Query Results")

    @on(Input.Submitted)
    @on(Button.Pressed)
    def do_query(self) -> None:
        """Perform the query and show the result."""
        self.query("Playground *").remove_class("hit")
        try:
            hits = self.query_one(Playground).query(
                self.query_one(Input).value
            )
            hits.add_class("hit")
            result = list(hits)
        except Exception as error: # pylint:disable=broad-exception-caught
            result = error
        self.query_one(Pretty).update(result)
        self.query_one(Input).focus()

### sandbox.py ends here
