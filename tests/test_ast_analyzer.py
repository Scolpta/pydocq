"""Tests for AST static analysis."""

import ast

import pytest

from docs_cli.analyzer.ast_analyzer import (
    ASTClassInfo,
    ASTFunctionInfo,
    ASTImportInfo,
    ASTModuleInfo,
    ASTSecurityError,
    analyze_file,
    analyze_module,
    analyze_object,
    find_calls,
    get_dependencies,
    parse_source,
)


def test_simple_function() -> None:
    """Example function for AST testing."""

    def example_func(x: int, y: str) -> bool:
        """Example function.

        Args:
            x: An integer
            y: A string

        Returns:
            A boolean
        """
        return True

    return example_func


def test_simple_class() -> None:
    """Example class for AST testing."""

    class ExampleClass:
        """Example class for testing."""

        def __init__(self, value: int):
            """Initialize with value."""
            self.value = value

        def method(self) -> int:
            """Return the value."""
            return self.value

    return ExampleClass


class TestParseSource:
    """Tests for parse_source function."""

    def test_parse_valid_code(self) -> None:
        """Test parsing valid Python code."""
        source = "def foo(): pass"
        tree = parse_source(source)

        assert isinstance(tree, ast.Module)

    def test_parse_invalid_code(self) -> None:
        """Test parsing invalid Python code."""
        source = "def foo("

        with pytest.raises(SyntaxError):
            parse_source(source)


class TestAnalyzeModule:
    """Tests for analyze_module function."""

    def test_analyze_simple_module(self) -> None:
        """Test analyzing a simple module."""
        source = '''
"""Module docstring."""

def func1():
    """Function 1."""
    pass

def func2(x, y):
    """Function 2."""
    return x + y

class MyClass:
    """A class."""
    pass
'''
        tree = parse_source(source)
        info = analyze_module(tree, "test_module")

        assert info.path == "test_module"
        assert info.docstring == "Module docstring."
        assert len(info.functions) == 2
        assert len(info.classes) == 1
        assert info.functions[0].name == "func1"
        assert info.classes[0].name == "MyClass"

    def test_analyze_module_with_imports(self) -> None:
        """Test analyzing module with imports."""
        source = '''
import os
import sys
from typing import List
from .module import func
'''
        tree = parse_source(source)
        info = analyze_module(tree, "test_module")

        assert len(info.imports) == 4
        assert any(imp.names == ["os"] for imp in info.imports)
        assert any(imp.is_from for imp in info.imports)


class TestAnalyzeFunction:
    """Tests for function analysis."""

    def test_analyze_function_basic(self) -> None:
        """Test analyzing basic function."""
        source = '''
def func(a, b, c):
    """Test function."""
    pass
'''
        tree = parse_source(source)
        info = analyze_module(tree, "test")

        func = info.functions[0]
        assert func.name == "func"
        assert func.args == ["a", "b", "c"]
        assert func.docstring == "Test function."

    def test_analyze_function_with_return(self) -> None:
        """Test analyzing function with return type."""
        source = '''
def func() -> int:
    """Test function."""
    return 42
'''
        tree = parse_source(source)
        info = analyze_module(tree, "test")

        func = info.functions[0]
        assert func.returns == "int"

    def test_analyze_async_function(self) -> None:
        """Test analyzing async function."""
        source = '''
async def async_func():
    """Async function."""
    pass
'''
        tree = parse_source(source)
        info = analyze_module(tree, "test")

        func = info.functions[0]
        assert func.is_async is True


class TestAnalyzeClass:
    """Tests for class analysis."""

    def test_analyze_class_basic(self) -> None:
        """Test analyzing basic class."""
        source = '''
class MyClass:
    """Test class."""
    pass
'''
        tree = parse_source(source)
        info = analyze_module(tree, "test")

        cls = info.classes[0]
        assert cls.name == "MyClass"
        assert cls.docstring == "Test class."

    def test_analyze_class_with_inheritance(self) -> None:
        """Test analyzing class with base classes."""
        source = '''
class MyClass(BaseClass, Other):
    """Test class."""
    pass
'''
        tree = parse_source(source)
        info = analyze_module(tree, "test")

        cls = info.classes[0]
        assert len(cls.bases) == 2
        assert "BaseClass" in cls.bases

    def test_analyze_class_with_methods(self) -> None:
        """Test analyzing class with methods."""
        source = '''
class MyClass:
    """Test class."""

    def method1(self):
        """Method 1."""
        pass

    def method2(self, x):
        """Method 2."""
        pass
'''
        tree = parse_source(source)
        info = analyze_module(tree, "test")

        cls = info.classes[0]
        assert len(cls.methods) == 2
        assert cls.methods[0].name == "method1"


class TestAnalyzeObject:
    """Tests for analyze_object function."""

    def test_analyze_function_object(self) -> None:
        """Test analyzing a function object."""
        # Use a module-level function to avoid indentation issues
        import json

        info = analyze_object(json.dumps)

        assert isinstance(info, ASTFunctionInfo)
        assert info.name == "dumps"

    def test_analyze_class_object(self) -> None:
        """Test analyzing a class object."""
        import json

        # JSONEncoder is a class
        info = analyze_object(json.JSONEncoder)

        assert isinstance(info, ASTClassInfo)
        assert info.name == "JSONEncoder"

    def test_analyze_builtin_raises_error(self) -> None:
        """Test that analyzing built-in raises error."""
        with pytest.raises(ValueError):
            analyze_object(len)


class TestGetDependencies:
    """Tests for get_dependencies function."""

    def test_get_external_dependencies(self) -> None:
        """Test getting external dependencies."""
        source = '''
import os
import sys
from typing import List
'''
        tree = parse_source(source)
        info = analyze_module(tree, "test")

        deps = get_dependencies(info)

        assert "external" in deps
        assert len(deps["external"]) > 0
        assert any("os" in dep or "typing" in dep for dep in deps["external"])


class TestFindCalls:
    """Tests for find_calls function."""

    def test_find_calls_placeholder(self) -> None:
        """Test find_calls (currently placeholder)."""
        source = "def func(): pass"
        tree = parse_source(source)
        info = analyze_module(tree, "test")

        calls = find_calls(info, "func")

        # Currently returns empty list (placeholder)
        assert isinstance(calls, list)


class TestASTSecurity:
    """Tests for AST file path security validation."""

    def test_path_traversal_with_double_dot_blocked(self) -> None:
        """Test that path traversal with ../ is blocked."""
        with pytest.raises(ASTSecurityError, match="dangerous pattern"):
            analyze_file("../test.py")

    def test_path_traversal_with_double_dot_and_path_blocked(self) -> None:
        """Test that path traversal with ../something is blocked."""
        with pytest.raises(ASTSecurityError, match="dangerous pattern"):
            analyze_file("../etc/passwd.py")

    def test_etc_directory_blocked(self) -> None:
        """Test that /etc/ directory access is blocked."""
        with pytest.raises(ASTSecurityError, match="dangerous pattern"):
            analyze_file("/etc/test.py")

    def test_sys_directory_blocked(self) -> None:
        """Test that /sys/ directory access is blocked."""
        with pytest.raises(ASTSecurityError, match="dangerous pattern"):
            analyze_file("/sys/test.py")

    def test_proc_directory_blocked(self) -> None:
        """Test that /proc/ directory access is blocked."""
        with pytest.raises(ASTSecurityError, match="dangerous pattern"):
            analyze_file("/proc/test.py")

    def test_root_directory_blocked(self) -> None:
        """Test that /root/ directory access is blocked."""
        with pytest.raises(ASTSecurityError, match="dangerous pattern"):
            analyze_file("/root/test.py")

    def test_home_directory_blocked(self) -> None:
        """Test that ~ home directory shortcut is blocked."""
        with pytest.raises(ASTSecurityError, match="dangerous pattern"):
            analyze_file("~/test.py")

    def test_absolute_path_blocked(self) -> None:
        """Test that absolute paths are blocked."""
        with pytest.raises(ASTSecurityError, match="Absolute paths are not allowed"):
            analyze_file("/usr/lib/python3/os.py")

    def test_non_py_file_blocked(self) -> None:
        """Test that non-.py files are blocked."""
        with pytest.raises(ASTSecurityError, match="Only Python files"):
            analyze_file("test.txt")

    def test_non_py_file_with_different_extension_blocked(self) -> None:
        """Test that files with other extensions are blocked."""
        with pytest.raises(ASTSecurityError, match="Only Python files"):
            analyze_file("test.md")

    def test_nonexistent_py_file_raises_file_not_found(self) -> None:
        """Test that nonexistent .py files raise FileNotFoundError."""
        # This should pass validation but fail at file existence check
        with pytest.raises(FileNotFoundError, match="File not found"):
            analyze_file("nonexistent.py")
