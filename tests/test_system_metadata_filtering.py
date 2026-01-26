"""Tests for --include-system flag."""

import json

from typer.testing import CliRunner

from pydocq.cli import app

runner = CliRunner()


def test_exclude_system_by_default() -> None:
    """Test that system metadata is filtered out by default."""
    result = runner.invoke(app, ["--list-members", "json"])
    assert result.exit_code == 0

    output = json.loads(result.stdout)

    # Check that dunder attributes are not present
    member_names = [m["name"] for m in output["members"]]

    # Common dunder attributes that should be filtered out
    system_attrs = ["__all__", "__author__", "__builtins__", "__cached__",
                   "__doc__", "__file__", "__name__", "__package__",
                   "__path__", "__version__"]

    for attr in system_attrs:
        assert attr not in member_names, f"System attribute {attr} should be filtered out"

    # Check that regular members are still present
    assert "codecs" in member_names
    assert "dump" in member_names


def test_include_system_flag() -> None:
    """Test that --include-system includes dunder attributes."""
    result = runner.invoke(app, ["--list-members", "--include-system", "json"])
    assert result.exit_code == 0

    output = json.loads(result.stdout)

    member_names = [m["name"] for m in output["members"]]

    # With --include-system, dunder attributes should be present
    system_attrs = ["__all__", "__author__", "__version__", "__doc__", "__name__"]
    present_attrs = [attr for attr in system_attrs if attr in member_names]

    # At least some dunder attributes should be present
    assert len(present_attrs) > 0, "Expected some dunder attributes with --include-system"


def test_include_system_help() -> None:
    """Test that --include-system appears in help."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "include-system" in result.stdout
