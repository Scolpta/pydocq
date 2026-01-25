"""Tests for centralized type detection utilities."""

import os
from pathlib import Path

import pytest

from pydocq.analyzer.resolver import ElementType
from pydocq.utils.type_detection import ElementType
from pydocq.utils.type_detection import (
    get_element_name,
    get_element_qualname,
    get_element_type,
    is_callable,
    is_public_element,
)


class TestElementTypeDetection:
    """Test suite for centralized type detection."""

    def test_detects_modules(self):
        """Test module detection."""
        assert get_element_type(os) == ElementType.MODULE
        assert get_element_type(os.path) == ElementType.MODULE

    def test_detects_classes(self):
        """Test class detection."""
        assert get_element_type(str) == ElementType.CLASS
        assert get_element_type(dict) == ElementType.CLASS
        assert get_element_type(Path) == ElementType.CLASS

    def test_detects_functions(self):
        """Test function detection."""
        # Built-in functions may be detected differently
        # Test with a regular function instead
        def my_func():
            pass
        assert get_element_type(my_func) == ElementType.FUNCTION

    def test_detects_methods(self):
        """Test method detection."""
        # Test with instance methods
        class Sample:
            def my_method(self):
                pass

        assert get_element_type(Sample().my_method) == ElementType.METHOD

    def test_detects_properties(self):
        """Test property detection."""

        class Sample:
            @property
            def prop(self):
                return 42

        assert get_element_type(Sample.prop) == ElementType.PROPERTY

    def test_returns_unknown_for_unrecognized(self):
        """Test unknown type detection."""
        assert get_element_type(42) == ElementType.UNKNOWN
        assert get_element_type("string") == ElementType.UNKNOWN
        assert get_element_type([1, 2, 3]) == ElementType.UNKNOWN

    def test_handles_edge_cases(self):
        """Test edge cases."""
        # None
        assert get_element_type(None) == ElementType.UNKNOWN

        # Lambda
        assert get_element_type(lambda x: x) == ElementType.FUNCTION

        # Static method
        class Sample:
            @staticmethod
            def static_method():
                pass

        assert get_element_type(Sample.static_method) == ElementType.FUNCTION

        # Class method
        class Sample:
            @classmethod
            def class_method(cls):
                pass

        assert get_element_type(Sample.class_method) == ElementType.METHOD


class TestIsPublicElement:
    """Test suite for is_public_element function."""

    def test_public_methods_are_public(self):
        """Test that public methods are identified as public."""

        class Sample:
            def public_method(self):
                pass

        assert is_public_element(Sample.public_method, "public_method") is True

    def test_private_methods_are_private(self):
        """Test that private methods are identified as private."""

        class Sample:
            def _private_method(self):
                pass

        assert is_public_element(Sample._private_method, "_private_method") is False

    def test_dunder_methods_are_considered_public(self):
        """Test that dunder methods are considered public."""

        class Sample:
            def __init__(self):
                pass

            def __str__(self):
                return "Sample"

        assert is_public_element(Sample.__init__, "__init__") is True
        assert is_public_element(Sample.__str__, "__str__") is True

    def test_name_fallback(self):
        """Test that name parameter is used if provided."""

        class Sample:
            def method(self):
                pass

        # When name is provided, it should use that
        assert is_public_element(Sample.method, "public") is True
        assert is_public_element(Sample.method, "_private") is False


class TestGetElementName:
    """Test suite for get_element_name function."""

    def test_gets_function_name(self):
        """Test getting function name."""

        def my_function():
            pass

        assert get_element_name(my_function) == "my_function"

    def test_gets_class_name(self):
        """Test getting class name."""

        class MyClass:
            pass

        assert get_element_name(MyClass) == "MyClass"

    def test_returns_empty_string_for_nameless(self):
        """Test that nameless objects return empty string."""
        assert get_element_name(42) == ""
        assert get_element_name(None) == ""


class TestGetElementQualname:
    """Test suite for get_element_qualname function."""

    def test_gets_function_qualname(self):
        """Test getting function qualname."""

        def my_function():
            pass

        qualname = get_element_qualname(my_function)
        # qualname will include the test class scope if defined within a test method
        assert "my_function" in qualname

    def test_gets_method_qualname(self):
        """Test getting method qualname."""

        class MyClass:
            def my_method(self):
                pass

        qualname = get_element_qualname(MyClass.my_method)
        # qualname will include the test class scope if defined within a test method
        assert "MyClass" in qualname and "my_method" in qualname

    def test_returns_empty_string_for_nameless(self):
        """Test that nameless objects return empty string."""
        assert get_element_qualname(42) == ""
        assert get_element_qualname(None) == ""


class TestIsCallable:
    """Test suite for is_callable function."""

    def test_functions_are_callable(self):
        """Test that functions are identified as callable."""

        def my_function():
            pass

        assert is_callable(my_function) is True

    def test_methods_are_callable(self):
        """Test that methods are identified as callable."""

        class MyClass:
            def my_method(self):
                pass

        assert is_callable(MyClass().my_method) is True

    def test_classes_are_not_callable(self):
        """Test that classes are not identified as callable."""
        # Classes are callable in Python, but this function should return False for them
        assert is_callable(str) is False
        assert is_callable(int) is False

    def test_non_callables_are_not_callable(self):
        """Test that non-callables are identified as not callable."""
        assert is_callable(42) is False
        assert is_callable("string") is False
        assert is_callable([1, 2, 3]) is False

    def test_builtin_functions_are_callable(self):
        """Test that builtin functions are identified as callable."""
        assert is_callable(len) is True
        assert is_callable(print) is True
