"""Tests for usage example extraction from test files."""

import json
import tempfile
from pathlib import Path

from typer.testing import CliRunner

from pydocq.analyzer.example_extractor import (
    UsageExample,
    _get_context,
    _is_valid_call,
    extract_examples_from_tests,
    extract_examples_from_tests_for_target,
)

runner = CliRunner()


class TestIsValidCall:
    """Test suite for _is_valid_call helper."""

    def test_valid_function_call(self) -> None:
        """Test that valid function call is accepted."""
        code = "result = my_function(arg1, arg2)"
        assert _is_valid_call(code, "my_function") is True

    def test_function_definition_is_rejected(self) -> None:
        """Test that function definitions are rejected."""
        code = "def my_function():"
        assert _is_valid_call(code, "my_function") is False

    def test_async_function_definition_is_rejected(self) -> None:
        """Test that async function definitions are rejected."""
        code = "async def my_function():"
        assert _is_valid_call(code, "my_function") is False

    def test_import_statement_is_rejected(self) -> None:
        """Test that import statements are rejected."""
        code = "from my_module import my_function"
        assert _is_valid_call(code, "my_function") is False

    def test_comment_is_rejected(self) -> None:
        """Test that comments are rejected."""
        code = "# my_function(arg1)"
        assert _is_valid_call(code, "my_function") is False

    def test_class_definition_is_rejected(self) -> None:
        """Test that class definitions are rejected."""
        code = "class my_function:"
        assert _is_valid_call(code, "my_function") is False

    def test_no_parenthesis_is_rejected(self) -> None:
        """Test that code without parenthesis is rejected."""
        code = "result = my_function"
        assert _is_valid_call(code, "my_function") is False


class TestGetContext:
    """Test suite for _get_context helper."""

    def test_context_includes_surrounding_lines(self) -> None:
        """Test that context includes lines before and after."""
        lines = ["line 1", "line 2", "line 3", "line 4", "line 5"]
        context = _get_context(lines, 2)  # Middle line

        # Should have line numbers and include surrounding lines
        assert "1: line 1" in context
        assert "2: line 2" in context
        assert "3: line 3" in context
        assert "4: line 4" in context

    def test_context_at_start_of_file(self) -> None:
        """Test context when line is at start of file."""
        lines = ["line 1", "line 2", "line 3"]
        context = _get_context(lines, 0)

        # Should not go negative
        assert "1: line 1" in context
        assert "2: line 2" in context
        assert "3: line 3" in context

    def test_context_at_end_of_file(self) -> None:
        """Test context when line is at end of file."""
        lines = ["line 1", "line 2", "line 3"]
        context = _get_context(lines, 2)

        # Should not go beyond length
        assert "1: line 1" in context
        assert "2: line 2" in context
        assert "3: line 3" in context


class TestExtractExamplesFromTests:
    """Test suite for extract_examples_from_tests function."""

    def test_extract_simple_call(self) -> None:
        """Test extracting simple function call."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text(
                """
def test_my_func():
    result = my_function(arg1, arg2)
    assert result == expected
"""
            )

            examples = extract_examples_from_tests("my_function", [tmpdir])

            assert len(examples) == 1
            assert "my_function" in examples[0].code
            assert "arg1" in examples[0].code

    def test_extract_multiple_calls(self) -> None:
        """Test extracting multiple calls."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text(
                """
def test_1():
    my_function(a)

def test_2():
    my_function(b, c)

def test_3():
    my_function(d, e, f)
"""
            )

            examples = extract_examples_from_tests("my_function", [tmpdir])

            assert len(examples) == 3

    def test_filters_non_calls(self) -> None:
        """Test that non-call lines are filtered out."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text(
                """
def my_function():  # Not a call
    pass

# my_function() in comment

result = my_function()  # Actual call
"""
            )

            examples = extract_examples_from_tests("my_function", [tmpdir])

            # Should only find the actual call
            assert len(examples) == 1
            assert "result = my_function()" in examples[0].code

    def test_includes_context(self) -> None:
        """Test that context is included."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text(
                """
def test_something():
    # Setup
    data = prepare_data()

    # Call function
    result = my_function(data)

    # Assert
    assert result is not None
"""
            )

            examples = extract_examples_from_tests("my_function", [tmpdir])

            assert len(examples) == 1
            # Context should include surrounding lines
            assert len(examples[0].context.split("\n")) >= 3

    def test_respects_max_examples_limit(self) -> None:
        """Test that max_examples limit is respected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            # Create 15 calls
            lines = ["    my_function({})".format(i) for i in range(15)]
            test_file.write_text("\n".join(lines))

            examples = extract_examples_from_tests("my_function", [tmpdir], max_examples=5)

            assert len(examples) <= 5

    def test_handles_nonexistent_directory(self) -> None:
        """Test that nonexistent directories are handled gracefully."""
        examples = extract_examples_from_tests("my_function", ["/nonexistent/path"])

        assert len(examples) == 0

    def test_searches_multiple_directories(self) -> None:
        """Test that multiple test directories are searched."""
        with tempfile.TemporaryDirectory() as tmpdir1:
            with tempfile.TemporaryDirectory() as tmpdir2:
                # Create file in first directory
                test_file1 = Path(tmpdir1) / "test.py"
                test_file1.write_text("my_function(a)\n")

                # Create file in second directory
                test_file2 = Path(tmpdir2) / "test.py"
                test_file2.write_text("my_function(b)\n")

                examples = extract_examples_from_tests("my_function", [tmpdir1, tmpdir2])

                # Should find examples from both directories
                assert len(examples) == 2


class TestExtractExamplesForTarget:
    """Test suite for extract_examples_from_tests_for_target function."""

    def test_extract_for_simple_function(self) -> None:
        """Test extracting examples for simple function name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("json.dump(data, fp)\n")

            examples = extract_examples_from_tests_for_target("json.dump", [tmpdir])

            assert len(examples) == 1
            assert "dump" in examples[0].code

    def test_extract_for_method(self) -> None:
        """Test extracting examples for method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("df.merge(other_df)\n")

            examples = extract_examples_from_tests_for_target("DataFrame.merge", [tmpdir])

            assert len(examples) == 1
            assert "merge" in examples[0].code


class TestCLIIntegration:
    """Test suite for CLI integration with --examples-from flag."""

    def test_examples_from_flag_works(self) -> None:
        """Test that --examples-from flag works."""
        from pydocq.cli import app

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test file with json.dump usage
            test_file = Path(tmpdir) / "test_json.py"
            test_file.write_text(
                """
import json

def test_dump():
    fp = open('out.json', 'w')
    json.dump({'a': 1}, fp)
"""
            )

            result = runner.invoke(app, ["--examples-from", tmpdir, "json.dump"])

            assert result.exit_code == 0

            output = json.loads(result.stdout)
            assert "usage_examples" in output
            assert len(output["usage_examples"]) > 0
            assert "json.dump" in output["usage_examples"][0]["code"]

    def test_examples_from_with_no_matches(self) -> None:
        """Test --examples-from when no matches are found."""
        from pydocq.cli import app

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create empty test file
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("# empty test file\n")

            result = runner.invoke(app, ["--examples-from", tmpdir, "json.dump"])

            assert result.exit_code == 0

            output = json.loads(result.stdout)
            assert "usage_examples" in output
            assert len(output["usage_examples"]) == 0
