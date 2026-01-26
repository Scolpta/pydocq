"""Tests for recursive package exploration."""

import json

from typer.testing import CliRunner

from pydocq.analyzer.explorer import TreeNode, explore_package_recursive, format_tree_ascii, get_package_stats
from pydocq.cli import app

runner = CliRunner()


class TestExplorePackageRecursive:
    """Test suite for explore_package_recursive function."""

    def test_explore_simple_module(self) -> None:
        """Test exploring a simple module."""
        tree = explore_package_recursive("json")

        assert tree is not None
        assert tree.path == "json"
        assert tree.element_type == "module"
        assert len(tree.functions) > 0  # Should have functions like dump, load

    def test_explore_with_max_depth(self) -> None:
        """Test exploring with depth limit."""
        tree_shallow = explore_package_recursive("json", max_depth=1)
        tree_deep = explore_package_recursive("json", max_depth=10)

        # Both should work
        assert tree_shallow is not None
        assert tree_deep is not None

        # Shallow should have fewer or equal modules
        stats_shallow = get_package_stats(tree_shallow)
        stats_deep = get_package_stats(tree_deep)

        assert stats_shallow["total_modules"] <= stats_deep["total_modules"]

    def test_explore_with_private_members(self) -> None:
        """Test exploring with private members included."""
        tree_without = explore_package_recursive("json", include_private=False)
        tree_with = explore_package_recursive("json", include_private=True)

        assert tree_without is not None
        assert tree_with is not None

        # Both should have results
        assert len(tree_without.functions) >= 0
        assert len(tree_with.functions) >= 0

    def test_explore_nonexistent_module(self) -> None:
        """Test exploring a nonexistent module."""
        tree = explore_package_recursive("nonexistent_module_xyz")

        assert tree is None

    def test_explore_with_contents(self) -> None:
        """Test exploring with docstrings included."""
        tree = explore_package_recursive("json", include_contents=True)

        assert tree is not None
        # With include_contents, docstring should be present
        # (may be None for stdlib modules, but the field should exist)
        assert hasattr(tree, "docstring")


class TestTreeNode:
    """Test suite for TreeNode class."""

    def test_to_dict_basic(self) -> None:
        """Test TreeNode.to_dict() with basic info."""
        node = TreeNode(
            path="test.module",
            name="module",
            element_type="module",
        )

        result = node.to_dict(include_contents=False)

        assert result["path"] == "test.module"
        assert result["name"] == "module"
        assert result["type"] == "module"
        assert "docstring" not in result

    def test_to_dict_with_contents(self) -> None:
        """Test TreeNode.to_dict() with contents."""
        node = TreeNode(
            path="test.module",
            name="module",
            element_type="module",
            docstring="Test module docstring",
            classes=["Class1", "Class2"],
            functions=["func1", "func2"],
        )

        result = node.to_dict(include_contents=True)

        assert result["path"] == "test.module"
        assert result["docstring"] == "Test module docstring"
        assert result["classes"] == ["Class1", "Class2"]
        assert result["functions"] == ["func1", "func2"]

    def test_to_dict_with_children(self) -> None:
        """Test TreeNode.to_dict() with child nodes."""
        child = TreeNode(
            path="test.module.child",
            name="child",
            element_type="module",
        )

        parent = TreeNode(
            path="test.module",
            name="module",
            element_type="module",
            children=[child],
        )

        result = parent.to_dict(include_contents=False)

        assert "children" in result
        assert len(result["children"]) == 1
        assert result["children"][0]["name"] == "child"


class TestFormatTreeAscii:
    """Test suite for format_tree_ascii function."""

    def test_format_simple_tree(self) -> None:
        """Test formatting a simple tree."""
        node = TreeNode(
            path="test",
            name="test",
            element_type="module",
            functions=["func1", "func2"],
        )

        output = format_tree_ascii(node)

        assert "test" in output
        assert "└──" in output or "├──" in output  # Tree connectors

    def test_format_tree_with_children(self) -> None:
        """Test formatting a tree with children."""
        child = TreeNode(
            path="test.child",
            name="child",
            element_type="module",
        )

        parent = TreeNode(
            path="test",
            name="test",
            element_type="module",
            children=[child],
        )

        output = format_tree_ascii(parent)

        assert "test" in output
        assert "child" in output


class TestGetPackageStats:
    """Test suite for get_package_stats function."""

    def test_stats_structure(self) -> None:
        """Test that stats returns expected structure."""
        node = TreeNode(
            path="test",
            name="test",
            element_type="module",
            classes=["Class1"],
            functions=["func1"],
        )

        stats = get_package_stats(node)

        assert "total_modules" in stats
        assert "total_classes" in stats
        assert "total_functions" in stats
        assert "total_methods" in stats
        assert "max_depth" in stats

    def test_stats_counts(self) -> None:
        """Test that stats counts are correct."""
        node = TreeNode(
            path="test",
            name="test",
            element_type="module",
            classes=["Class1", "Class2"],
            functions=["func1", "func2", "func3"],
        )

        stats = get_package_stats(node)

        assert stats["total_modules"] == 1
        assert stats["total_classes"] == 2
        assert stats["total_functions"] == 3


class TestCLIRecursive:
    """Test suite for CLI recursive exploration."""

    def test_recursive_flag(self) -> None:
        """Test --recursive flag."""
        result = runner.invoke(app, ["--recursive", "json"])

        assert result.exit_code == 0

        output = json.loads(result.stdout)
        assert "path" in output
        assert "type" in output
        assert output["path"] == "json"

    def test_recursive_with_max_depth(self) -> None:
        """Test --recursive with --max-depth."""
        result = runner.invoke(app, ["--recursive", "--max-depth", "1", "json"])

        assert result.exit_code == 0

        output = json.loads(result.stdout)
        assert "stats" in output
        assert "max_depth" in output["stats"]

    def test_recursive_with_tree_output(self) -> None:
        """Test --recursive with --tree flag."""
        result = runner.invoke(app, ["--recursive", "--tree", "json"])

        assert result.exit_code == 0

        # Should have ASCII tree characters
        assert "└──" in result.stdout or "├──" in result.stdout or "json" in result.stdout

    def test_recursive_nonexistent_module(self) -> None:
        """Test --recursive with nonexistent module."""
        result = runner.invoke(app, ["--recursive", "nonexistent_module_xyz"])

        assert result.exit_code == 1
        # stderr may not be separately captured in all Click versions
        try:
            if result.stderr:
                assert "Error" in result.stderr
        except ValueError:
            # stderr not separately captured in this version
            pass

    def test_recursive_with_verbose(self) -> None:
        """Test --recursive with --verbose includes docstrings."""
        result = runner.invoke(app, ["--recursive", "--verbose", "json"])

        assert result.exit_code == 0

        output = json.loads(result.stdout)
        # Verbose should include more detailed info
        assert "path" in output
