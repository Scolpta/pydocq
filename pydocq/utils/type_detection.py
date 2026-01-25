"""Centralized element type detection utilities.

This module provides the SINGLE source of truth for element type detection
across the entire pydocq project, eliminating code duplication and ensuring
consistent behavior.
"""

import inspect
from enum import Enum
from typing import Any


class ElementType(Enum):
    """Type of Python element."""

    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    PROPERTY = "property"
    UNKNOWN = "unknown"


# Type detection function order matters (more specific types first)
_TYPE_CHECKS = [
    # Modules first (most general)
    (inspect.ismodule, ElementType.MODULE),
    # Then classes
    (inspect.isclass, ElementType.CLASS),
    # Then functions (before methods)
    (inspect.isfunction, ElementType.FUNCTION),
    # Then methods (bound functions)
    (inspect.ismethod, ElementType.METHOD),
    # Then properties
    (lambda obj: isinstance(obj, property), ElementType.PROPERTY),
]


def get_element_type(obj: Any) -> ElementType:
    """Determine the type of a Python object.

    This is the SINGLE source of truth for element type detection
    across the entire pydocq project.

    Args:
        obj: Python object to classify

    Returns:
        ElementType enum value

    Examples:
        >>> import os
        >>> get_element_type(os)
        <ElementType.MODULE: 'module'>
        >>> get_element_type(str)
        <ElementType.CLASS: 'class'>
        >>> get_element_type(len)
        <ElementType.FUNCTION: 'function'>
    """
    for check_func, element_type in _TYPE_CHECKS:
        if check_func(obj):
            return element_type

    return ElementType.UNKNOWN


def is_public_element(obj: Any, name: str | None = None) -> bool:
    """Check if an element is public (not private).

    Args:
        obj: Python object to check
        name: Optional name string (if available, avoids name lookup)

    Returns:
        True if element is public, False if private
    """
    if name is None:
        name = getattr(obj, "__name__", "")

    # Private if starts with underscore (but not __dunder__)
    if name.startswith("_"):
        # Dunder methods are considered public
        return name.startswith("__") and name.endswith("__")
    return True


def get_element_name(obj: Any) -> str:
    """Get the name of an element safely.

    Args:
        obj: Python object

    Returns:
        Element name or empty string if not available
    """
    return getattr(obj, "__name__", "")


def get_element_qualname(obj: Any) -> str:
    """Get the qualified name of an element safely.

    Args:
        obj: Python object

    Returns:
        Qualified name or empty string if not available
    """
    return getattr(obj, "__qualname__", "")


def is_callable(obj: Any) -> bool:
    """Check if an object is callable (excluding classes).

    Args:
        obj: Python object to check

    Returns:
        True if callable and not a class
    """
    if inspect.isclass(obj):
        return False
    return callable(obj)
