"""Tests for CLI interface."""

import json

from typer.testing import CliRunner

from docs_cli.cli import app

runner = CliRunner(mix_stderr=False)


def test_cli_runs() -> None:
    """Test that the CLI runs without errors."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Query Python package documentation" in result.stdout


def test_query_command() -> None:
    """Test the query command with standard library."""
    result = runner.invoke(app, ["os"])
    assert result.exit_code == 0

    # Parse JSON output
    output = json.loads(result.stdout)
    assert output["path"] == "os"
    assert output["type"] == "module"
    assert output["module_path"] == "os"


def test_query_command_nested() -> None:
    """Test the query command with nested path."""
    result = runner.invoke(app, ["os.path.join"])
    assert result.exit_code == 0

    output = json.loads(result.stdout)
    assert output["path"] == "os.path.join"
    assert output["type"] == "function"
    assert output["module_path"] is not None


def test_query_command_class() -> None:
    """Test the query command with a class."""
    result = runner.invoke(app, ["builtins.str"])
    assert result.exit_code == 0

    output = json.loads(result.stdout)
    assert output["path"] == "builtins.str"
    assert output["type"] == "class"


def test_query_command_nonexistent_package() -> None:
    """Test the query command with non-existent package."""
    result = runner.invoke(app, ["nonexistentpackage"])
    assert result.exit_code == 1
    # The error message goes to stderr
    if result.stderr:
        assert "nonexistentpackage" in result.stderr


def test_query_command_nonexistent_element() -> None:
    """Test the query command with non-existent element."""
    result = runner.invoke(app, ["os.NonExistentClass"])
    assert result.exit_code == 1
    # The error message goes to stderr
    if result.stderr:
        assert "NonExistentClass" in result.stderr or "not found" in result.stderr
