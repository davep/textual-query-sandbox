"""Main entry point for the application."""

from .sandbox import QuerySandboxApp


def run() -> None:
    """Run the application."""
    QuerySandboxApp().run()


if __name__ == "__main__":
    run()

### __main__.py ends here
