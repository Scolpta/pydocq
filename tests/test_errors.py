"""Tests for enhanced error handling."""

import pytest

from pydocq.analyzer.errors import (
    DiscoveryError,
    DocsCliError,
    FormatValidationError,
    FormattingError,
    InspectionError,
    ResolutionError,
    create_resolution_error,
    format_error_for_output,
    handle_error,
    wrap_error,
)
from pydocq.analyzer.resolver import (
    ElementNotFoundError,
    InvalidPathError,
    PackageNotFoundError,
)


class TestDocsCliError:
    """Tests for DocsCliError base class."""

    def test_basic_error(self) -> None:
        """Test basic error creation."""
        error = DocsCliError("Test error message")

        assert error.message == "Test error message"
        assert error.details == {}
        assert str(error) == "Test error message"

    def test_error_with_details(self) -> None:
        """Test error with details."""
        details = {"key": "value", "number": 42}
        error = DocsCliError("Test error", details=details)

        assert error.details == details

    def test_error_to_dict(self) -> None:
        """Test converting error to dictionary."""
        error = DocsCliError("Test error", details={"key": "value"})

        result = error.to_dict()

        assert result["error"] == "DocsCliError"
        assert result["message"] == "Test error"
        assert result["key"] == "value"


class TestErrorSubclasses:
    """Tests for error subclasses."""

    def test_resolution_error(self) -> None:
        """Test ResolutionError."""
        error = ResolutionError("Resolution failed")

        assert isinstance(error, DocsCliError)
        assert error.message == "Resolution failed"

    def test_inspection_error(self) -> None:
        """Test InspectionError."""
        error = InspectionError("Inspection failed")

        assert isinstance(error, DocsCliError)
        assert error.message == "Inspection failed"

    def test_formatting_error(self) -> None:
        """Test FormattingError."""
        error = FormattingError("Formatting failed")

        assert isinstance(error, DocsCliError)
        assert error.message == "Formatting failed"

    def test_discovery_error(self) -> None:
        """Test DiscoveryError."""
        error = DiscoveryError("Discovery failed")

        assert isinstance(error, DocsCliError)
        assert error.message == "Discovery failed"

    def test_format_validation_error(self) -> None:
        """Test FormatValidationError."""
        error = FormatValidationError("Invalid format")

        assert isinstance(error, DocsCliError)
        assert error.message == "Invalid format"


class TestFormatErrorForOutput:
    """Tests for format_error_for_output function."""

    def test_format_pydocq_error(self) -> None:
        """Test formatting DocsCliError."""
        error = DocsCliError("Test error", details={"key": "value"})

        result = format_error_for_output(error)

        assert result["error"] == "DocsCliError"
        assert result["message"] == "Test error"
        assert result["key"] == "value"

    def test_format_standard_exception(self) -> None:
        """Test formatting standard exception."""
        error = ValueError("Standard error")

        result = format_error_for_output(error)

        assert result["error"] == "ValueError"
        assert result["message"] == "Standard error"

    def test_format_with_traceback(self) -> None:
        """Test formatting with traceback."""
        error = DocsCliError("Test error")

        result = format_error_for_output(error, include_traceback=True)

        assert "traceback" in result
        assert isinstance(result["traceback"], str)


class TestCreateResolutionError:
    """Tests for create_resolution_error function."""

    def test_from_package_not_found(self) -> None:
        """Test creating from PackageNotFoundError."""
        original = PackageNotFoundError("test_package")
        error = create_resolution_error(original)

        assert isinstance(error, ResolutionError)
        assert "Package or module not found" in error.message
        assert error.details["original_type"] == "PackageNotFoundError"

    def test_from_element_not_found(self) -> None:
        """Test creating from ElementNotFoundError."""
        original = ElementNotFoundError("test_element not found")
        error = create_resolution_error(original)

        assert isinstance(error, ResolutionError)
        assert "Element not found" in error.message
        assert error.details["original_type"] == "ElementNotFoundError"

    def test_from_invalid_path(self) -> None:
        """Test creating from InvalidPathError."""
        original = InvalidPathError("invalid path")
        error = create_resolution_error(original)

        assert isinstance(error, ResolutionError)
        assert "Invalid path" in error.message
        assert error.details["original_type"] == "InvalidPathError"


class TestWrapError:
    """Tests for wrap_error function."""

    def test_wrap_standard_error(self) -> None:
        """Test wrapping a standard error."""
        original = ValueError("Original error")
        error = wrap_error(original, InspectionError)

        assert isinstance(error, InspectionError)
        assert error.message == "Original error"
        assert error.details["original_type"] == "ValueError"

    def test_wrap_with_message_override(self) -> None:
        """Test wrapping with custom message."""
        original = ValueError("Original error")
        error = wrap_error(original, InspectionError, message_override="Custom message")

        assert error.message == "Custom message"
        assert error.details["original_message"] == "Original error"


class TestHandleError:
    """Tests for handle_error function."""

    def test_handle_error_exits(self) -> None:
        """Test that handle_error exits with correct code."""
        error = DocsCliError("Test error")

        with pytest.raises(SystemExit) as exc_info:
            handle_error(error, exit_code=42)

        assert exc_info.value.code == 42

    def test_handle_error_with_pydocq_error(self, capsys) -> None:
        """Test handling DocsCliError outputs to stderr."""
        error = DocsCliError("Test error")

        with pytest.raises(SystemExit):
            handle_error(error)

        captured = capsys.readouterr()
        assert "Error: Test error" in captured.err
