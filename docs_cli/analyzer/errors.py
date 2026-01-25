"""Enhanced error handling for docs-cli.

This module provides custom exceptions and error handling utilities
for better error messages and debugging.
"""

import sys
from typing import Any

from docs_cli.analyzer.resolver import (
    ElementNotFoundError,
    InvalidPathError,
    PackageNotFoundError,
    ResolverError,
)


class DocsCliError(Exception):
    """Base exception for docs-cli errors."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        """Initialize error with message and optional details.

        Args:
            message: Error message
            details: Additional error details for debugging
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


class ResolutionError(DocsCliError):
    """Error during path resolution."""

    pass


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


def create_resolution_error(original_error: ResolverError) -> ResolutionError:
    """Create a ResolutionError from a ResolverError.

    Args:
        original_error: The original resolver error

    Returns:
        ResolutionError with enhanced message
    """
    details = {"original_type": original_error.__class__.__name__}

    if isinstance(original_error, PackageNotFoundError):
        message = f"Package or module not found: {original_error}"
    elif isinstance(original_error, ElementNotFoundError):
        message = f"Element not found: {original_error}"
    elif isinstance(original_error, InvalidPathError):
        message = f"Invalid path: {original_error}"
    else:
        message = f"Resolution error: {original_error}"

    return ResolutionError(message, details=details)


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
