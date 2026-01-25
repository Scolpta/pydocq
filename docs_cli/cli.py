"""CLI interface for docs-cli."""

import json
import sys

from typer import Exit, Option, Typer

from docs_cli.analyzer.discovery import discover_class_members, discover_module_members
from docs_cli.analyzer.formatter import format_json, format_json_compact, format_json_verbose
from docs_cli.analyzer.inspector import inspect_element
from docs_cli.analyzer.resolver import (
    ElementNotFoundError,
    ElementType,
    InvalidPathError,
    PackageNotFoundError,
    resolve_path,
)

app = Typer(
    help="Query Python package documentation for AI agents",
    no_args_is_help=True,
    add_completion=False,
)


def _format_member_info(member) -> dict:
    """Format a MemberInfo object for JSON output.

    Args:
        member: MemberInfo object

    Returns:
        JSON-serializable dictionary
    """
    return {
        "name": member.name,
        "type": member.element_type.value,
        "is_public": member.is_public,
        "is_defined_here": member.is_defined_here,
    }


def _format_module_members(module_members) -> dict:
    """Format a ModuleMembers object for JSON output.

    Args:
        module_members: ModuleMembers object

    Returns:
        JSON-serializable dictionary
    """
    return {
        "path": module_members.path,
        "members": [_format_member_info(m) for m in module_members.members],
        "classes": [_format_member_info(m) for m in module_members.classes],
        "functions": [_format_member_info(m) for m in module_members.functions],
        "methods": [_format_member_info(m) for m in module_members.methods],
        "properties": [_format_member_info(m) for m in module_members.properties],
        "submodules": [_format_member_info(m) for m in module_members.submodules],
    }


@app.command()
def query(
    target: str,
    version: bool = Option(False, "--version", "-v", help="Show version and exit"),
    compact: bool = Option(False, "--compact", "-c", help="Use compact output format"),
    verbose: bool = Option(False, "--verbose", "-V", help="Use verbose output format"),
    no_docstring: bool = Option(False, "--no-docstring", help="Exclude docstring from output"),
    no_signature: bool = Option(False, "--no-signature", help="Exclude signature from output"),
    include_source: bool = Option(False, "--include-source", "-s", help="Include source location"),
    list_members: bool = Option(False, "--list-members", "-l", help="List all members of module/class"),
    include_private: bool = Option(False, "--include-private", help="Include private members"),
    include_imported: bool = Option(False, "--include-imported", help="Include imported members"),
    include_inherited: bool = Option(False, "--include-inherited", help="Include inherited members"),
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

        # Handle list_members option
        if list_members:
            if resolved.element_type == ElementType.MODULE:
                members = discover_module_members(
                    resolved.obj,
                    include_private=include_private,
                    include_imported=include_imported,
                )
                output = _format_module_members(members)
            elif resolved.element_type == ElementType.CLASS:
                members = discover_class_members(
                    resolved.obj,
                    include_private=include_private,
                    include_inherited=include_inherited,
                )
                output = {
                    "path": resolved.path,
                    "type": resolved.element_type.value,
                    "members": [_format_member_info(m) for m in members],
                }
            else:
                # For other types, just return the inspected element
                output = {"error": "Cannot list members for non-module/class types"}
        else:
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
