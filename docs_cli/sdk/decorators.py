"""SDK decorators for adding custom metadata to Python code.

This module provides decorators that allow developers to add custom metadata
to their Python code for better documentation and AI agent understanding.

The decorators are non-opinionated and don't affect runtime behavior.
They only store metadata that can be retrieved by docs-cli.
"""

import functools
import inspect
from typing import Any, Callable


# Global metadata storage
# Maps object IDs to their metadata
_METADATA_STORE: dict[int, dict] = {}


class Metadata:
    """Metadata container for Python objects."""

    def __init__(self, **kwargs: Any) -> None:
        """Initialize metadata with key-value pairs.

        Args:
            **kwargs: Arbitrary metadata key-value pairs
        """
        self.data = kwargs

    def get(self, key: str, default: Any = None) -> Any:
        """Get a metadata value.

        Args:
            key: Metadata key
            default: Default value if key not found

        Returns:
            Metadata value or default
        """
        return self.data.get(key, default)

    def to_dict(self) -> dict:
        """Convert metadata to dictionary.

        Returns:
            Dictionary of all metadata
        """
        return self.data.copy()


def metadata(**kwargs: Any) -> Callable:
    """Generic decorator for adding custom metadata.

    This decorator allows adding arbitrary key-value pairs as metadata
    to any Python object (function, class, method).

    Usage:
        @metadata(category="data", version="1.0")
        def my_function():
            pass

        @metadata(author="John Doe", tags=["important", "api"])
        class MyClass:
            pass

    Args:
        **kwargs: Arbitrary metadata key-value pairs

    Returns:
        Decorator function
    """

    def decorator(obj: Any) -> Any:
        # Store metadata by object id
        obj_id = id(obj)
        _METADATA_STORE[obj_id] = kwargs

        # Attach metadata as attribute for easy access
        if not hasattr(obj, "__docs_metadata__"):
            obj.__docs_metadata__ = Metadata(**kwargs)
        else:
            # Merge with existing metadata
            obj.__docs_metadata__.data.update(kwargs)

        return obj

    return decorator


def example(code: str, description: str | None = None) -> Callable:
    """Add code example to function or class.

    Usage:
        @example("x = my_func(42)", "Example usage")
        def my_func(x):
            return x * 2

    Args:
        code: Example code snippet
        description: Optional description of the example

    Returns:
        Decorator function
    """
    return metadata(example={"code": code, "description": description})


def deprecated(
    reason: str | None = None, since: str | None = None, version: str | None = None
) -> Callable:
    """Mark a function or class as deprecated.

    Usage:
        @deprecated("Use new_func instead", since="1.0", version="2.0")
        def old_func():
            pass

    Args:
        reason: Reason for deprecation
        since: Version when deprecation was introduced
        version: Version when removal is planned

    Returns:
        Decorator function
    """
    return metadata(deprecated={"reason": reason, "since": since, "version": version})


def param(name: str, **info: Any) -> Callable:
    """Add parameter documentation.

    Usage:
        @param("x", type="int", description="The input value")
        def my_func(x):
            return x * 2

    Args:
        name: Parameter name
        **info: Parameter information (type, description, etc.)

    Returns:
        Decorator function
    """
    return metadata(params={name: info})


def returns(**info: Any) -> Callable:
    """Add return value documentation.

    Usage:
        @returns(type="int", description="The result")
        def my_func():
            return 42

    Args:
        **info: Return value information

    Returns:
        Decorator function
    """
    return metadata(returns=info)


def category(*categories: str) -> Callable:
    """Categorize a function or class.

    Usage:
        @category("api", "public")
        def my_func():
            pass

    Args:
        *categories: Category names

    Returns:
        Decorator function
    """
    return metadata(category=list(categories))


def when(version: str, condition: str | None = None) -> Callable:
    """Add version or condition information.

    Usage:
        @when(version="1.0", condition="stable")
        def my_func():
            pass

    Args:
        version: Version string
        condition: Optional condition (e.g., "stable", "experimental")

    Returns:
        Decorator function
    """
    return metadata(when={"version": version, "condition": condition})


def tag(*tags: str) -> Callable:
    """Add tags to function or class.

    Usage:
        @tag("important", "api", "v2")
        def my_func():
            pass

    Args:
        *tags: Tag names

    Returns:
        Decorator function
    """
    return metadata(tags=list(tags))


def note(text: str) -> Callable:
    """Add a note to function or class.

    Usage:
        @note("This is an important note")
        def my_func():
            pass

    Args:
        text: Note text

    Returns:
        Decorator function
    """
    return metadata(notes=[text])


def author(name: str, email: str | None = None) -> Callable:
    """Add author information.

    Usage:
        @author("John Doe", "john@example.com")
        def my_func():
            pass

    Args:
        name: Author name
        email: Optional author email

    Returns:
        Decorator function
    """
    return metadata(author={"name": name, "email": email})


def see_also(*references: str) -> Callable:
    """Add cross-references.

    Usage:
        @see_also("other_func", "MyClass.method")
        def my_func():
            pass

    Args:
        *references: Reference strings

    Returns:
        Decorator function
    """
    return metadata(see_also=list(references))


def get_metadata(obj: Any) -> Metadata | None:
    """Get metadata for an object.

    Args:
        obj: Python object

    Returns:
        Metadata object or None if no metadata
    """
    # Check attached metadata first
    if hasattr(obj, "__docs_metadata__"):
        return obj.__docs_metadata__

    # Check metadata store
    obj_id = id(obj)
    if obj_id in _METADATA_STORE:
        return Metadata(**_METADATA_STORE[obj_id])

    return None


def get_metadata_dict(obj: Any) -> dict:
    """Get metadata for an object as a dictionary.

    Args:
        obj: Python object

    Returns:
        Dictionary of metadata or empty dict
    """
    meta = get_metadata(obj)
    if meta:
        return meta.to_dict()
    return {}


def clear_metadata() -> None:
    """Clear all metadata from the store.

    This is primarily useful for testing.
    """
    global _METADATA_STORE
    _METADATA_STORE = {}
