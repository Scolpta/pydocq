"""Path resolution for Python packages and elements."""

import importlib
import re
from dataclasses import dataclass
from typing import Any

from docs_cli.analyzer.errors import (
    ElementNotFoundError,
    InvalidPathError,
    PackageNotFoundError,
    SecurityError,
)
from docs_cli.utils.type_detection import ElementType, get_element_type


# Blacklist of dangerous modules that should not be imported
_DANGEROUS_MODULES = {
    "subprocess",
    "multiprocessing",
    "threading",
    "socket",
    "ssl",
    "http",
    "urllib",
    "urllib2",
    "httplib",
    "ftplib",
    "telnetlib",
    "pickle",
    "shelve",
    "marshal",
    "eval",
    "exec",
}

# Blacklist of dangerous module paths that should not be accessed
_DANGEROUS_PATHS = {
    "os.system",
    "os.popen",
    "os.spawn",
    "os.fork",
    "os.exec",
    "os.posix_spawn",
}


@dataclass
class ResolvedElement:
    """A resolved Python element."""

    path: str
    element_type: ElementType
    obj: Any
    module_path: str | None = None
    parent: Any | None = None


def _validate_package_name(package_name: str) -> None:
    """Validate that a package name is safe to import.

    Args:
        package_name: Name of the package to validate

    Raises:
        SecurityError: If the package name is dangerous or invalid
    """
    # Check for path traversal attempts
    if ".." in package_name or package_name.startswith(("/", "\\")):
        raise SecurityError(
            f"Path traversal detected in package name: {package_name}"
        )

    # Check for absolute paths
    if re.match(r'^[a-zA-Z_]', package_name) and not re.match(r'^[a-zA-Z_][a-zA-Z0-9_\.]*$', package_name):
        raise SecurityError(
            f"Invalid package name format: {package_name}. "
            "Package names must be valid Python identifiers separated by dots."
        )

    # Check against dangerous modules blacklist
    if package_name in _DANGEROUS_MODULES:
        raise SecurityError(
            f"Import of module '{package_name}' is not allowed for security reasons"
        )

    # Check if package name starts with underscore (private/internal)
    if package_name.startswith("_"):
        raise SecurityError(
            f"Import of private module '{package_name}' is not allowed"
        )


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
        SecurityError: If path contains dangerous or invalid components
    """
    if not path_string:
        raise InvalidPathError("Path string cannot be empty")

    # Split the path into components
    parts = path_string.split(".")

    if not parts:
        raise InvalidPathError(f"Invalid path: {path_string}")

    # Check for empty parts (resulting from .. or leading/trailing dots)
    if any(part == "" for part in parts):
        raise SecurityError(
            f"Path traversal detected in package name: {path_string}"
        )

    # The first part is always the package name
    package_name = parts[0]

    # Validate package name for security
    _validate_package_name(package_name)

    # Validate all parts against dangerous modules blacklist
    for part in parts:
        if part in _DANGEROUS_MODULES:
            raise SecurityError(
                f"Import of module '{part}' is not allowed for security reasons"
            )

    # Validate path combinations against dangerous paths blacklist
    # Build paths incrementally (e.g., for "os.system", check both "os" and "os.system")
    current_path = parts[0]
    for part in parts[1:]:
        current_path = f"{current_path}.{part}"
        if current_path in _DANGEROUS_PATHS:
            raise SecurityError(
                f"Access to '{current_path}' is not allowed for security reasons"
            )

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
    element_type = get_element_type(current)

    return ResolvedElement(
        path=path_string,
        element_type=element_type,
        obj=current,
        module_path=_get_module_path(current),
    )


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
