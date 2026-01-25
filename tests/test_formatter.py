"""Tests for JSON formatting."""

import inspect

from docs_cli.analyzer.formatter import (
    _format_docstring,
    _format_signature,
    _format_source_location,
    format_json,
    format_json_compact,
    format_json_verbose,
)
from docs_cli.analyzer.inspector import (
    DocstringInfo,
    SignatureInfo,
    SourceLocation,
    inspect_element,
)
from docs_cli.utils.type_detection import ElementType
from docs_cli.analyzer.resolver import resolve_path


class TestFormatSignature:
    """Tests for _format_signature function."""

    def test_format_signature_with_params(self) -> None:
        """Test formatting signature with parameters."""
        sig = SignatureInfo(
            parameters=[{"name": "a", "kind": "POSITIONAL_OR_KEYWORD"}],
            return_type="str",
        )

        result = _format_signature(sig)

        assert result == {
            "parameters": [{"name": "a", "kind": "POSITIONAL_OR_KEYWORD"}],
            "return_type": "str",
        }

    def test_format_signature_empty(self) -> None:
        """Test formatting empty signature."""
        sig = SignatureInfo(parameters=[], return_type=None)

        result = _format_signature(sig)

        assert result == {"parameters": [], "return_type": None}


class TestFormatDocstring:
    """Tests for _format_docstring function."""

    def test_format_docstring_with_examples(self) -> None:
        """Test formatting docstring with examples."""
        doc = DocstringInfo(
            docstring="Example:\n>>> test()", length=17, has_examples=True
        )

        result = _format_docstring(doc)

        assert result == {
            "docstring": "Example:\n>>> test()",
            "length": 17,
            "has_examples": True,
        }

    def test_format_docstring_without_examples(self) -> None:
        """Test formatting docstring without examples."""
        doc = DocstringInfo(
            docstring="Just a docstring", length=16, has_examples=False
        )

        result = _format_docstring(doc)

        assert result == {
            "docstring": "Just a docstring",
            "length": 16,
        }
        # has_examples should not be in output when False
        assert "has_examples" not in result

    def test_format_docstring_empty(self) -> None:
        """Test formatting empty docstring."""
        doc = DocstringInfo(docstring=None, length=0, has_examples=False)

        result = _format_docstring(doc)

        assert result == {"docstring": None, "length": 0}


class TestFormatSourceLocation:
    """Tests for _format_source_location function."""

    def test_format_source_location_complete(self) -> None:
        """Test formatting complete source location."""
        loc = SourceLocation(file="/path/to/file.py", line=42)

        result = _format_source_location(loc)

        assert result == {"file": "/path/to/file.py", "line": 42}

    def test_format_source_location_partial(self) -> None:
        """Test formatting partial source location."""
        loc = SourceLocation(file="/path/to/file.py", line=None)

        result = _format_source_location(loc)

        assert result == {"file": "/path/to/file.py"}
        assert "line" not in result

    def test_format_source_location_empty(self) -> None:
        """Test formatting empty source location."""
        loc = SourceLocation(file=None, line=None)

        result = _format_source_location(loc)

        assert result == {}


class TestFormatJson:
    """Tests for format_json function."""

    def test_format_json_default(self) -> None:
        """Test default JSON formatting."""
        resolved = resolve_path("os.path.join")
        inspected = inspect_element(resolved)

        result = format_json(inspected)

        assert "path" in result
        assert "type" in result
        assert "module_path" in result
        # Signature and docstring included by default
        assert "signature" in result
        assert "docstring" in result
        # Source location not included by default
        assert "source_location" not in result

    def test_format_json_with_source(self) -> None:
        """Test JSON formatting with source location."""
        resolved = resolve_path("os.path.join")
        inspected = inspect_element(resolved)

        result = format_json(inspected, include_source=True)

        assert "source_location" in result

    def test_format_json_without_docstring(self) -> None:
        """Test JSON formatting without docstring."""
        resolved = resolve_path("os.path.join")
        inspected = inspect_element(resolved)

        result = format_json(inspected, include_docstring=False)

        assert "docstring" not in result
        assert "signature" in result

    def test_format_json_without_signature(self) -> None:
        """Test JSON formatting without signature."""
        resolved = resolve_path("os.path.join")
        inspected = inspect_element(resolved)

        result = format_json(inspected, include_signature=False)

        assert "signature" not in result
        assert "docstring" in result


class TestFormatJsonCompact:
    """Tests for format_json_compact function."""

    def test_format_json_compact(self) -> None:
        """Test compact JSON formatting."""
        resolved = resolve_path("os.path.join")
        inspected = inspect_element(resolved)

        result = format_json_compact(inspected)

        # Should only have basic fields
        assert set(result.keys()) == {"path", "type", "module_path"}
        assert result["path"] == "os.path.join"
        assert result["type"] == "function"


class TestFormatJsonVerbose:
    """Tests for format_json_verbose function."""

    def test_format_json_verbose(self) -> None:
        """Test verbose JSON formatting."""
        resolved = resolve_path("os.path.join")
        inspected = inspect_element(resolved)

        result = format_json_verbose(inspected)

        # Should have all fields
        assert "path" in result
        assert "type" in result
        assert "module_path" in result
        assert "signature" in result
        assert "docstring" in result
        assert "source_location" in result
