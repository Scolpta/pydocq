"""Tests for hyphenated package name support."""

import json

from typer.testing import CliRunner

from pydocq.cli import app

runner = CliRunner()


def test_hyphen_normalization_doesnt_break_normal_names() -> None:
    """Test that packages without hyphens still work correctly."""
    # Test several standard library packages to ensure no regression
    test_packages = ["json", "os", "sys"]

    for package in test_packages:
        result = runner.invoke(app, [package])
        assert result.exit_code == 0, f"Failed for package: {package}"


def test_hyphenated_package_name_not_found() -> None:
    """Test error handling when package doesn't exist."""
    result = runner.invoke(app, ["nonexistent-package"])
    assert result.exit_code == 1


def test_hyphenated_package_name_with_element() -> None:
    """Test that element paths still work correctly."""
    # Test with a normal package to ensure the normalization doesn't break
    # element access
    result = runner.invoke(app, ["json.dumps"])
    assert result.exit_code == 0

    output = json.loads(result.stdout)
    assert output["path"] == "json.dumps"
