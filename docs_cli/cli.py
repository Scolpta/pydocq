"""CLI interface for docs-cli."""

import json
import sys

from typer import Exit, Option, Typer

from docs_cli.analyzer.resolver import (
    ElementNotFoundError,
    InvalidPathError,
    PackageNotFoundError,
    resolve_path,
)

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

    Examples:
        doc pandas.DataFrame
        doc pandas.core.frame.DataFrame.merge
        doc os.path.join
    """
    if version:
        from docs_cli import __version__

        sys.stdout.write(f"docs-cli v{__version__}\n")
        raise Exit(code=0)

    try:
        # Resolve the target path
        resolved = resolve_path(target)

        # Create output structure
        output = {
            "path": resolved.path,
            "type": resolved.element_type.value,
            "module_path": resolved.module_path,
        }

        # Print as JSON
        sys.stdout.write(json.dumps(output, indent=2))

    except (InvalidPathError, PackageNotFoundError, ElementNotFoundError) as e:
        sys.stderr.write(f"Error: {e}\n")
        raise Exit(code=1)


if __name__ == "__main__":
    app()
