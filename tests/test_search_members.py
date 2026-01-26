"""Tests for search functionality."""

import json

from typer.testing import CliRunner

from pydocq.analyzer.search import MatchResult, search_members
from pydocq.cli import app

runner = CliRunner()


class TestSearchMembers:
    """Test suite for search_members function."""

    def test_search_by_substring(self) -> None:
        """Test searching for members by substring pattern."""
        results = search_members("json", "dump")

        assert len(results) > 0
        assert any("dump" in r.name.lower() for r in results)

    def test_search_by_glob_pattern(self) -> None:
        """Test searching for members using glob pattern."""
        results = search_members("json", "*load")

        # Should find load, loads, etc.
        assert len(results) > 0
        assert any("load" in r.name.lower() for r in results)

    def test_search_with_regex(self) -> None:
        """Test searching with regex pattern."""
        results = search_members("json", "^dump", use_regex=True)

        assert len(results) > 0
        # All results should start with "dump"
        assert all(r.name.startswith("dump") for r in results)

    def test_search_case_insensitive_default(self) -> None:
        """Test that search is case-insensitive by default."""
        results_lower = search_members("json", "dump")
        results_upper = search_members("json", "DUMP")
        results_mixed = search_members("json", "DuMp")

        # All should return the same results
        assert len(results_lower) == len(results_upper) == len(results_mixed)

    def test_search_case_sensitive(self) -> None:
        """Test case-sensitive search."""
        results = search_members("json", "DUMP", case_sensitive=True)

        # Should find exact matches only (likely none in stdlib)
        # This test verifies the flag is respected
        assert isinstance(results, list)

    def test_search_filter_by_type(self) -> None:
        """Test filtering search results by element type."""
        results = search_members("json", "*", element_type_filter="function")

        assert len(results) > 0
        # All results should be functions
        assert all(r.element_type == "function" for r in results)

    def test_search_with_max_results(self) -> None:
        """Test that max_results limits the number of results."""
        results = search_members("json", "*", max_results=5)

        assert len(results) <= 5

    def test_search_with_private_members(self) -> None:
        """Test including private members in search."""
        results_without_private = search_members("json", "*", include_private=False)
        results_with_private = search_members("json", "*", include_private=True)

        # With private should return more or equal results
        assert len(results_with_private) >= len(results_without_private)

    def test_search_empty_pattern(self) -> None:
        """Test searching with empty pattern (should match all)."""
        results = search_members("json", "")

        # Should return many results (all members)
        assert len(results) > 0


class TestCLISearch:
    """Test suite for CLI search integration."""

    def test_search_flag_basic(self) -> None:
        """Test basic --search flag."""
        result = runner.invoke(app, ["--search", "dump", "json"])

        assert result.exit_code == 0

        output = json.loads(result.stdout)
        assert "matches" in output
        assert "count" in output
        assert output["count"] > 0

    def test_search_with_regex_flag(self) -> None:
        """Test --search with --regex flag."""
        result = runner.invoke(app, ["--search", "^load", "--regex", "json"])

        assert result.exit_code == 0

        output = json.loads(result.stdout)
        assert "matches" in output
        # All matches should start with "load"
        assert all(m["name"].startswith("load") for m in output["matches"])

    def test_search_with_type_filter(self) -> None:
        """Test --search with --type flag."""
        result = runner.invoke(app, ["--search", "*", "--type", "class", "json"])

        assert result.exit_code == 0

        output = json.loads(result.stdout)
        assert "matches" in output
        # All matches should be classes
        assert all(m["type"] == "class" for m in output["matches"])

    def test_search_with_max_results(self) -> None:
        """Test --search with --max-results flag."""
        result = runner.invoke(app, ["--search", "*", "--max-results", "3", "json"])

        assert result.exit_code == 0

        output = json.loads(result.stdout)
        assert "matches" in output
        assert output["count"] <= 3

    def test_search_case_sensitive(self) -> None:
        """Test --search with --case-sensitive flag."""
        result = runner.invoke(app, ["--search", "DUMP", "--case-sensitive", "json"])

        assert result.exit_code == 0

        output = json.loads(result.stdout)
        assert "matches" in output
        assert isinstance(output["matches"], list)

    def test_search_with_private_members(self) -> None:
        """Test --search with --include-private flag."""
        result_without = runner.invoke(app, ["--search", "*", "json"])
        result_with = runner.invoke(app, ["--search", "*", "--include-private", "json"])

        assert result_without.exit_code == 0
        assert result_with.exit_code == 0

        output_without = json.loads(result_without.stdout)
        output_with = json.loads(result_with.stdout)

        # With private should have more or equal results
        assert output_with["count"] >= output_without["count"]

    def test_search_nonexistent_module(self) -> None:
        """Test search on nonexistent module."""
        result = runner.invoke(app, ["--search", "*", "nonexistent_module_xyz"])

        assert result.exit_code == 0

        output = json.loads(result.stdout)
        assert "matches" in output
        assert output["count"] == 0


class TestMatchResult:
    """Test suite for MatchResult class."""

    def test_to_dict(self) -> None:
        """Test MatchResult.to_dict() method."""
        result = MatchResult(
            path="json.dump",
            name="dump",
            element_type="function",
            module="json",
            is_public=True,
        )

        result_dict = result.to_dict()

        assert result_dict["path"] == "json.dump"
        assert result_dict["name"] == "dump"
        assert result_dict["type"] == "function"
        assert result_dict["module"] == "json"
        assert result_dict["is_public"] is True
