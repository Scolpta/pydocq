"""CLI interface for docs-cli."""

import json
import sys

from typer import Exit, Option, Typer

from docs_cli.analyzer.formatter import format_json, format_json_compact, format_json_verbose
from docs_cli.analyzer.inspector import inspect_element
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
    compact: bool = Option(False, "--compact", "-c", help="Use compact output format"),
    verbose: bool = Option(False, "--verbose", "-V", help="Use verbose output format"),
    no_docstring: bool = Option(False, "--no-docstring", help="Exclude docstring from output"),
    no_signature: bool = Option(False, "--no-signature", help="Exclude signature from output"),
    include_source: bool = Option(False, "--include-source", "-s", help="Include source location"),
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

        # Inspect the element
        inspected = inspect_element(resolved)

        # Format output based on options
        if compact:
            output = format_json_compact(inspected)
        elif verbose:
            output = format_json_verbose(inspected)
        else:
            output = format_json(
                inspected,
                include_docstring=not no_docstring,
                include_signature=not no_signature,
                include_source=include_source,
            )

        # Print as JSON
        sys.stdout.write(json.dumps(output, indent=2))

    except (InvalidPathError, PackageNotFoundError, ElementNotFoundError) as e:
        sys.stderr.write(f"Error: {e}\n")
        raise Exit(code=1)


if __name__ == "__main__":
    app()
