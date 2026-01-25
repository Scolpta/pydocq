# Issue QUAL-002: Exception Handling Inconsistencies

## Description

The project has two parallel exception hierarchies that are not integrated:

1. **Base exceptions in `resolver.py`**: `ResolverError`, `PackageNotFoundError`, `ElementNotFoundError`, `InvalidPathError`
2. **Enhanced exceptions in `errors.py`**: `DocsCliError`, `ResolutionError`, `InspectionError`, `FormattingError`, etc.

The CLI (`cli.py`) only catches and uses the base resolver exceptions, while the enhanced exceptions in `errors.py` are defined but unused, creating confusion and inconsistency.

## Problem Details

### Exception Hierarchy 1: Base Exceptions (Used)

```python
# docs_cli/analyzer/resolver.py:31-52
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
```

### Exception Hierarchy 2: Enhanced Exceptions (Unused)

```python
# docs_cli/analyzer/errors.py:18-72
class DocsCliError(Exception):
    """Base exception for docs-cli errors."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict:
        """Convert error to dictionary for JSON output."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            **self.details,
        }

class ResolutionError(DocsCliError):
    """Error during path resolution."""
    pass

class InspectionError(DocsCliError):
    """Error during element inspection."""
    pass

class FormattingError(DocsCliError):
    """Error during output formatting."""
    pass
```

### CLI Usage (Only Catches Base Exceptions)

```python
# docs_cli/cli.py:158-164
except (InvalidPathError, PackageNotFoundError, ElementNotFoundError) as e:
    sys.stderr.write(f"Error: {e}\n")
    raise Exit(code=1)
except ValueError as e:
    sys.stderr.write(f"Error: {e}\n")
    raise Exit(code=1)
```

### Issues Identified

| Issue | Impact | Severity |
|-------|--------|----------|
| **Unused Code** | Enhanced exceptions defined but never used | Medium |
| **Inconsistent Error Handling** | Some modules use one hierarchy, others another | Medium |
| **Missing Features** | `to_dict()` and error details not utilized | Medium |
| **Confusion** | Developers don't know which exceptions to use/raise | Medium |
| **Maintenance Burden** | Two parallel systems to maintain | Low |

### Example of Inconsistency

```python
# In resolver.py - raises base exception
raise PackageNotFoundError(f"Package '{name}' not found")

# In errors.py - has enhanced version but it's not used
# ResolutionError has .to_dict() method and details support
# But resolver.py doesn't use it!
```

## Impact Assessment

| Impact Type | Severity | Description |
|-------------|----------|-------------|
| Code Quality | 🟡 Medium | Unused dead code in errors.py |
| Error Reporting | 🟡 Medium | Missing structured error details |
| API Consistency | 🟡 Medium | Inconsistent exception types across modules |
| Developer Experience | 🟢 Low | Confusing which exceptions to use |
| User Experience | 🟢 Low | Error messages less informative than they could be |

## Recommended Fix

### Option 1: Unify and Use Enhanced Exceptions (Recommended)

#### Step 1: Restructure Exception Hierarchy

```python
# docs_cli/analyzer/errors.py (new unified version)
"""Enhanced error handling for docs-cli."""

import sys
from typing import Any, Optional

# ============================================================================
# Base Exception
# ============================================================================

class DocsCliError(Exception):
    """Base exception for all docs-cli errors.

    All custom exceptions should inherit from this class.
    Provides consistent error formatting and JSON output support.
    """

    def __init__(
        self,
        message: str,
        details: Optional[dict[str, Any]] = None,
        exit_code: int = 1
    ) -> None:
        """Initialize error with message and optional details.

        Args:
            message: Human-readable error message
            details: Additional structured details for debugging/JSON output
            exit_code: Suggested exit code for CLI
        """
        self.message = message
        self.details = details or {}
        self.exit_code = exit_code
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary for JSON output.

        Returns:
            Dictionary with error information suitable for JSON serialization
        """
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "exit_code": self.exit_code,
            **self.details,
        }

    def __str__(self) -> str:
        """String representation (for human-readable output)."""
        return self.message


# ============================================================================
# Resolution Errors
# ============================================================================

class ResolutionError(DocsCliError):
    """Error during path resolution."""

    def __init__(
        self,
        message: str,
        path: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        """Initialize resolution error.

        Args:
            message: Error message
            path: The path that failed to resolve
            details: Additional details
        """
        final_details = details or {}
        if path:
            final_details["path"] = path

        super().__init__(message, details=final_details)


class PackageNotFoundError(ResolutionError):
    """Raised when a package cannot be found or imported."""

    def __init__(self, package_name: str, details: Optional[dict[str, Any]] = None) -> None:
        """Initialize package not found error.

        Args:
            package_name: Name of the package that wasn't found
            details: Additional details
        """
        super().__init__(
            message=f"Package or module '{package_name}' not found or cannot be imported",
            path=package_name,
            details=details
        )


class ElementNotFoundError(ResolutionError):
    """Raised when an element cannot be found in a module."""

    def __init__(
        self,
        element_name: str,
        parent_path: str,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        """Initialize element not found error.

        Args:
            element_name: Name of the element that wasn't found
            parent_path: Path of the parent module/class
            details: Additional details
        """
        super().__init__(
            message=f"Element '{element_name}' not found in '{parent_path}'",
            path=f"{parent_path}.{element_name}",
            details=details
        )


class InvalidPathError(ResolutionError):
    """Raised when a path string is invalid."""

    def __init__(
        self,
        path: str,
        reason: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        """Initialize invalid path error.

        Args:
            path: The invalid path string
            reason: Why the path is invalid
            details: Additional details
        """
        message = f"Invalid path: {path}"
        if reason:
            message += f" - {reason}"

        super().__init__(
            message=message,
            path=path,
            details=details
        )


# ============================================================================
# Inspection Errors
# ============================================================================

class InspectionError(DocsCliError):
    """Error during element inspection."""

    def __init__(
        self,
        message: str,
        element_path: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        """Initialize inspection error.

        Args:
            message: Error message
            element_path: Path of element being inspected
            details: Additional details
        """
        final_details = details or {}
        if element_path:
            final_details["element_path"] = element_path

        super().__init__(message, details=final_details)


# ============================================================================
# Discovery Errors
# ============================================================================

class DiscoveryError(DocsCliError):
    """Error during member discovery."""

    def __init__(
        self,
        message: str,
        target_path: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        """Initialize discovery error.

        Args:
            message: Error message
            target_path: Path being discovered
            details: Additional details
        """
        final_details = details or {}
        if target_path:
            final_details["target_path"] = target_path

        super().__init__(message, details=final_details)


# ============================================================================
# Formatting Errors
# ============================================================================

class FormattingError(DocsCliError):
    """Error during output formatting."""

    def __init__(
        self,
        message: str,
        format_type: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        """Initialize formatting error.

        Args:
            message: Error message
            format_type: The output format being generated
            details: Additional details
        """
        final_details = details or {}
        if format_type:
            final_details["format"] = format_type

        super().__init__(message, details=final_details)


class FormatValidationError(FormattingError):
    """Error when output format validation fails."""

    def __init__(
        self,
        format_name: str,
        reason: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        """Initialize format validation error.

        Args:
            format_name: The invalid format name
            reason: Why validation failed
            details: Additional details
        """
        message = f"Unsupported or invalid format: {format_name}"
        if reason:
            message += f" - {reason}"

        super().__init__(
            message=message,
            format_type=format_name,
            details=details
        )


# ============================================================================
# Security Errors
# ============================================================================

class SecurityError(DocsCliError):
    """Base exception for security-related errors."""

    def __init__(
        self,
        message: str,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        """Initialize security error.

        Args:
            message: Error message
            details: Additional details
        """
        super().__init__(message, details=details, exit_code=2)


class UnsafeImportError(SecurityError):
    """Raised when attempting to import an unsafe module."""

    def __init__(
        self,
        module_name: str,
        reason: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        """Initialize unsafe import error.

        Args:
            module_name: The unsafe module name
            reason: Why the module is unsafe
            details: Additional details
        """
        message = f"Import blocked: '{module_name}'"
        if reason:
            message += f" - {reason}"

        final_details = details or {}
        final_details["module_name"] = module_name

        super().__init__(message, details=final_details)


class UnsafePathError(SecurityError):
    """Raised when attempting to access an unsafe file path."""

    def __init__(
        self,
        file_path: str,
        reason: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        """Initialize unsafe path error.

        Args:
            file_path: The unsafe file path
            reason: Why the path is unsafe
            details: Additional details
        """
        message = f"Path traversal blocked: '{file_path}'"
        if reason:
            message += f" - {reason}"

        final_details = details or {}
        final_details["file_path"] = file_path

        super().__init__(message, details=final_details)
```

#### Step 2: Update resolver.py to Use Enhanced Exceptions

```python
# docs_cli/analyzer/resolver.py
# Remove old exception classes
# Import from errors.py instead:

from docs_cli.analyzer.errors import (
    PackageNotFoundError,
    ElementNotFoundError,
    InvalidPathError,
)

def resolve_path(path_string: str) -> ResolvedElement:
    """Resolve a path string to an actual Python element."""
    if not path_string:
        raise InvalidPathError(
            path_string,
            reason="Path string cannot be empty"
        )

    parts = path_string.split(".")
    if not parts:
        raise InvalidPathError(
            path_string,
            reason="Invalid path format"
        )

    package_name = parts[0]

    try:
        module = importlib.import_module(package_name)
    except ImportError as e:
        raise PackageNotFoundError(package_name) from e

    # ... rest of function

    # Later in function, for element not found:
    try:
        current = getattr(current, part)
    except AttributeError as e:
        raise ElementNotFoundError(
            element_name=part,
            parent_path=current_path
        ) from e
```

#### Step 3: Update cli.py to Use Enhanced Exceptions

```python
# docs_cli/cli.py
from typer import Exit
from docs_cli.analyzer.errors import DocsCliError

def _handle_error(error: Exception) -> None:
    """Handle an error and output appropriate message.

    Args:
        error: The exception to handle
    """
    if isinstance(error, DocsCliError):
        # Use enhanced error formatting
        error_dict = error.to_dict()

        # Human-readable output to stderr
        sys.stderr.write(f"Error: {error.message}\n")

        # Optionally include details in verbose mode
        if error.details:
            for key, value in error.details.items():
                sys.stderr.write(f"  {key}: {value}\n")

        # Suggest exit code
        raise Exit(code=error.exit_code)
    else:
        # Fallback for standard exceptions
        sys.stderr.write(f"Error: {error}\n")
        raise Exit(code=1)


@app.command()
def query(
    target: str,
    # ... other options
) -> None:
    """Query Python package documentation."""
    try:
        # Resolve the target path
        resolved = resolve_path(target)

        # ... rest of function

    except DocsCliError as e:
        # Catch all docs-cli errors with unified handler
        _handle_error(e)
    except Exception as e:
        # Catch unexpected exceptions
        _handle_error(e)
```

### Option 2: Remove Unused Enhanced Exceptions (Simpler)

If the enhanced features aren't needed:

```python
# Remove docs_cli/analyzer/errors.py entirely
# Or keep only what's actually used

# Minimal version:
class DocsCliError(Exception):
    """Base exception for docs-cli errors."""
    pass
```

But this loses the benefits of enhanced error reporting.

### Option 3: Gradual Migration (Safe Approach)

1. Keep both hierarchies temporarily
2. Make resolver exceptions inherit from both
3. Gradually migrate modules one by one
4. Remove old hierarchy once migration complete

```python
# Temporary bridge
class PackageNotFoundError(ResolverError, errors.PackageNotFoundError):
    """Bridge class during migration."""
    pass
```

## Testing

### Test Suite for Exception Hierarchy

```python
# tests/test_exceptions.py
import pytest
from docs_cli.analyzer.errors import (
    DocsCliError,
    PackageNotFoundError,
    ElementNotFoundError,
    InvalidPathError,
    FormatValidationError,
    UnsafeImportError,
)

class TestExceptionHierarchy:
    """Test suite for exception classes."""

    def test_base_error_has_to_dict(self):
        """Test that base error has to_dict method."""
        error = DocsCliError("Test error", details={"key": "value"})
        error_dict = error.to_dict()

        assert "error" in error_dict
        assert error_dict["error"] == "DocsCliError"
        assert error_dict["message"] == "Test error"
        assert error_dict["key"] == "value"

    def test_package_not_found_error(self):
        """Test PackageNotFoundError."""
        error = PackageNotFoundError("mypackage")

        assert "mypackage" in error.message
        assert error.details["path"] == "mypackage"
        assert error.exit_code == 1

        error_dict = error.to_dict()
        assert error_dict["path"] == "mypackage"

    def test_element_not_found_error(self):
        """Test ElementNotFoundError."""
        error = ElementNotFoundError("myfunction", "mymodule")

        assert "myfunction" in error.message
        assert "mymodule" in error.message
        assert error.details["element_path"] == "mymodule.myfunction"

    def test_invalid_path_error(self):
        """Test InvalidPathError."""
        error = InvalidPathError("../../etc/passwd", reason="Path traversal detected")

        assert "../../etc/passwd" in error.message
        assert "Path traversal detected" in error.message
        assert error.details["path"] == "../../etc/passwd"

    def test_format_validation_error(self):
        """Test FormatValidationError."""
        error = FormatValidationError("xml", reason="XML format not supported")

        assert "xml" in error.message
        assert error.details["format"] == "xml"

    def test_unsafe_import_error(self):
        """Test UnsafeImportError."""
        error = UnsafeImportError("subprocess", reason="Blocked for security")

        assert "subprocess" in error.message
        assert "Blocked" in error.message
        assert error.exit_code == 2  # Security errors use exit code 2

    def test_error_inheritance_chain(self):
        """Test that all errors inherit from DocsCliError."""
        errors = [
            PackageNotFoundError("test"),
            ElementNotFoundError("test", "parent"),
            InvalidPathError("test"),
            FormatValidationError("test"),
            UnsafeImportError("test"),
        ]

        for error in errors:
            assert isinstance(error, DocsCliError)
            assert hasattr(error, 'to_dict')
            assert hasattr(error, 'exit_code')

    def test_cli_error_handling(self):
        """Test that CLI properly handles enhanced errors."""
        from docs_cli.cli import _handle_error
        from io import StringIO
        import sys

        # Capture stderr
        old_stderr = sys.stderr
        sys.stderr = StringIO()

        try:
            error = PackageNotFoundError("nonexistent")
            with pytest.raises(Exit):
                _handle_error(error)

            output = sys.stderr.getvalue()
            assert "nonexistent" in output
        finally:
            sys.stderr = old_stderr
```

## Migration Plan

### Phase 1: Prepare (Week 1)
- [ ] Review all exception usage across codebase
- [ ] Design final exception hierarchy
- [ ] Write tests for new exception hierarchy

### Phase 2: Implement (Week 1-2)
- [ ] Implement unified exception hierarchy in `errors.py`
- [ ] Add helper functions for error creation
- [ ] Add comprehensive tests

### Phase 3: Migrate Modules (Week 2)
- [ ] Update `resolver.py` to use new exceptions
- [ ] Update `cli.py` error handling
- [ ] Update `discovery.py` if needed
- [ ] Update `search.py` if needed
- [ ] Update `inspector.py` if needed

### Phase 4: Cleanup (Week 2)
- [ ] Remove old exception classes from `resolver.py`
- [ ] Remove any unused exception classes
- [ ] Update all imports
- [ ] Run full test suite

### Phase 5: Verify (Week 2)
- [ ] Test all CLI commands
- [ ] Verify error messages are user-friendly
- [ ] Verify JSON error output is correct
- [ ] Update documentation

## Benefits of Fix

| Benefit | Impact |
|---------|--------|
| **Consistency** | Single exception hierarchy across all modules |
| **Better Error Messages** | Structured details for debugging |
| **JSON Output** | `to_dict()` method for API responses |
| **Maintainability** | One place to update error handling |
| **Type Safety** | Clear exception inheritance |
| **User Experience** | More informative error messages |
| **Developer Experience** | Clear guidance on which exceptions to use |

## Related Issues

- [QUAL-001: Code Duplication - Type Detection](./004-code-duplication-type-detection.md)
- [SEC-001: Dynamic Import Without Sanitization](./001-dynamic-import-without-sanitization.md)

## References

- [Python Exception Handling Best Practices](https://docs.python.org/3/tutorial/errors.html)
- [Designing Exception Hierarchies](https://martinfowler.com/bliki/ExceptionHandling.html)

## Checklist

- [ ] Design unified exception hierarchy
- [ ] Implement new exception classes in `errors.py`
- [ ] Add `to_dict()` method to all exceptions
- [ ] Add error details support
- [ ] Update `resolver.py` to use new exceptions
- [ ] Update `cli.py` to use new exceptions
- [ ] Update other modules as needed
- [ ] Remove old exception classes
- [ ] Write comprehensive tests
- [ ] Update documentation
- [ ] Verify all error paths
