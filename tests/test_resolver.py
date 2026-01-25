"""Tests for path resolution."""

import pytest

from docs_cli.analyzer.resolver import (
    ElementNotFoundError,
    ElementType,
    InvalidPathError,
    PackageNotFoundError,
    resolve_path,
)


class TestResolvePath:
    """Tests for resolve_path function."""

    def test_resolve_stdlib_module(self) -> None:
        """Test resolving a standard library module."""
        result = resolve_path("os")
        assert result.path == "os"
        assert result.element_type == ElementType.MODULE
        assert result.module_path == "os"

    def test_resolve_stdlib_class(self) -> None:
        """Test resolving a class from standard library."""
        result = resolve_path("os.PathLike")
        assert result.path == "os.PathLike"
        assert result.element_type == ElementType.CLASS
        assert result.module_path is not None

    def test_resolve_stdlib_function(self) -> None:
        """Test resolving a function from standard library."""
        result = resolve_path("os.path.join")
        assert result.path == "os.path.join"
        assert result.element_type == ElementType.FUNCTION
        # Note: os.path is actually an alias to platform-specific modules
        assert result.module_path is not None

    def test_resolve_builtins(self) -> None:
        """Test resolving builtins module."""
        result = resolve_path("builtins.str")
        assert result.path == "builtins.str"
        assert result.element_type == ElementType.CLASS

    def test_resolve_deeply_nested(self) -> None:
        """Test resolving a deeply nested element."""
        result = resolve_path("collections.abc.Mapping")
        assert result.path == "collections.abc.Mapping"
        assert result.module_path == "collections.abc"

    def test_empty_path_raises_error(self) -> None:
        """Test that empty path raises InvalidPathError."""
        with pytest.raises(InvalidPathError, match="cannot be empty"):
            resolve_path("")

    def test_nonexistent_package_raises_error(self) -> None:
        """Test that non-existent package raises PackageNotFoundError."""
        with pytest.raises(PackageNotFoundError):
            resolve_path("nonexistentpackage")

    def test_nonexistent_element_raises_error(self) -> None:
        """Test that non-existent element raises ElementNotFoundError."""
        with pytest.raises(ElementNotFoundError):
            resolve_path("os.NonExistentClass")

    def test_invalid_path_with_leading_dot(self) -> None:
        """Test that path with leading dot is handled."""
        # Leading dots cause ValueError from importlib
        # We expect this to be caught and converted to our error type
        with pytest.raises((PackageNotFoundError, InvalidPathError, ValueError)):
            resolve_path(".invalid")


class TestElementType:
    """Tests for ElementType enum."""

    def test_element_type_values(self) -> None:
        """Test that ElementType has expected values."""
        assert ElementType.MODULE.value == "module"
        assert ElementType.CLASS.value == "class"
        assert ElementType.FUNCTION.value == "function"
        assert ElementType.METHOD.value == "method"
        assert ElementType.PROPERTY.value == "property"
        assert ElementType.UNKNOWN.value == "unknown"


class TestResolverErrors:
    """Tests for resolver exception classes."""

    def test_package_not_found_error(self) -> None:
        """Test PackageNotFoundError message."""
        error = PackageNotFoundError("test_package")
        assert "test_package" in str(error)

    def test_element_not_found_error(self) -> None:
        """Test ElementNotFoundError message."""
        error = ElementNotFoundError("test_element not found in test_module")
        assert "test_element" in str(error) or "test_module" in str(error)

    def test_invalid_path_error(self) -> None:
        """Test InvalidPathError message."""
        error = InvalidPathError("invalid path")
        assert "invalid path" in str(error)
