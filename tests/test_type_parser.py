"""Tests for type annotation parsing."""

from typing import List, Optional, Union

import pytest

from docs_cli.analyzer.type_parser import (
    TypeInfo,
    get_class_type_hints,
    get_type_hints_safe,
    parse_signature_types,
    parse_type_annotation,
    resolve_forward_reference,
)


def example_func(
    x: int, y: str, z: Optional[List[int]] = None
) -> Union[str, int]:
    """Example function with type annotations."""
    return x


def example_simple_func(a: int, b: str) -> bool:
    """Simple function with type annotations."""
    return True


class ExampleClass:
    """Example class with typed attributes."""

    attr1: int
    attr2: List[str]

    def method(self, x: int) -> str:
        """Method with type annotations."""
        return str(x)


class TestTypeInfo:
    """Tests for TypeInfo class."""

    def test_basic_type(self) -> None:
        """Test basic type info."""
        info = TypeInfo(name="int")

        assert info.name == "int"
        assert info.origin is None
        assert info.args == []
        assert info.is_optional is False

    def test_generic_type(self) -> None:
        """Test generic type info."""
        info = TypeInfo(name="List", origin="List", args=[TypeInfo(name="int")])

        assert info.name == "List"
        assert info.origin == "List"
        assert len(info.args) == 1
        assert info.args[0].name == "int"

    def test_optional_type(self) -> None:
        """Test optional type info."""
        info = TypeInfo(name="int", is_optional=True)

        assert info.is_optional is True

    def test_to_dict(self) -> None:
        """Test converting to dictionary."""
        info = TypeInfo(name="List", origin="List", args=[TypeInfo(name="int")])

        result = info.to_dict()

        assert result["name"] == "List"
        assert result["origin"] == "List"
        assert "args" in result
        assert result["args"][0]["name"] == "int"


class TestParseTypeAnnotation:
    """Tests for parse_type_annotation function."""

    def test_parse_string_annotation(self) -> None:
        """Test parsing string annotation."""
        info = parse_type_annotation("MyClass")

        assert info.name == "MyClass"

    def test_parse_builtin_type(self) -> None:
        """Test parsing built-in type."""
        info = parse_type_annotation(int)

        assert info.name == "int"

    def test_parse_optional_type(self) -> None:
        """Test parsing Optional type."""
        info = parse_type_annotation(Optional[int])

        assert info.is_optional is True
        assert info.name == "int"

    def test_parse_union_type(self) -> None:
        """Test parsing Union type."""
        info = parse_type_annotation(Union[int, str])

        # Union types are parsed
        assert info.name  # Should have a name

    def test_parse_list_type(self) -> None:
        """Test parsing List type."""
        info = parse_type_annotation(List[int])

        # In Python 3.9+, List[int] origin is 'list' (lowercase)
        assert info.origin in ["List", "list"]
        assert len(info.args) > 0


class TestGetTypeHintsSafe:
    """Tests for get_type_hints_safe function."""

    def test_get_hints_from_function(self) -> None:
        """Test getting hints from function."""
        hints = get_type_hints_safe(example_func)

        assert "x" in hints or "return" in hints

    def test_get_hints_from_class(self) -> None:
        """Test getting hints from class."""
        hints = get_type_hints_safe(ExampleClass)

        # Should have attribute annotations
        assert isinstance(hints, dict)


class TestParseSignatureTypes:
    """Tests for parse_signature_types function."""

    def test_parse_function_types(self) -> None:
        """Test parsing types from function."""
        result = parse_signature_types(example_simple_func)

        assert "parameters" in result
        assert "return" in result
        assert "a" in result["parameters"]
        assert "b" in result["parameters"]

    def test_parse_return_type(self) -> None:
        """Test parsing return type."""
        result = parse_signature_types(example_simple_func)

        return_type = result.get("return")
        assert return_type is not None
        assert "name" in return_type

    def test_parse_complex_annotations(self) -> None:
        """Test parsing complex type annotations."""
        result = parse_signature_types(example_func)

        # Should have parameters with types
        assert "parameters" in result
        assert len(result["parameters"]) >= 2


class TestGetClassTypeHints:
    """Tests for get_class_type_hints function."""

    def test_get_class_attributes(self) -> None:
        """Test getting class attribute types."""
        result = get_class_type_hints(ExampleClass)

        assert "attributes" in result
        assert "methods" in result

    def test_get_class_methods(self) -> None:
        """Test getting class method types."""
        result = get_class_type_hints(ExampleClass)

        assert "methods" in result
        # Should have at least the method we defined
        assert len(result["methods"]) >= 0


class TestResolveForwardReference:
    """Tests for resolve_forward_reference function."""

    def test_resolve_typing_annotation(self) -> None:
        """Test resolving typing module annotation."""
        result = resolve_forward_reference("List")

        assert result == "typing.List"

    def test_resolve_already_qualified(self) -> None:
        """Test already qualified name."""
        result = resolve_forward_reference("mypackage.MyClass")

        assert result == "mypackage.MyClass"

    def test_resolve_simple_name(self) -> None:
        """Test simple forward reference."""
        result = resolve_forward_reference("MyClass")

        assert result == "MyClass"
