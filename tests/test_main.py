"""Tests for __main__ module."""

import json

from typer.testing import CliRunner


def test_main_module_exists() -> None:
    """Test that the __main__ module can be imported."""
    import pydocq.__main__  # noqa: F401


def test_main_module_exports_app() -> None:
    """Test that the __main__ module exports the app."""
    import pydocq.__main__

    assert hasattr(pydocq.__main__, "app")


def test_main_module_runs_via_cli_runner() -> None:
    """Test that the __main__ module works via CliRunner."""
    from typer.testing import CliRunner

    from pydocq.__main__ import app

    runner = CliRunner()
    result = runner.invoke(app, ["json.dumps"])
    assert result.exit_code == 0

    # Parse JSON output
    output = json.loads(result.stdout)
    assert output["path"] == "json.dumps"
    assert output["type"] == "function"


def test_main_module_with_version_flag() -> None:
    """Test that the __main__ module respects --version flag."""
    from typer.testing import CliRunner

    from pydocq.__main__ import app

    runner = CliRunner()
    result = runner.invoke(app, ["--version", "json.dumps"])
    assert result.exit_code == 0
    assert "docs-cli" in result.stdout


def test_main_module_with_compact_flag() -> None:
    """Test that the __main__ module respects --compact flag."""
    from typer.testing import CliRunner

    from pydocq.__main__ import app

    runner = CliRunner()
    result = runner.invoke(app, ["--compact", "json.dumps"])
    assert result.exit_code == 0

    output = json.loads(result.stdout)
    # Compact mode only has basic fields
    assert set(output.keys()) == {"path", "type", "module_path"}
    assert output["path"] == "json.dumps"
