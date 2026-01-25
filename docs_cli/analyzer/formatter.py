"""JSON formatting for inspected elements.

This module provides functions to convert inspected elements to JSON-serializable
dictionaries for output.
"""

import inspect
from datetime import datetime
from pathlib import Path

from docs_cli.analyzer.inspector import InspectedElement
from docs_cli.analyzer.resolver import ElementType


def format_json(
    inspected: InspectedElement,
    include_source: bool = False,
    include_docstring: bool = True,
    include_signature: bool = True,
    include_metadata: bool = False,
) -> dict:
    """Format an inspected element as JSON-serializable dictionary.

    Args:
        inspected: The InspectedElement to format
        include_source: Whether to include source location information
        include_docstring: Whether to include docstring information
        include_signature: Whether to include signature information
        include_metadata: Whether to include SDK metadata

    Returns:
        JSON-serializable dictionary with element information
    """
    output = {
        "path": inspected.path,
        "type": inspected.element_type.value,
        "module_path": inspected.module_path,
    }

    # Add signature information if available and requested
    if include_signature and inspected.signature is not None:
        output["signature"] = _format_signature(inspected.signature)

    # Add docstring information if available and requested
    if include_docstring and inspected.docstring is not None:
        output["docstring"] = _format_docstring(inspected.docstring)

    # Add source location if available and requested
    if include_source and inspected.source_location is not None:
        output["source_location"] = _format_source_location(
            inspected.source_location
        )

    # Add SDK metadata if available and requested
    if include_metadata and inspected.sdk_metadata:
        output["sdk_metadata"] = inspected.sdk_metadata

    return output


def _format_signature(signature) -> dict:
    """Format a SignatureInfo for JSON output.

    Args:
        signature: SignatureInfo object

    Returns:
        JSON-serializable dictionary
    """
    return {
        "parameters": signature.parameters,
        "return_type": signature.return_type,
    }


def _format_docstring(docstring) -> dict:
    """Format a DocstringInfo for JSON output.

    Args:
        docstring: DocstringInfo object

    Returns:
        JSON-serializable dictionary
    """
    output = {
        "docstring": docstring.docstring,
        "length": docstring.length,
    }

    # Only add has_examples if it's True (to avoid cluttering output)
    if docstring.has_examples:
        output["has_examples"] = True

    return output


def _format_source_location(source_location) -> dict:
    """Format a SourceLocation for JSON output.

    Args:
        source_location: SourceLocation object

    Returns:
        JSON-serializable dictionary
    """
    output = {}

    if source_location.file is not None:
        output["file"] = source_location.file

    if source_location.line is not None:
        output["line"] = source_location.line

    return output


def format_json_compact(inspected: InspectedElement) -> dict:
    """Format an inspected element as minimal JSON output.

    This is a compact version with only essential information.

    Args:
        inspected: The InspectedElement to format

    Returns:
        JSON-serializable dictionary with minimal information
    """
    return {
        "path": inspected.path,
        "type": inspected.element_type.value,
        "module_path": inspected.module_path,
    }


def format_json_verbose(inspected: InspectedElement) -> dict:
    """Format an inspected element as verbose JSON output.

    This includes all available information.

    Args:
        inspected: The InspectedElement to format

    Returns:
        JSON-serializable dictionary with all information
    """
    return format_json(
        inspected,
        include_source=True,
        include_docstring=True,
        include_signature=True,
        include_metadata=True,
    )
