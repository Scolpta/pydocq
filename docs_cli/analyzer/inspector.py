"""Runtime introspection using Python's inspect module.

This module provides functions to extract information from Python objects
at runtime using the inspect module.
"""

import inspect
from dataclasses import dataclass, field
from typing import Any

from docs_cli.analyzer.resolver import ElementType, ResolvedElement


@dataclass
class SignatureInfo:
    """Information about a function or method signature."""

    parameters: list[dict] = field(default_factory=list)
    return_type: str | None = None
    return_annotation: Any = None


@dataclass
class DocstringInfo:
    """Information about a docstring."""

    docstring: str | None = None
    length: int = 0
    has_examples: bool = False


@dataclass
class SourceLocation:
    """Information about the source location of an element."""

    file: str | None = None
    line: int | None = None


@dataclass
class InspectedElement:
    """Complete information about an inspected element."""

    path: str
    element_type: ElementType
    obj: Any
    signature: SignatureInfo | None = None
    docstring: DocstringInfo | None = None
    source_location: SourceLocation | None = None
    module_path: str | None = None
    sdk_metadata: dict | None = None


def get_signature(obj: Any) -> SignatureInfo:
    """Extract signature information from a callable object.

    Args:
        obj: A callable object (function, method, etc.)

    Returns:
        SignatureInfo with parameters and return type
    """
    try:
        sig = inspect.signature(obj)
    except (ValueError, TypeError):
        # Object doesn't have a signature
        return SignatureInfo()

    parameters = []
    for name, param in sig.parameters.items():
        param_info = {
            "name": name,
            "kind": str(param.kind),
            "default": str(param.default) if param.default != param.empty else None,
            "annotation": str(param.annotation) if param.annotation != param.empty else None,
        }
        parameters.append(param_info)

    return_type = None
    if sig.return_annotation != inspect.Parameter.empty:
        return_type = str(sig.return_annotation)

    return SignatureInfo(
        parameters=parameters,
        return_type=return_type,
        return_annotation=sig.return_annotation,
    )


def get_docstring(obj: Any) -> DocstringInfo:
    """Extract and analyze docstring from an object.

    Args:
        obj: Any Python object

    Returns:
        DocstringInfo with docstring content and metadata
    """
    doc = inspect.getdoc(obj)

    if doc is None:
        return DocstringInfo()

    return DocstringInfo(
        docstring=doc,
        length=len(doc),
        has_examples=_check_for_examples(doc),
    )


def _check_for_examples(docstring: str) -> bool:
    """Check if docstring contains code examples.

    Args:
        docstring: The docstring to check

    Returns:
        True if examples are detected, False otherwise
    """
    doc_lower = docstring.lower()

    # Check for common example indicators
    example_indicators = [
        "example:",
        "examples:",
        ">>>",
        "usage:",
        "::",  # reStructuredText directive
    ]

    return any(indicator in doc_lower for indicator in example_indicators)


def get_source_location(obj: Any) -> SourceLocation:
    """Get source file location for an object.

    Args:
        obj: Any Python object

    Returns:
        SourceLocation with file and line number
    """
    try:
        file = inspect.getsourcefile(obj)
        lines, lineno = inspect.getsourcelines(obj)
    except (TypeError, OSError):
        # Built-in objects, C extensions, etc.
        return SourceLocation()

    return SourceLocation(
        file=file,
        line=lineno,
    )


def inspect_element(element: ResolvedElement) -> InspectedElement:
    """Perform complete inspection of a resolved element.

    Args:
        element: A ResolvedElement to inspect

    Returns:
        InspectedElement with complete information
    """
    # Get signature if it's a callable
    signature = None
    if element.element_type in (ElementType.FUNCTION, ElementType.METHOD):
        signature = get_signature(element.obj)
    elif element.element_type == ElementType.CLASS:
        # Classes have __init__ signature
        try:
            if hasattr(element.obj, "__init__"):
                signature = get_signature(element.obj.__init__)
        except Exception:
            pass

    # Get docstring
    docstring = get_docstring(element.obj)

    # Get source location
    source_location = get_source_location(element.obj)

    # Get SDK metadata
    sdk_metadata = None
    try:
        from docs_cli.sdk import get_metadata_dict

        sdk_metadata = get_metadata_dict(element.obj)
        if not sdk_metadata:
            sdk_metadata = None
    except ImportError:
        pass

    return InspectedElement(
        path=element.path,
        element_type=element.element_type,
        obj=element.obj,
        signature=signature,
        docstring=docstring,
        source_location=source_location,
        module_path=element.module_path,
        sdk_metadata=sdk_metadata,
    )
