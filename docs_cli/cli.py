"""CLI interface for docs-cli."""

from typer import Exit, Option, Typer

app = Typer(
    help="Query Python package documentation for AI agents",
    no_args_is_help=True,
    add_completion=False,
)


@app.command()
def query(
    target: str,
    version: bool = Option(False, "--version", "-v", help="Show version and exit"),
) -> None:
    """Query Python package documentation.

    TARGET is the package or element to query (e.g., pandas.DataFrame).
    """
    if version:
        from docs_cli import __version__

        import sys

        sys.stdout.write(f"docs-cli v{__version__}\n")
        raise Exit(code=0)

    import sys

    sys.stdout.write(f"Hello from docs-cli! Querying: {target}\n")


if __name__ == "__main__":
    app()
