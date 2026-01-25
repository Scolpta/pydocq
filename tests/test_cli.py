"""Tests for CLI interface."""

from typer.testing import CliRunner

from docs_cli.cli import app

runner = CliRunner()


def test_cli_runs() -> None:
    """Test that the CLI runs without errors."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Query Python package documentation" in result.stdout


def test_query_command() -> None:
    """Test the query command."""
    result = runner.invoke(app, ["pandas.DataFrame"])
    assert result.exit_code == 0
    assert "Hello from docs-cli!" in result.stdout
    assert "Querying: pandas.DataFrame" in result.stdout


def test_query_command_simple() -> None:
    """Test the query command with a simple package."""
    result = runner.invoke(app, ["os"])
    assert result.exit_code == 0
    assert "Querying: os" in result.stdout
