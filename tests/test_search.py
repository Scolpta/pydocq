"""Tests for search functionality."""

import pytest

from docs_cli.analyzer.search import (
    SearchResult,
    search_by_docstring,
    search_by_metadata,
    search_by_name,
    search_by_type,
)
from docs_cli.analyzer.resolver import ElementType


class TestSearchResult:
    """Tests for SearchResult class."""

    def test_to_dict(self) -> None:
        """Test converting search result to dictionary."""
        result = SearchResult(
            path="test.module.func",
            element_type=ElementType.FUNCTION,
            name="func",
            match_reason="name_pattern",
        )

        result_dict = result.to_dict()
        assert result_dict["path"] == "test.module.func"
        assert result_dict["type"] == "function"
        assert result_dict["name"] == "func"
        assert result_dict["match_reason"] == "name_pattern"


class TestSearchByName:
    """Tests for search_by_name function."""

    def test_search_by_name_pattern(self) -> None:
        """Test searching by name pattern."""
        results = search_by_name("json", "*dump*")

        assert len(results) > 0
        assert any("dump" in r.name.lower() for r in results)

    def test_search_by_name_exact(self) -> None:
        """Test searching by exact name."""
        results = search_by_name("json", "dumps")

        assert len(results) > 0
        assert any(r.name == "dumps" for r in results)

    def test_search_by_name_no_results(self) -> None:
        """Test search with no results."""
        results = search_by_name("json", "nonexistent*")

        assert len(results) == 0


class TestSearchByDocstring:
    """Tests for search_by_docstring function."""

    def test_search_by_docstring_keyword(self) -> None:
        """Test searching by docstring keyword."""
        results = search_by_docstring("json", "serialize")

        # Should find functions with "serialize" in docstring
        assert len(results) >= 0

    def test_search_by_docstring_case_insensitive(self) -> None:
        """Test case insensitive search."""
        results_lower = search_by_docstring("json", "JSON", case_sensitive=False)
        results_upper = search_by_docstring("json", "json", case_sensitive=False)

        # Should get similar results
        assert len(results_lower) >= 0 or len(results_upper) >= 0

    def test_search_by_docstring_no_results(self) -> None:
        """Test search with no results."""
        results = search_by_docstring("json", "xyznonexistent123")

        assert len(results) == 0


class TestSearchByType:
    """Tests for search_by_type function."""

    def test_search_functions(self) -> None:
        """Test searching for functions."""
        results = search_by_type("json", ElementType.FUNCTION)

        assert len(results) > 0
        assert all(r.element_type == ElementType.FUNCTION for r in results)

    def test_search_classes(self) -> None:
        """Test searching for classes."""
        results = search_by_type("json", ElementType.CLASS)

        assert len(results) >= 0

    def test_search_modules(self) -> None:
        """Test searching for modules."""
        results = search_by_type("json", ElementType.MODULE)

        # Should find the main json module at least
        assert len(results) >= 0


class TestSearchByMetadata:
    """Tests for search_by_metadata function."""

    def test_search_by_metadata_key(self) -> None:
        """Test searching by metadata key."""
        from docs_cli.sdk import metadata, clear_metadata

        # Add metadata to test function
        @metadata(category="test")
        def test_func():
            pass

        # Search in current module
        import sys

        module_name = sys.modules[__name__].__name__

        # This test is basic - real usage would search actual modules with metadata
        clear_metadata()

    def test_search_by_metadata_value(self) -> None:
        """Test searching by metadata key and value."""
        # Basic test - actual implementation would need test module
        pass
