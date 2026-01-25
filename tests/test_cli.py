"""Tests for CLI interface."""

import json

from typer.testing import CliRunner

from pydocq.cli import app

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
    # Default output includes signature and docstring
    assert "docstring" in output


def test_query_command_nested() -> None:
    """Test the query command with nested path."""
    result = runner.invoke(app, ["os.path.join"])
    assert result.exit_code == 0

    output = json.loads(result.stdout)
    assert output["path"] == "os.path.join"
    assert output["type"] == "function"
    assert output["module_path"] is not None
    # Default output includes signature and docstring
    assert "signature" in output
    assert "docstring" in output


def test_query_command_class() -> None:
    """Test the query command with a class."""
    result = runner.invoke(app, ["builtins.str"])
    assert result.exit_code == 0

    output = json.loads(result.stdout)
    assert output["path"] == "builtins.str"
    assert output["type"] == "class"
    # Classes have signature (__init__) or docstring
    assert "docstring" in output


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


def test_query_compact_option() -> None:
    """Test the --compact option."""
    result = runner.invoke(app, ["--compact", "os.path.join"])
    assert result.exit_code == 0

    output = json.loads(result.stdout)
    # Compact mode only has basic fields
    assert set(output.keys()) == {"path", "type", "module_path"}
    assert output["path"] == "os.path.join"


def test_query_verbose_option() -> None:
    """Test the --verbose option."""
    result = runner.invoke(app, ["--verbose", "os.path.join"])
    assert result.exit_code == 0

    output = json.loads(result.stdout)
    # Verbose mode has all fields
    assert "path" in output
    assert "type" in output
    assert "module_path" in output
    assert "signature" in output
    assert "docstring" in output
    assert "source_location" in output


def test_query_no_docstring_option() -> None:
    """Test the --no-docstring option."""
    result = runner.invoke(app, ["--no-docstring", "os.path.join"])
    assert result.exit_code == 0

    output = json.loads(result.stdout)
    assert "docstring" not in output
    assert "signature" in output


def test_query_no_signature_option() -> None:
    """Test the --no-signature option."""
    result = runner.invoke(app, ["--no-signature", "os.path.join"])
    assert result.exit_code == 0

    output = json.loads(result.stdout)
    assert "signature" not in output
    assert "docstring" in output


def test_query_include_source_option() -> None:
    """Test the --include-source option."""
    result = runner.invoke(app, ["--include-source", "os.path.join"])
    assert result.exit_code == 0

    output = json.loads(result.stdout)
    assert "source_location" in output
    assert "file" in output["source_location"] or "line" in output["source_location"]


def test_query_list_members_module() -> None:
    """Test the --list-members option for modules."""
    result = runner.invoke(app, ["--list-members", "json"])
    assert result.exit_code == 0

    output = json.loads(result.stdout)
    assert "path" in output
    assert "members" in output
    assert "classes" in output or "functions" in output
    assert len(output["members"]) > 0


def test_query_list_members_class() -> None:
    """Test the --list-members option for classes."""
    result = runner.invoke(app, ["--list-members", "builtins.str"])
    assert result.exit_code == 0

    output = json.loads(result.stdout)
    assert "path" in output
    assert "type" in output
    assert "members" in output


def test_query_list_members_with_private() -> None:
    """Test the --list-members option with --include-private."""
    result_no_private = runner.invoke(app, ["--list-members", "json"])
    result_with_private = runner.invoke(app, ["--list-members", "--include-private", "json"])

    assert result_no_private.exit_code == 0
    assert result_with_private.exit_code == 0

    output_no_private = json.loads(result_no_private.stdout)
    output_with_private = json.loads(result_with_private.stdout)

    # With private should have more or equal members
    assert len(output_with_private["members"]) >= len(output_no_private["members"])


def test_query_list_members_function_returns_error() -> None:
    """Test that --list-members on a function returns an error message."""
    result = runner.invoke(app, ["--list-members", "os.path.join"])
    assert result.exit_code == 1

    # Error message goes to stderr
    if result.stderr:
        assert "Cannot list members" in result.stderr


def test_query_format_raw() -> None:
    """Test the --format raw option."""
    result = runner.invoke(app, ["--format", "raw", "json.dumps"])
    assert result.exit_code == 0

    output = result.stdout
    assert "Path: json.dumps" in output
    assert "Type: function" in output


def test_query_format_signature() -> None:
    """Test the --format signature option."""
    result = runner.invoke(app, ["--format", "signature", "json.dumps"])
    assert result.exit_code == 0

    output = result.stdout.strip()
    assert "json.dumps(" in output


def test_query_format_markdown() -> None:
    """Test the --format markdown option."""
    result = runner.invoke(app, ["--format", "markdown", "json.dumps"])
    assert result.exit_code == 0

    output = result.stdout
    assert "# `json.dumps`" in output
    assert "## Signature" in output


def test_query_format_yaml() -> None:
    """Test the --format yaml option."""
    result = runner.invoke(app, ["--format", "yaml", "json.dumps"])
    assert result.exit_code == 0

    output = result.stdout
    assert '"path": "json.dumps"' in output


def test_query_format_invalid() -> None:
    """Test that invalid format returns error."""
    result = runner.invoke(app, ["--format", "invalid", "json.dumps"])
    assert result.exit_code == 1

    if result.stderr:
        assert "Unsupported format" in result.stderr
