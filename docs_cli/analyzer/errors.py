"""Enhanced error handling for docs-cli.

This module provides the unified exception hierarchy for all docs-cli errors.
"""

import sys
from typing import Any, Optional


class DocsCliError(Exception):
    """Base exception for all docs-cli errors.

    All custom exceptions should inherit from this class.
    Provides consistent error formatting and JSON output support.
    """

    def __init__(
        self,
        message: str,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize error with message and optional details.

        Args:
            message: Human-readable error message
            details: Additional structured details for debugging/JSON output
        """
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict:
        """Convert error to dictionary for JSON output.

        Returns:
            Dictionary with error information
        """
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            **self.details,
        }


# ============================================================================
# Resolution Exceptions (inherit from DocsCliError)
# ============================================================================

class ResolutionError(DocsCliError):
    """Base exception for resolution errors."""

    pass


class PackageNotFoundError(ResolutionError):
    """Raised when a package cannot be found or imported."""

    pass


class ElementNotFoundError(ResolutionError):
    """Raised when an element cannot be found in a module."""

    pass


class InvalidPathError(ResolutionError):
    """Raised when a path string is invalid."""

    pass


class SecurityError(ResolutionError):
    """Raised when a path is rejected for security reasons."""

    pass


# ============================================================================
# Other Exception Categories
# ============================================================================

class InspectionError(DocsCliError):
    """Error during element inspection."""

    pass


class FormattingError(DocsCliError):
    """Error during output formatting."""

    pass


class DiscoveryError(DocsCliError):
    """Error during member discovery."""

    pass


class FormatValidationError(DocsCliError):
    """Error when output format validation fails."""

    pass


# ============================================================================
# Error Handling Utilities
# ============================================================================

def format_error_for_output(
    error: Exception, include_traceback: bool = False
) -> dict:
    """Format an exception for JSON output.

    Args:
        error: The exception to format
        include_traceback: Whether to include traceback information

    Returns:
        Dictionary with error information
    """
    if isinstance(error, DocsCliError):
        result = error.to_dict()
    else:
        result = {
            "error": error.__class__.__name__,
            "message": str(error),
        }

    if include_traceback:
        import traceback

        result["traceback"] = traceback.format_exc()

    return result


def handle_error(
    error: Exception,
    exit_code: int = 1,
    show_traceback: bool = False,
    output_format: str = "text",
) -> None:
    """Handle an error and output appropriate message.

    Args:
        error: The exception to handle
        exit_code: Exit code to use
        show_traceback: Whether to show traceback
        output_format: Output format (text or json)
    """
    if output_format == "json":
        import json

        error_dict = format_error_for_output(error, include_traceback=show_traceback)
        sys.stderr.write(json.dumps(error_dict, indent=2) + "\n")
    else:
        # Text format
        if isinstance(error, DocsCliError):
            sys.stderr.write(f"Error: {error.message}\n")
            if error.details and show_traceback:
                sys.stderr.write(f"Details: {error.details}\n")
        else:
            sys.stderr.write(f"Error: {error}\n")

        if show_traceback:
            import traceback

            sys.stderr.write("\nTraceback:\n")
            sys.stderr.write(traceback.format_exc())

    sys.exit(exit_code)


def wrap_error(
    error: Exception,
    wrapper_class: type[DocsCliError],
    message_override: str | None = None,
) -> DocsCliError:
    """Wrap an exception in a docs-cli error.

    Args:
        error: The original exception
        wrapper_class: The docs-cli error class to use
        message_override: Optional message override

    Returns:
        Wrapped docs-cli error
    """
    message = message_override or str(error)
    details = {"original_type": error.__class__.__name__, "original_message": str(error)}

    return wrapper_class(message, details=details)


def create_resolution_error(original_error: ResolutionError) -> ResolutionError:
    """Create a ResolutionError from another resolution error.

    This function exists for backwards compatibility and test support.
    Since all resolution errors now inherit from ResolutionError,
    it simply returns the original error with enhanced details.

    Args:
        original_error: The original resolution error

    Returns:
        ResolutionError with potentially enhanced message
    """
    # If already a ResolutionError with details, return as-is
    if isinstance(original_error, PackageNotFoundError):
        message = f"Package or module not found: {original_error}"
    elif isinstance(original_error, ElementNotFoundError):
        message = f"Element not found: {original_error}"
    elif isinstance(original_error, InvalidPathError):
        message = f"Invalid path: {original_error}"
    elif isinstance(original_error, SecurityError):
        message = f"Security error: {original_error}"
    else:
        message = str(original_error)

    # Create new error with enhanced message and original type in details
    details = {"original_type": original_error.__class__.__name__}
    if hasattr(original_error, "details"):
        details.update(original_error.details)

    return ResolutionError(message, details=details)
