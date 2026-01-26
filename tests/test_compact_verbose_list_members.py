"""Tests for --compact and --verbose flags with --list-members."""

import json

from typer.testing import CliRunner

from pydocq.cli import app

runner = CliRunner()


def test_compact_mode_with_list_members() -> None:
    """Test --compact with --list-members shows only names."""
    result = runner.invoke(app, ["--list-members", "--compact", "json"])
    assert result.exit_code == 0

    output = json.loads(result.stdout)

    # Compact mode should have categories with lists of names (not dicts)
    assert "classes" in output
    assert "functions" in output
    assert "submodules" in output

    # Check that values are strings (names), not dicts
    assert isinstance(output["functions"], list)
    if len(output["functions"]) > 0:
        assert isinstance(output["functions"][0], str)

    # Should have fewer total fields than default mode
    assert set(output.keys()) == {"path", "classes", "functions", "methods", "properties", "submodules"}


def test_verbose_mode_with_list_members() -> None:
    """Test --verbose with --list-members includes full details."""
    result = runner.invoke(app, ["--list-members", "--verbose", "json"])
    assert result.exit_code == 0

    output = json.loads(result.stdout)

    # Verbose mode should have members with additional fields
    assert "members" in output
    if len(output["members"]) > 0:
        # First member should have more than just basic fields
        first_member = output["members"][0]
        # Should have at least the basic fields
        assert "name" in first_member
        # And additional fields in verbose mode
        assert "docstring" in first_member or "signature" in first_member


def test_default_mode_still_works() -> None:
    """Test that default mode (neither compact nor verbose) still works."""
    result = runner.invoke(app, ["--list-members", "json"])
    assert result.exit_code == 0

    output = json.loads(result.stdout)

    # Default mode should have member dicts with basic info
    assert "members" in output
    if len(output["members"]) > 0:
        member = output["members"][0]
        # Should have basic fields
        assert "name" in member
        assert "type" in member


def test_compact_with_include_system() -> None:
    """Test that --compact works with --include-system."""
    result = runner.invoke(app, ["--list-members", "--compact", "--include-system", "json"])
    assert result.exit_code == 0

    output = json.loads(result.stdout)

    # Compact mode should still have just names
    assert isinstance(output["functions"], list)
    if len(output["functions"]) > 0:
        assert isinstance(output["functions"][0], str)


def test_verbose_with_include_system() -> None:
    """Test that --verbose works with --include-system."""
    result = runner.invoke(app, ["--list-members", "--verbose", "--include-system", "json"])
    assert result.exit_code == 0

    output = json.loads(result.stdout)

    # With --include-system, should have more members (including dunder)
    # And they should have verbose details
    assert "members" in output
    assert len(output["members"]) > 10  # Should have many more with dunder


def test_compact_output_matches_expected() -> None:
    """Test that compact output matches the expected format from the issue."""
    result = runner.invoke(app, ["--list-members", "--compact", "json"])
    assert result.exit_code == 0

    output = json.loads(result.stdout)

    # Expected format from issue:
    # {"path": "better_py.monads.maybe", "classes": ["Maybe", "Some", "Nothing"]}
    # Just the names, no metadata
    assert output["path"] == "json"
    assert isinstance(output["classes"], list)
    assert isinstance(output["functions"], list)


def test_verbose_output_includes_docstrings() -> None:
    """Test that verbose mode includes docstrings."""
    result = runner.invoke(app, ["--list-members", "--verbose", "json"])
    assert result.exit_code == 0

    output = json.loads(result.stdout)

    # Find a function with a docstring
    dump_member = [m for m in output["members"] if m["name"] == "dump"][0]

    # Should have docstring in verbose mode
    assert "docstring" in dump_member
    assert dump_member["docstring"]  # Should be non-empty
