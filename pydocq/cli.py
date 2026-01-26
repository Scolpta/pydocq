"""CLI interface for docs-cli."""

import json
import sys

from typer import Exit, Option, Typer

from pydocq.analyzer.discovery import discover_class_members, discover_module_members
from pydocq.analyzer.errors import DocsCliError
from pydocq.analyzer.formatter import format_json, format_json_compact, format_json_verbose
from pydocq.analyzer.inspector import inspect_element
from pydocq.analyzer.output_formats import get_formatter
from pydocq.analyzer.resolver import resolve_path
from pydocq.utils.type_detection import ElementType

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
    show_version: bool = Option(False, "--version", "-v", help="Show version and exit"),
    format: str = Option("json", "--format", "-f", help="Output format (json, raw, signature, markdown, yaml, llm)"),
    compact: bool = Option(False, "--compact", "-c", help="Use compact output format"),
    verbose: bool = Option(False, "--verbose", "-V", help="Use verbose output format"),
    no_docstring: bool = Option(False, "--no-docstring", help="Exclude docstring from output"),
    no_signature: bool = Option(False, "--no-signature", help="Exclude signature from output"),
    include_source: bool = Option(False, "--include-source", "-s", help="Include source location"),
    include_metadata: bool = Option(False, "--include-metadata", "-m", help="Include SDK metadata"),
    list_members: bool = Option(False, "--list-members", "-l", help="List all members of module/class"),
    include_private: bool = Option(False, "--include-private", help="Include private members"),
    include_imported: bool = Option(False, "--include-imported", help="Include imported members"),
    include_inherited: bool = Option(False, "--include-inherited", help="Include inherited members"),
    for_ai: bool = Option(False, "--for-ai", help="AI-optimized output (enables llm format, metadata, source, verbose)"),
) -> None:
    """Query Python package documentation.

    TARGET is the package or element to query (e.g., pandas.DataFrame).

    Examples:
        doc pandas.DataFrame
        doc pandas.core.frame.DataFrame.merge
        doc os.path.join
    """
    if show_version:
        from pydocq import __version__

        sys.stdout.write(f"docs-cli v{__version__}\n")
        raise Exit(code=0)

    # Handle --for-ai flag: combine all AI-optimized options
    if for_ai:
        format = "llm"
        include_metadata = True
        include_source = True
        verbose = True

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
                output_dict = _format_module_members(members)
                # Output is always JSON for list_members
                sys.stdout.write(json.dumps(output_dict, indent=2))
                return
            elif resolved.element_type == ElementType.CLASS:
                members = discover_class_members(
                    resolved.obj,
                    include_private=include_private,
                    include_inherited=include_inherited,
                )
                output_dict = {
                    "path": resolved.path,
                    "type": resolved.element_type.value,
                    "members": [_format_member_info(m) for m in members],
                }
                # Output is always JSON for list_members
                sys.stdout.write(json.dumps(output_dict, indent=2))
                return
            else:
                # For other types, return error
                sys.stderr.write("Error: Cannot list members for non-module/class types\n")
                raise Exit(code=1)

        # Inspect the element
        inspected = inspect_element(resolved)

        # Handle different output formats
        if format == "json":
            # Standard JSON output with options
            if compact:
                output_dict = format_json_compact(inspected)
            elif verbose:
                output_dict = format_json_verbose(inspected)
            else:
                output_dict = format_json(
                    inspected,
                    include_docstring=not no_docstring,
                    include_signature=not no_signature,
                    include_source=include_source,
                    include_metadata=include_metadata,
                )
            sys.stdout.write(json.dumps(output_dict, indent=2))
        else:
            # Use custom formatter (raw, signature, markdown, yaml)
            formatter = get_formatter(format)
            output = formatter(inspected)
            sys.stdout.write(output)
            # Add newline for non-JSON formats
            if not output.endswith('\n'):
                sys.stdout.write('\n')

    except DocsCliError as e:
        sys.stderr.write(f"Error: {e}\n")
        raise Exit(code=1)
    except ValueError as e:
        # Invalid format type
        sys.stderr.write(f"Error: {e}\n")
        raise Exit(code=1)


if __name__ == "__main__":
    app()
