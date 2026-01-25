"""Output format handlers for different documentation formats.

This module provides specialized formatters for different output formats
beyond the standard JSON format.
"""

import inspect
import json
import sys
from typing import Any

from docs_cli.analyzer.inspector import InspectedElement
from docs_cli.analyzer.resolver import ElementType


def format_raw(inspected: InspectedElement) -> str:
    """Format output as raw text (human-readable).

    Args:
        inspected: The InspectedElement to format

    Returns:
        Raw text representation
    """
    lines = []

    # Header
    lines.append(f"Path: {inspected.path}")
    lines.append(f"Type: {inspected.element_type.value}")
    if inspected.module_path:
        lines.append(f"Module: {inspected.module_path}")

    # Signature
    if inspected.signature:
        lines.append("\nSignature:")
        if inspected.signature.parameters:
            for param in inspected.signature.parameters:
                param_str = f"  {param['name']}"
                if param.get('annotation'):
                    param_str += f": {param['annotation']}"
                if param.get('kind'):
                    param_str += f"  # {param['kind']}"
                if param.get('default'):
                    param_str += f" = {param['default']}"
                lines.append(param_str)
        else:
            lines.append("  (no parameters)")

        if inspected.signature.return_type:
            lines.append(f"  -> {inspected.signature.return_type}")

    # Docstring
    if inspected.docstring and inspected.docstring.docstring:
        lines.append("\nDocstring:")
        lines.append(f"  Length: {inspected.docstring.length} characters")
        if inspected.docstring.has_examples:
            lines.append("  Contains examples: Yes")
        lines.append("\n  " + inspected.docstring.docstring.replace('\n', '\n  '))

    # Source location
    if inspected.source_location:
        lines.append("\nSource Location:")
        if inspected.source_location.file:
            lines.append(f"  File: {inspected.source_location.file}")
        if inspected.source_location.line:
            lines.append(f"  Line: {inspected.source_location.line}")

    return '\n'.join(lines)


def format_signature(inspected: InspectedElement) -> str:
    """Format output as function/class signature only.

    Args:
        inspected: The InspectedElement to format

    Returns:
        Signature string
    """
    if not inspected.signature or not inspected.signature.parameters:
        return f"{inspected.path}()"

    # Build signature string
    params = []
    for param in inspected.signature.parameters:
        param_str = param['name']
        if param.get('annotation'):
            param_str += f": {param['annotation']}"
        if param.get('default'):
            param_str += f" = {param['default']}"
        params.append(param_str)

    sig_str = f"{inspected.path}({', '.join(params)})"

    if inspected.signature.return_type:
        sig_str += f" -> {inspected.signature.return_type}"

    return sig_str


def format_markdown(inspected: InspectedElement) -> str:
    """Format output as Markdown documentation.

    Args:
        inspected: The InspectedElement to format

    Returns:
        Markdown string
    """
    lines = []

    # Title
    lines.append(f"# `{inspected.path}`")
    lines.append("")

    # Metadata table
    lines.append("| Property | Value |")
    lines.append("|----------|-------|")
    lines.append(f"| **Type** | {inspected.element_type.value} |")
    if inspected.module_path:
        lines.append(f"| **Module** | `{inspected.module_path}` |")
    lines.append("")

    # Signature
    if inspected.signature:
        lines.append("## Signature")
        lines.append("")
        lines.append("```python")
        lines.append(format_signature(inspected))
        lines.append("```")
        lines.append("")

        # Parameters table
        if inspected.signature.parameters:
            lines.append("### Parameters")
            lines.append("")
            lines.append("| Name | Type | Default | Description |")
            lines.append("|------|------|---------|-------------|")
            for param in inspected.signature.parameters:
                name = param['name']
                annotation = param.get('annotation') or '-'
                default = str(param.get('default')) if param.get('default') else '-'
                lines.append(f"| {name} | {annotation} | {default} | |")
            lines.append("")

        # Return type
        if inspected.signature.return_type:
            lines.append(f"**Returns:** `{inspected.signature.return_type}`")
            lines.append("")

    # Docstring
    if inspected.docstring and inspected.docstring.docstring:
        lines.append("## Documentation")
        lines.append("")
        lines.append(inspected.docstring.docstring)
        lines.append("")

    # Source location
    if inspected.source_location and inspected.source_location.file:
        lines.append("## Source")
        lines.append("")
        if inspected.source_location.file:
            lines.append(f"**File:** `{inspected.source_location.file}`")
        if inspected.source_location.line:
            lines.append(f"**Line:** {inspected.source_location.line}")
        lines.append("")

    return '\n'.join(lines)


def format_yaml(inspected: InspectedElement) -> str:
    """Format output as YAML.

    Args:
        inspected: The InspectedElement to format

    Returns:
        YAML string
    """
    # Use JSON and convert to YAML-like structure
    # For now, return JSON since YAML requires additional dependency
    data = {
        "path": inspected.path,
        "type": inspected.element_type.value,
    }

    if inspected.module_path:
        data["module"] = inspected.module_path

    if inspected.signature:
        data["signature"] = {
            "parameters": inspected.signature.parameters,
            "return_type": inspected.signature.return_type,
        }

    if inspected.docstring and inspected.docstring.docstring:
        data["docstring"] = {
            "content": inspected.docstring.docstring,
            "length": inspected.docstring.length,
        }
        if inspected.docstring.has_examples:
            data["docstring"]["has_examples"] = True

    if inspected.source_location:
        loc = {}
        if inspected.source_location.file:
            loc["file"] = inspected.source_location.file
        if inspected.source_location.line:
            loc["line"] = inspected.source_location.line
        if loc:
            data["source_location"] = loc

    return json.dumps(data, indent=2)


def get_formatter(format_type: str):
    """Get the formatter function for a given format type.

    Args:
        format_type: The format type (json, raw, signature, markdown, yaml)

    Returns:
        Formatter function

    Raises:
        ValueError: If format_type is not supported
    """
    formatters = {
        "json": lambda x: json.dumps(
            {
                "path": x.path,
                "type": x.element_type.value,
                "module_path": x.module_path,
            },
            indent=2,
        ),
        "raw": format_raw,
        "signature": format_signature,
        "markdown": format_markdown,
        "yaml": format_yaml,
    }

    if format_type not in formatters:
        raise ValueError(
            f"Unsupported format '{format_type}'. "
            f"Supported formats: {', '.join(formatters.keys())}"
        )

    return formatters[format_type]
