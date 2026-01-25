"""Tests for path resolution."""

import pytest

from pydocq.analyzer.resolver import (
    ElementNotFoundError,
    InvalidPathError,
    PackageNotFoundError,
    SecurityError,
    resolve_path,
)
from pydocq.utils.type_detection import ElementType


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
        # Leading dots cause ValueError from importlib or SecurityError from our validation
        # We expect this to be caught and converted to our error type
        with pytest.raises((PackageNotFoundError, InvalidPathError, ValueError, SecurityError)):
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


class TestResolverSecurity:
    """Tests for resolver security validation."""

    def test_dangerous_module_subprocess_blocked(self) -> None:
        """Test that subprocess module is blocked."""
        with pytest.raises(SecurityError, match="not allowed for security reasons"):
            resolve_path("subprocess")

    def test_dangerous_module_os_system_blocked(self) -> None:
        """Test that os.system is blocked."""
        with pytest.raises(SecurityError, match="not allowed for security reasons"):
            resolve_path("os.system")

    def test_dangerous_module_multiprocessing_blocked(self) -> None:
        """Test that multiprocessing module is blocked."""
        with pytest.raises(SecurityError, match="not allowed for security reasons"):
            resolve_path("multiprocessing")

    def test_dangerous_module_threading_blocked(self) -> None:
        """Test that threading module is blocked."""
        with pytest.raises(SecurityError, match="not allowed for security reasons"):
            resolve_path("threading")

    def test_dangerous_module_socket_blocked(self) -> None:
        """Test that socket module is blocked."""
        with pytest.raises(SecurityError, match="not allowed for security reasons"):
            resolve_path("socket")

    def test_dangerous_module_ssl_blocked(self) -> None:
        """Test that ssl module is blocked."""
        with pytest.raises(SecurityError, match="not allowed for security reasons"):
            resolve_path("ssl")

    def test_dangerous_module_http_blocked(self) -> None:
        """Test that http module is blocked."""
        with pytest.raises(SecurityError, match="not allowed for security reasons"):
            resolve_path("http")

    def test_dangerous_module_urllib_blocked(self) -> None:
        """Test that urllib module is blocked."""
        with pytest.raises(SecurityError, match="not allowed for security reasons"):
            resolve_path("urllib")

    def test_dangerous_module_pickle_blocked(self) -> None:
        """Test that pickle module is blocked."""
        with pytest.raises(SecurityError, match="not allowed for security reasons"):
            resolve_path("pickle")

    def test_dangerous_module_eval_blocked(self) -> None:
        """Test that eval is blocked."""
        with pytest.raises(SecurityError, match="not allowed for security reasons"):
            resolve_path("eval")

    def test_dangerous_module_exec_blocked(self) -> None:
        """Test that exec is blocked."""
        with pytest.raises(SecurityError, match="not allowed for security reasons"):
            resolve_path("exec")

    def test_path_traversal_with_double_dot(self) -> None:
        """Test that path traversal with .. is blocked."""
        with pytest.raises(SecurityError, match="Path traversal detected"):
            resolve_path("os../subprocess")

    def test_path_traversal_with_leading_slash(self) -> None:
        """Test that path traversal with leading / is blocked."""
        with pytest.raises(SecurityError, match="Path traversal detected"):
            resolve_path("/etc/passwd")

    def test_path_traversal_with_leading_backslash(self) -> None:
        """Test that path traversal with leading \\ is blocked."""
        with pytest.raises(SecurityError, match="Path traversal detected"):
            resolve_path("\\windows\\system32")

    def test_private_module_rejected(self) -> None:
        """Test that modules starting with underscore are rejected."""
        with pytest.raises(SecurityError, match="private module.*not allowed"):
            resolve_path("_private")

    def test_invalid_package_name_format(self) -> None:
        """Test that invalid package name formats are rejected."""
        with pytest.raises(SecurityError, match="Invalid package name format"):
            resolve_path("pkg-with-dash")

    def test_invalid_package_name_with_special_chars(self) -> None:
        """Test that special characters in package name are rejected."""
        with pytest.raises(SecurityError, match="Invalid package name format"):
            resolve_path("pkg@#$")

    def test_valid_module_with_underscore_in_name(self) -> None:
        """Test that valid modules with underscores are allowed."""
        # This should work - underscore is valid in Python identifiers
        result = resolve_path("builtins.__import__")
        assert result.path == "builtins.__import__"

    def test_os_module_allowed_but_os_system_blocked(self) -> None:
        """Test that os module is allowed but os.system is not."""
        # os module itself should work
        result = resolve_path("os")
        assert result.path == "os"
        assert result.element_type == ElementType.MODULE

        # But os.system should be blocked
        with pytest.raises(SecurityError, match="not allowed for security reasons"):
            resolve_path("os.system")
