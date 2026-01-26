"""Tests for --for-ai flag."""

import json

from typer.testing import CliRunner

from pydocq.cli import app

runner = CliRunner()


def test_for_ai_flag_sets_llm_format() -> None:
    """Test that --for-ai sets output format to llm."""
    result = runner.invoke(app, ["--for-ai", "json.dump"])
    assert result.exit_code == 0

    output = json.loads(result.stdout)
    # LLM format has these fields
    assert "summary" in output
    assert "key_params" in output
    assert "token_count" in output
    # Standard format doesn't have these
    assert output.get("type") == "function"


def test_for_ai_flag_simplifies_cli() -> None:
    """Test that --for-ai is equivalent to combining multiple flags."""
    # With --for-ai
    result_ai = runner.invoke(app, ["--for-ai", "json.dump"])
    assert result_ai.exit_code == 0

    # Without --for-ai (should produce different output)
    result_regular = runner.invoke(app, ["json.dump"])
    assert result_regular.exit_code == 0

    # --for-ai should produce LLM format (with summary, key_params, etc.)
    output_ai = json.loads(result_ai.stdout)
    output_regular = json.loads(result_regular.stdout)

    # LLM format has these fields
    assert "summary" in output_ai
    assert "token_count" in output_ai

    # Regular format has different fields
    assert "summary" not in output_regular
    assert "token_count" not in output_regular


def test_for_ai_flag_with_list_members() -> None:
    """Test that --for-ai works with --list-members."""
    result = runner.invoke(app, ["--for-ai", "--list-members", "json"])
    assert result.exit_code == 0

    output = json.loads(result.stdout)
    # --list-members output structure
    assert "members" in output or "classes" in output or "functions" in output


def test_for_ai_flag_cannot_be_overridden() -> None:
    """Test that --for-ai always applies its settings."""
    # When both --for-ai and --format are specified, --for-ai wins
    result = runner.invoke(app, ["--for-ai", "--format", "json", "json.dump"])
    assert result.exit_code == 0

    output = json.loads(result.stdout)
    # --for-ai always sets LLM format, even if --format is also specified
    assert "summary" in output
    assert "token_count" in output


def test_for_ai_flag_works_with_various_targets() -> None:
    """Test that --for-ai works with different target types."""
    # Test with function
    result_func = runner.invoke(app, ["--for-ai", "json.dump"])
    assert result_func.exit_code == 0
    output_func = json.loads(result_func.stdout)
    assert "summary" in output_func

    # Test with module
    result_mod = runner.invoke(app, ["--for-ai", "json"])
    assert result_mod.exit_code == 0
    output_mod = json.loads(result_mod.stdout)
    assert "summary" in output_mod or "members" in output_mod


def test_for_ai_flag_in_help() -> None:
    """Test that --for-ai is documented in help."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "--for-ai" in result.stdout
    assert "AI-optimized" in result.stdout
