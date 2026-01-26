"""Tests for the analyze command."""

import json
import os
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from pydocq.cli import app

runner = CliRunner()


def _create_test_file(content: str, filename: str) -> str:
    """Helper to create a test file with a relative path."""
    # Create in current directory to avoid absolute path security check
    filepath = Path(filename)
    filepath.write_text(content)
    return str(filepath)


def test_analyze_command_basic() -> None:
    """Test basic file analysis."""
    test_file = _create_test_file("""
def test_function():
    '''A test function.'''
    pass

class TestClass:
    '''A test class.'''
    def method(self):
        pass
""", "test_analyze_basic.py")

    try:
        result = runner.invoke(app, ["analyze", test_file])
        assert result.exit_code == 0

        output = json.loads(result.stdout)
        assert "functions" in output
        assert "classes" in output
        assert len(output["functions"]) == 1
        assert output["functions"][0]["name"] == "test_function"
        assert len(output["classes"]) == 1
        assert output["classes"][0]["name"] == "TestClass"
    finally:
        Path(test_file).unlink(missing_ok=True)


def test_analyze_command_with_element_class() -> None:
    """Test analyzing a specific class."""
    test_file = _create_test_file("""
def test_function():
    pass

class MyClass:
    def method(self):
        pass

class OtherClass:
    def other_method(self):
        pass
""", "test_analyze_class.py")

    try:
        result = runner.invoke(app, ["analyze", test_file, "--element", "MyClass"])
        assert result.exit_code == 0

        output = json.loads(result.stdout)
        assert output["name"] == "MyClass"
        assert "methods" in output
        assert len(output["methods"]) == 1
        assert output["methods"][0]["name"] == "method"
    finally:
        Path(test_file).unlink(missing_ok=True)


def test_analyze_command_with_element_function() -> None:
    """Test analyzing a specific function."""
    test_file = _create_test_file("""
def func1():
    pass

def func2():
    pass

class MyClass:
    pass
""", "test_analyze_func.py")

    try:
        result = runner.invoke(app, ["analyze", test_file, "--element", "func1"])
        assert result.exit_code == 0

        output = json.loads(result.stdout)
        assert output["name"] == "func1"
        assert "args" in output
    finally:
        Path(test_file).unlink(missing_ok=True)


def test_analyze_command_element_not_found() -> None:
    """Test error when element is not found."""
    test_file = _create_test_file("""
def existing_function():
    pass
""", "test_analyze_notfound.py")

    try:
        result = runner.invoke(app, ["analyze", test_file, "--element", "nonexistent"])
        assert result.exit_code == 1
        # Check output contains error message (may be in stdout or exception)
        assert "nonexistent" in str(result.exception) or "not found" in result.stdout
    finally:
        Path(test_file).unlink(missing_ok=True)


def test_analyze_command_file_not_found() -> None:
    """Test error when file doesn't exist."""
    result = runner.invoke(app, ["analyze", "nonexistent_file.py"])
    assert result.exit_code == 1


def test_analyze_command_syntax_error() -> None:
    """Test error when file has syntax errors."""
    test_file = _create_test_file("""
def broken_function(
    # Missing closing parenthesis
""", "test_analyze_syntax.py")

    try:
        result = runner.invoke(app, ["analyze", test_file])
        assert result.exit_code == 1
    finally:
        Path(test_file).unlink(missing_ok=True)


def test_analyze_command_security_error() -> None:
    """Test security error for dangerous paths."""
    # Test with absolute path (should be blocked)
    result = runner.invoke(app, ["analyze", "/etc/passwd"])
    assert result.exit_code == 1


def test_analyze_command_in_help() -> None:
    """Test that analyze command appears in help."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "analyze" in result.stdout


def test_analyze_command_empty_file() -> None:
    """Test analyzing an empty Python file."""
    test_file = _create_test_file("", "test_analyze_empty.py")

    try:
        result = runner.invoke(app, ["analyze", test_file])
        assert result.exit_code == 0

        output = json.loads(result.stdout)
        assert output["functions"] == []
        assert output["classes"] == []
        assert output["imports"] == []
    finally:
        Path(test_file).unlink(missing_ok=True)


def test_analyze_command_with_imports() -> None:
    """Test analyzing a file with imports."""
    test_file = _create_test_file("""
import os
import sys
from typing import List

def my_function():
    pass
""", "test_analyze_imports.py")

    try:
        result = runner.invoke(app, ["analyze", test_file])
        assert result.exit_code == 0

        output = json.loads(result.stdout)
        assert "imports" in output
        assert len(output["imports"]) == 3
        # Check import structure (has 'names' array, not single 'name')
        import_names = []
        for imp in output["imports"]:
            import_names.extend(imp.get("names", []))
        assert "os" in import_names
        assert "sys" in import_names
        assert "List" in import_names
    finally:
        Path(test_file).unlink(missing_ok=True)
