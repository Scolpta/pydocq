"""Path resolution for Python packages and elements."""

import importlib
from dataclasses import dataclass
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


@dataclass
class ResolvedElement:
    """A resolved Python element."""

    path: str
    element_type: ElementType
    obj: Any
    module_path: str | None = None
    parent: Any | None = None


class ResolverError(Exception):
    """Base exception for resolver errors."""

    pass


class PackageNotFoundError(ResolverError):
    """Raised when a package cannot be found or imported."""

    pass


class ElementNotFoundError(ResolverError):
    """Raised when an element cannot be found in a module."""

    pass


class InvalidPathError(ResolverError):
    """Raised when a path string is invalid."""

    pass


def resolve_path(path_string: str) -> ResolvedElement:
    """Resolve a path string to an actual Python element.

    Args:
        path_string: Path like 'pandas.DataFrame' or 'pandas.core.frame.DataFrame.merge'

    Returns:
        ResolvedElement with the actual Python object

    Raises:
        InvalidPathError: If path string is invalid
        PackageNotFoundError: If package cannot be imported
        ElementNotFoundError: If element cannot be found
    """
    if not path_string:
        raise InvalidPathError("Path string cannot be empty")

    # Split the path into components
    parts = path_string.split(".")

    if not parts:
        raise InvalidPathError(f"Invalid path: {path_string}")

    # The first part is always the package name
    package_name = parts[0]

    try:
        # Try to import the package/module
        module = importlib.import_module(package_name)
    except ImportError as e:
        raise PackageNotFoundError(
            f"Package or module '{package_name}' not found or cannot be imported"
        ) from e

    # If only package name provided, return the module
    if len(parts) == 1:
        return ResolvedElement(
            path=path_string,
            element_type=ElementType.MODULE,
            obj=module,
            module_path=package_name,
        )

    # Navigate deeper into the path
    current = module
    current_path = package_name

    for part in parts[1:]:
        try:
            # Try to get attribute from current object
            current = getattr(current, part)
            current_path = f"{current_path}.{part}"
        except AttributeError as e:
            # Check if it might be a submodule
            module_path = f"{current_path}.{part}"
            try:
                current = importlib.import_module(module_path)
                current_path = module_path
            except ImportError:
                raise ElementNotFoundError(
                    f"Element '{part}' not found in '{current_path}'"
                ) from e

    # Determine the element type
    element_type = _determine_element_type(current)

    return ResolvedElement(
        path=path_string,
        element_type=element_type,
        obj=current,
        module_path=_get_module_path(current),
    )


def _determine_element_type(obj: Any) -> ElementType:
    """Determine the type of a Python object.

    Args:
        obj: Python object to classify

    Returns:
        ElementType enum value
    """
    import inspect

    if inspect.ismodule(obj):
        return ElementType.MODULE
    if inspect.isclass(obj):
        return ElementType.CLASS
    if inspect.isfunction(obj):
        return ElementType.FUNCTION
    if inspect.ismethod(obj):
        return ElementType.METHOD
    if isinstance(obj, property):
        return ElementType.PROPERTY
    return ElementType.UNKNOWN


def _get_module_path(obj: Any) -> str | None:
    """Get the module path for an object.

    Args:
        obj: Python object

    Returns:
        Module path string or None
    """
    import inspect

    try:
        module = inspect.getmodule(obj)
        if module is not None:
            return module.__name__
    except Exception:
        pass

    return None
