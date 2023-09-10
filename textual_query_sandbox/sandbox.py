"""A simple textual DOM query sandbox."""

from __future__ import annotations

from itertools import cycle

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Grid, Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Button, Input, Pretty, Static, TabbedContent, TabPane, Label


class Playground(Vertical, inherit_css=False):
    """The playground container."""

    BORDER_TITLE = "Playground"

    DEFAULT_CSS = """
    Playground {
        border: panel cornflowerblue;
        height: 2fr;
    }
    """

    def on_mount(self) -> None:
        """Set up the playground once the DOM is mounted."""
        # There's little point in anything in the playground getting focus,
        # so remove that ability from everything in here.
        for child in self.query("*"):
            child.can_focus = False


def title(widget: Widget, main_title: str | None = None) -> Widget:
    """Add a title to a widget.

    Args:
        widget: The widget to name.
        main_title: The optional title to give the widget.

    Returns:
        The widget.
    """
    border_title = main_title
    if main_title is None:
        border_title = widget.__class__.__name__
        if widget.id is not None:
            border_title = f"{border_title}#{widget.id}"
        if widget.classes:
            border_title = f"{border_title}.{'.'.join(widget.classes)}"
    widget.border_title = border_title
    return widget


class NestedContainers(Playground):
    """A Playground made of nested containers."""

    def compose(self) -> ComposeResult:
        """Compose the playground."""
        with title(Vertical(id="one", classes="foo bar")):
            with title(Vertical(id="two")):
                with title(Horizontal(id="three", classes="baz")):
                    for n in range(3):
                        yield title(
                            Vertical(id=f"three-{n}", classes=f"wibble wobble-{n}")
                        )
                with title(Vertical(id="four")):
                    yield title(Vertical(id="innermost", classes="foo baz"))


class VariousWidgets(Playground):
    """A playground made of some widgets."""

    DEFAULT_CSS = """
    VariousWidgets Label {
        width: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the playground."""
        with title(Horizontal()):
            classes = cycle(("foo", "bar"))
            with title(Vertical(id="input-widgets")):
                for n in range(5):
                    yield title(
                        Input(
                            placeholder=f"Example input {n}",
                            id=f"input-{n}",
                            classes=next(classes),
                        )
                    )
            with title(Vertical(id="static-and-labels")):
                for n in range(3):
                    yield title(
                        Static(
                            "Can you find me?", id=f"static-{n}", classes=next(classes)
                        )
                    )
                    yield title(
                        Label(
                            "Can you find me?", id=f"label-{n}", classes=next(classes)
                        )
                    )


class IDAndClassGrid(Playground):
    """A playground of ID and class combinations."""

    DEFAULT_CSS = """
    IDAndClassGrid Grid {
        grid-size: 3 3;
    }

    IDAndClassGrid Static {
        height: 100%;
        content-align: center middle;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the child widgets."""
        two_cycle = cycle(("even", "odd"))
        three_cycle = cycle(("yes", "no", "maybe"))
        six_cycle = cycle(("up", "down", "strange", "charm", "bottom", "top"))
        with title(Grid()):
            for n in range(9):
                yield title(
                    Static(
                        str(n),
                        id=f"cell-{n}",
                        classes=f"{next(two_cycle)} {next(three_cycle)} {next(six_cycle)}",
                    )
                )


class QuerySandboxApp(App[None]):
    """A Textual CSS query sandbox application."""

    CSS = """
    Static {
        color: $text-muted;
    }

    Input {
        width: 1fr;
    }

    #input {
        height: 4;
    }

    TabbedContent {
        height: 2fr;
    }

    Playground * {
        margin: 1;
        border: panel red 40%;
        border-title-color: $text 50%;
    }

    Playground .hit {
        border: panel green;
        background: green 10%;
        border-title-color: $boost;
    }

    VerticalScroll {
        margin-top: 1;
        height: 1fr;
        border: panel cornflowerblue 60%;
        padding: 1;
    }

    VerticalScroll:focus {
        border: panel cornflowerblue;
    }

    #output {
        height: 1fr;
    }

    #results {
        width: 3fr;
    }

    #tree {
        width: 2fr;
    }
    """

    BINDINGS = [
        Binding("f1", "playground('tab-1')"),
        Binding("f2", "playground('tab-2')"),
        Binding("f3", "playground('tab-3')"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the DOM for the application."""
        with Horizontal(id="input"):
            yield Input()
            yield Button("Query")
        with TabbedContent():
            with TabPane("Nested Containers (F1)"):
                yield NestedContainers()
            with TabPane("Various Widgets (F2)"):
                yield VariousWidgets()
            with TabPane("IDs and Classes (F3)"):
                yield IDAndClassGrid()
        with Horizontal(id="output"):
            with title(VerticalScroll(id="results"), "Query Results"):
                yield Pretty([])
            with title(VerticalScroll(id="tree"), "Playground DOM Tree"):
                yield Static("")

    @property
    def input(self) -> Input:
        """The main input widget."""
        return self.query_one("#input Input", Input)

    @property
    def playground(self) -> Playground:
        """The current playground widget."""
        return self.query_one(
            f"TabPane#{self.query_one(TabbedContent).active} Playground", Playground
        )

    @on(Input.Submitted)
    @on(Button.Pressed)
    @on(TabbedContent.TabActivated)
    def do_query(self, event: Message | None = None) -> None:
        """Perform the query and show the result."""
        self.query("Playground *").remove_class("hit")
        result: list[Widget] | Exception
        try:
            result = list(
                self.playground.query(f"Playground {self.input.value}").add_class("hit")
            )
        except Exception as error:  # pylint:disable=broad-exception-caught
            result = error
        self.query_one("#results > Pretty", Pretty).update(result)
        self.query_one("#tree > Static", Static).update(
            self.playground.children[0].tree
        )
        if not isinstance(event, TabbedContent.TabActivated):
            self.input.focus()

    def action_playground(self, playground: str) -> None:
        """Switch between different playgrounds.

        Args:
            playground: The playground to switch to.
        """
        self.query_one(TabbedContent).active = playground
        self.do_query()


### sandbox.py ends here
