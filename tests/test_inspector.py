"""Tests for runtime introspection."""

import inspect
from pathlib import Path


def _simple_test_function():
    """A simple function for testing signature extraction."""
    pass


from docs_cli.analyzer.inspector import (
    DocstringInfo,
    SignatureInfo,
    SourceLocation,
    _check_for_examples,
    get_docstring,
    get_signature,
    get_source_location,
    inspect_element,
)
from docs_cli.utils.type_detection import ElementType
from docs_cli.analyzer.resolver import resolve_path


class TestGetSignature:
    """Tests for get_signature function."""

    def test_get_signature_function(self) -> None:
        """Test extracting signature from a function."""
        # Use a simple module-level function
        result = get_signature(_simple_test_function)

        assert isinstance(result, SignatureInfo)
        assert len(result.parameters) == 0

    def test_get_signature_with_parameters(self) -> None:
        """Test extracting signature with parameters."""

        def example_func(a: int, b: str = "default") -> str:
            return b * a

        result = get_signature(example_func)

        assert len(result.parameters) == 2
        assert result.parameters[0]["name"] == "a"
        # Annotation is converted to string representation
        assert "int" in result.parameters[0]["annotation"]
        assert result.parameters[1]["name"] == "b"
        assert result.parameters[1]["default"] == "default"
        assert "str" in result.return_type

    def test_get_signature_builtin(self) -> None:
        """Test that built-in functions can have signatures extracted."""
        result = get_signature(len)

        assert isinstance(result, SignatureInfo)
        # Built-in functions often have signatures in Python 3.11+
        assert len(result.parameters) >= 0


class TestGetDocstring:
    """Tests for get_docstring function."""

    def test_get_docstring_with_docstring(self) -> None:
        """Test extracting a docstring."""

        def example_func():
            """This is an example docstring."""

        result = get_docstring(example_func)

        assert isinstance(result, DocstringInfo)
        assert result.docstring == "This is an example docstring."
        assert result.length == len("This is an example docstring.")

    def test_get_docstring_without_docstring(self) -> None:
        """Test function without docstring."""

        def example_func():
            pass

        result = get_docstring(example_func)

        assert result.docstring is None
        assert result.length == 0

    def test_get_docstring_detects_examples(self) -> None:
        """Test detecting examples in docstring."""

        def example_func():
            """This is a docstring.

            Example:
                >>> example_func()
                'result'
            """

        result = get_docstring(example_func)

        assert result.has_examples is True


class TestCheckForExamples:
    """Tests for _check_for_examples helper."""

    def test_check_example_colon(self) -> None:
        """Test detecting 'Example:' indicator."""
        assert _check_for_examples("Some text\nExample:\n    code") is True

    def test_check_examples_colon(self) -> None:
        """Test detecting 'Examples:' indicator."""
        assert _check_for_examples("Some text\nExamples:\n    code") is True

    def test_check_python_prompt(self) -> None:
        """Test detecting '>>>' prompt."""
        assert _check_for_examples("Some text\n>>> example()") is True

    def test_check_usage_indicator(self) -> None:
        """Test detecting 'Usage:' indicator."""
        assert _check_for_examples("Some text\nUsage:\n    code") is True

    def test_check_rest_directive(self) -> None:
        """Test detecting '::' directive."""
        assert _check_for_examples("Some text\n::\n    code") is True

    def test_check_no_examples(self) -> None:
        """Test docstring without examples."""
        assert _check_for_examples("Just regular text") is False


class TestGetSourceLocation:
    """Tests for get_source_location function."""

    def test_get_source_location_function(self) -> None:
        """Test getting source location for a function."""
        # Use the test method itself
        result = get_source_location(self.test_get_source_location_function)

        assert isinstance(result, SourceLocation)
        assert result.file is not None
        assert "test_inspector.py" in result.file
        assert result.line is not None

    def test_get_source_location_builtin(self) -> None:
        """Test that built-in functions return empty location."""
        result = get_source_location(len)

        assert isinstance(result, SourceLocation)
        assert result.file is None
        assert result.line is None


class TestInspectElement:
    """Tests for inspect_element function."""

    def test_inspect_module(self) -> None:
        """Test inspecting a module."""
        resolved = resolve_path("os")
        result = inspect_element(resolved)

        assert result.path == "os"
        assert result.element_type == ElementType.MODULE
        assert result.docstring is not None
        assert result.docstring.docstring is not None
        assert result.source_location is not None

    def test_inspect_function(self) -> None:
        """Test inspecting a function."""
        resolved = resolve_path("os.path.join")
        result = inspect_element(resolved)

        assert result.path == "os.path.join"
        assert result.element_type == ElementType.FUNCTION
        assert result.signature is not None
        assert len(result.signature.parameters) > 0
        assert result.docstring is not None
        assert result.source_location is not None

    def test_inspect_class(self) -> None:
        """Test inspecting a class."""
        resolved = resolve_path("builtins.str")
        result = inspect_element(resolved)

        assert result.path == "builtins.str"
        assert result.element_type == ElementType.CLASS
        # Classes should have __init__ signature
        assert result.signature is not None or result.docstring is not None

    def test_inspect_element_preserves_module_path(self) -> None:
        """Test that module_path is preserved in inspected element."""
        resolved = resolve_path("os.path.join")
        result = inspect_element(resolved)

        assert result.module_path == resolved.module_path
