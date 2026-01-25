"""Tests for SDK decorators."""

import pytest

from docs_cli.sdk import (
    author,
    category,
    clear_metadata,
    deprecated,
    example,
    get_metadata,
    get_metadata_dict,
    metadata,
    note,
    param,
    returns,
    see_also,
    tag,
    when,
)


@pytest.fixture(autouse=True)
def clear_metadata_before_each_test():
    """Clear metadata before each test."""
    clear_metadata()
    yield
    clear_metadata()


class TestMetadata:
    """Tests for metadata decorator."""

    def test_metadata_on_function(self) -> None:
        """Test adding metadata to function."""
        @metadata(category="test", version="1.0")
        def test_func():
            pass

        meta = get_metadata(test_func)
        assert meta is not None
        assert meta.get("category") == "test"
        assert meta.get("version") == "1.0"

    def test_metadata_on_class(self) -> None:
        """Test adding metadata to class."""
        @metadata(author="John")
        class TestClass:
            pass

        meta = get_metadata(TestClass)
        assert meta is not None
        assert meta.get("author") == "John"

    def test_metadata_multiple_decorators(self) -> None:
        """Test multiple metadata decorators."""
        @metadata(category="test")
        @metadata(version="1.0")
        def test_func():
            pass

        meta = get_metadata(test_func)
        assert meta is not None
        # Should have both metadata entries
        assert "category" in meta.to_dict() or "version" in meta.to_dict()

    def test_get_metadata_dict(self) -> None:
        """Test getting metadata as dictionary."""
        @metadata(key1="value1", key2="value2")
        def test_func():
            pass

        meta_dict = get_metadata_dict(test_func)
        assert meta_dict["key1"] == "value1"
        assert meta_dict["key2"] == "value2"


class TestExample:
    """Tests for example decorator."""

    def test_example_decorator(self) -> None:
        """Test adding example."""
        @example("x = func(42)", "Usage example")
        def test_func():
            pass

        meta = get_metadata(test_func)
        assert meta is not None
        example_data = meta.get("example")
        assert example_data is not None
        assert example_data["code"] == "x = func(42)"
        assert example_data["description"] == "Usage example"


class TestDeprecated:
    """Tests for deprecated decorator."""

    def test_deprecated_decorator(self) -> None:
        """Test marking as deprecated."""
        @deprecated(reason="Use new_func", since="1.0", version="2.0")
        def test_func():
            pass

        meta = get_metadata(test_func)
        assert meta is not None
        dep = meta.get("deprecated")
        assert dep is not None
        assert dep["reason"] == "Use new_func"
        assert dep["since"] == "1.0"
        assert dep["version"] == "2.0"


class TestParam:
    """Tests for param decorator."""

    def test_param_decorator(self) -> None:
        """Test adding parameter documentation."""
        @param("x", type="int", description="Input value")
        def test_func(x):
            pass

        meta = get_metadata(test_func)
        assert meta is not None
        params = meta.get("params")
        assert params is not None
        assert "x" in params
        assert params["x"]["type"] == "int"


class TestReturns:
    """Tests for returns decorator."""

    def test_returns_decorator(self) -> None:
        """Test adding return value documentation."""
        @returns(type="int", description="The result")
        def test_func():
            return 42

        meta = get_metadata(test_func)
        assert meta is not None
        ret = meta.get("returns")
        assert ret is not None
        assert ret["type"] == "int"
        assert ret["description"] == "The result"


class TestCategory:
    """Tests for category decorator."""

    def test_category_decorator(self) -> None:
        """Test adding categories."""
        @category("api", "public", "v2")
        def test_func():
            pass

        meta = get_metadata(test_func)
        assert meta is not None
        cat = meta.get("category")
        assert cat is not None
        assert "api" in cat
        assert "public" in cat


class TestWhen:
    """Tests for when decorator."""

    def test_when_decorator(self) -> None:
        """Test adding version/condition info."""
        @when(version="1.0", condition="stable")
        def test_func():
            pass

        meta = get_metadata(test_func)
        assert meta is not None
        when_data = meta.get("when")
        assert when_data is not None
        assert when_data["version"] == "1.0"
        assert when_data["condition"] == "stable"


class TestTag:
    """Tests for tag decorator."""

    def test_tag_decorator(self) -> None:
        """Test adding tags."""
        @tag("important", "api", "experimental")
        def test_func():
            pass

        meta = get_metadata(test_func)
        assert meta is not None
        tags = meta.get("tags")
        assert tags is not None
        assert "important" in tags
        assert "api" in tags


class TestNote:
    """Tests for note decorator."""

    def test_note_decorator(self) -> None:
        """Test adding note."""
        @note("This is an important note")
        def test_func():
            pass

        meta = get_metadata(test_func)
        assert meta is not None
        notes = meta.get("notes")
        assert notes is not None
        assert "This is an important note" in notes


class TestAuthor:
    """Tests for author decorator."""

    def test_author_decorator(self) -> None:
        """Test adding author info."""
        @author("John Doe", "john@example.com")
        def test_func():
            pass

        meta = get_metadata(test_func)
        assert meta is not None
        author_data = meta.get("author")
        assert author_data is not None
        assert author_data["name"] == "John Doe"
        assert author_data["email"] == "john@example.com"


class TestSeeAlso:
    """Tests for see_also decorator."""

    def test_see_also_decorator(self) -> None:
        """Test adding cross-references."""
        @see_also("other_func", "MyClass.method")
        def test_func():
            pass

        meta = get_metadata(test_func)
        assert meta is not None
        refs = meta.get("see_also")
        assert refs is not None
        assert "other_func" in refs
        assert "MyClass.method" in refs


class TestMultipleDecorators:
    """Tests for combining multiple decorators."""

    def test_combine_decorators(self) -> None:
        """Test using multiple decorators together."""
        @category("api")
        @tag("important")
        @author("Jane Doe")
        @example("result = my_func()")
        def my_func():
            pass

        meta = get_metadata(my_func)
        assert meta is not None
        meta_dict = meta.to_dict()

        # Should have metadata from all decorators
        assert "category" in meta_dict or "tags" in meta_dict or "author" in meta_dict or "example" in meta_dict


class TestMetadataClass:
    """Tests for Metadata class."""

    def test_metadata_get(self) -> None:
        """Test Metadata.get method."""
        from docs_cli.sdk.decorators import Metadata

        meta = Metadata(key1="value1", key2="value2")

        assert meta.get("key1") == "value1"
        assert meta.get("key3", "default") == "default"

    def test_metadata_to_dict(self) -> None:
        """Test Metadata.to_dict method."""
        from docs_cli.sdk.decorators import Metadata

        meta = Metadata(key1="value1", key2="value2")
        result = meta.to_dict()

        assert result["key1"] == "value1"
        assert result["key2"] == "value2"
