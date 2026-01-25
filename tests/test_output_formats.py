"""Tests for output format handlers."""

import inspect

import pytest

from docs_cli.analyzer.inspector import (
    DocstringInfo,
    InspectedElement,
    SignatureInfo,
    SourceLocation,
)
from docs_cli.analyzer.output_formats import (
    format_markdown,
    format_raw,
    format_signature,
    format_yaml,
    get_formatter,
)
from docs_cli.analyzer.resolver import ElementType
from docs_cli.utils.type_detection import ElementType


class TestFormatRaw:
    """Tests for format_raw function."""

    def test_format_raw_basic(self) -> None:
        """Test basic raw formatting."""
        element = InspectedElement(
            path="test.module",
            element_type=ElementType.MODULE,
            obj=None,
            module_path="test.module",
        )

        result = format_raw(element)

        assert "Path: test.module" in result
        assert "Type: module" in result
        assert "Module: test.module" in result

    def test_format_raw_with_signature(self) -> None:
        """Test raw formatting with signature."""
        sig = SignatureInfo(
            parameters=[
                {
                    "name": "x",
                    "kind": "POSITIONAL_OR_KEYWORD",
                    "default": None,
                    "annotation": "int",
                }
            ],
            return_type="str",
        )

        element = InspectedElement(
            path="test.func",
            element_type=ElementType.FUNCTION,
            obj=None,
            signature=sig,
            module_path="test",
        )

        result = format_raw(element)

        assert "Signature:" in result
        assert "x: int" in result
        assert "-> str" in result

    def test_format_raw_with_docstring(self) -> None:
        """Test raw formatting with docstring."""
        doc = DocstringInfo(
            docstring="This is a test function.\nIt does something.",
            length=39,
            has_examples=True,
        )

        element = InspectedElement(
            path="test.func",
            element_type=ElementType.FUNCTION,
            obj=None,
            docstring=doc,
            module_path="test",
        )

        result = format_raw(element)

        assert "Docstring:" in result
        assert "Length: 39 characters" in result
        assert "Contains examples: Yes" in result
        assert "This is a test function." in result

    def test_format_raw_with_source_location(self) -> None:
        """Test raw formatting with source location."""
        loc = SourceLocation(file="/path/to/file.py", line=42)

        element = InspectedElement(
            path="test.func",
            element_type=ElementType.FUNCTION,
            obj=None,
            source_location=loc,
            module_path="test",
        )

        result = format_raw(element)

        assert "Source Location:" in result
        assert "File: /path/to/file.py" in result
        assert "Line: 42" in result


class TestFormatSignature:
    """Tests for format_signature function."""

    def test_format_signature_no_params(self) -> None:
        """Test signature formatting with no parameters."""
        element = InspectedElement(
            path="test.func",
            element_type=ElementType.FUNCTION,
            obj=None,
            signature=SignatureInfo(parameters=[], return_type=None),
            module_path="test",
        )

        result = format_signature(element)

        assert result == "test.func()"

    def test_format_signature_with_params(self) -> None:
        """Test signature formatting with parameters."""
        sig = SignatureInfo(
            parameters=[
                {
                    "name": "x",
                    "kind": "POSITIONAL_OR_KEYWORD",
                    "default": None,
                    "annotation": "int",
                },
                {
                    "name": "y",
                    "kind": "POSITIONAL_OR_KEYWORD",
                    "default": "5",
                    "annotation": "str",
                },
            ],
            return_type="bool",
        )

        element = InspectedElement(
            path="test.func",
            element_type=ElementType.FUNCTION,
            obj=None,
            signature=sig,
            module_path="test",
        )

        result = format_signature(element)

        assert "test.func(" in result
        assert "x: int" in result
        assert "y: str = 5" in result
        assert "-> bool" in result

    def test_format_signature_no_return(self) -> None:
        """Test signature formatting without return type."""
        sig = SignatureInfo(
            parameters=[
                {
                    "name": "x",
                    "kind": "POSITIONAL_OR_KEYWORD",
                    "default": None,
                    "annotation": None,
                }
            ],
            return_type=None,
        )

        element = InspectedElement(
            path="test.func",
            element_type=ElementType.FUNCTION,
            obj=None,
            signature=sig,
            module_path="test",
        )

        result = format_signature(element)

        assert "->" not in result


class TestFormatMarkdown:
    """Tests for format_markdown function."""

    def test_format_markdown_basic(self) -> None:
        """Test basic markdown formatting."""
        element = InspectedElement(
            path="test.module",
            element_type=ElementType.MODULE,
            obj=None,
            module_path="test.module",
        )

        result = format_markdown(element)

        assert "# `test.module`" in result
        assert "| **Type** | module |" in result
        assert "| **Module** | `test.module` |" in result

    def test_format_markdown_with_signature(self) -> None:
        """Test markdown formatting with signature."""
        sig = SignatureInfo(
            parameters=[
                {
                    "name": "x",
                    "kind": "POSITIONAL_OR_KEYWORD",
                    "default": None,
                    "annotation": "int",
                }
            ],
            return_type="str",
        )

        element = InspectedElement(
            path="test.func",
            element_type=ElementType.FUNCTION,
            obj=None,
            signature=sig,
            module_path="test",
        )

        result = format_markdown(element)

        assert "## Signature" in result
        assert "```python" in result
        assert "test.func(" in result
        assert "### Parameters" in result
        assert "| Name | Type | Default |" in result

    def test_format_markdown_with_docstring(self) -> None:
        """Test markdown formatting with docstring."""
        doc = DocstringInfo(
            docstring="Test function that does something.",
            length=34,
            has_examples=False,
        )

        element = InspectedElement(
            path="test.func",
            element_type=ElementType.FUNCTION,
            obj=None,
            docstring=doc,
            module_path="test",
        )

        result = format_markdown(element)

        assert "## Documentation" in result
        assert "Test function that does something." in result


class TestFormatYaml:
    """Tests for format_yaml function."""

    def test_format_yaml_basic(self) -> None:
        """Test basic YAML formatting."""
        element = InspectedElement(
            path="test.func",
            element_type=ElementType.FUNCTION,
            obj=None,
            module_path="test",
        )

        result = format_yaml(element)

        # YAML output is JSON for now
        assert '"path": "test.func"' in result
        assert '"type": "function"' in result
        assert '"module": "test"' in result


class TestGetFormatter:
    """Tests for get_formatter function."""

    def test_get_formatter_json(self) -> None:
        """Test getting JSON formatter."""
        formatter = get_formatter("json")
        assert callable(formatter)

        element = InspectedElement(
            path="test.func",
            element_type=ElementType.FUNCTION,
            obj=None,
            module_path="test",
        )

        result = formatter(element)
        assert '"path": "test.func"' in result

    def test_get_formatter_raw(self) -> None:
        """Test getting raw formatter."""
        formatter = get_formatter("raw")
        assert callable(formatter)
        assert formatter == format_raw

    def test_get_formatter_signature(self) -> None:
        """Test getting signature formatter."""
        formatter = get_formatter("signature")
        assert callable(formatter)
        assert formatter == format_signature

    def test_get_formatter_markdown(self) -> None:
        """Test getting markdown formatter."""
        formatter = get_formatter("markdown")
        assert callable(formatter)
        assert formatter == format_markdown

    def test_get_formatter_yaml(self) -> None:
        """Test getting YAML formatter."""
        formatter = get_formatter("yaml")
        assert callable(formatter)
        assert formatter == format_yaml

    def test_get_formatter_invalid(self) -> None:
        """Test getting invalid formatter raises error."""
        with pytest.raises(ValueError, match="Unsupported format"):
            get_formatter("invalid_format")
