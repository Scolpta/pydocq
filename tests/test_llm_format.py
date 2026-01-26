"""Tests for LLM-optimized output format."""

import json

from pydocq.analyzer.output_formats import (
    _summarize_docstring,
    _extract_key_params,
    _estimate_tokens,
    _generate_example,
    format_llm,
    get_formatter,
)
from pydocq.analyzer.inspector import (
    InspectedElement,
    SignatureInfo,
    DocstringInfo,
    SourceLocation,
)
from pydocq.utils.type_detection import ElementType


def test_summarize_docstring_short() -> None:
    """Test summarizing a short docstring."""
    docstring = "This is a short docstring."
    result = _summarize_docstring(docstring)
    assert result == "This is a short docstring."


def test_summarize_docstring_long() -> None:
    """Test summarizing a long docstring."""
    docstring = (
        "This is a very long docstring that has multiple sentences. "
        "It should be truncated to the first sentence only. "
        "This part should not appear in the summary."
    )
    result = _summarize_docstring(docstring)
    # The period is removed by the split
    assert result == "This is a very long docstring that has multiple sentences"


def test_summarize_docstring_truncation() -> None:
    """Test summarizing a docstring that needs truncation."""
    docstring = "This is a very long first sentence that goes on and on and on and on and on and on and on and on until it exceeds the maximum length."
    result = _summarize_docstring(docstring, max_length=50)
    assert len(result) <= 53  # max_length + '...'
    assert result.endswith("...")


def test_summarize_docstring_none() -> None:
    """Test summarizing a None docstring."""
    result = _summarize_docstring(None)
    assert result == "No documentation available."


def test_extract_key_params_required() -> None:
    """Test extracting key parameters with required ones."""
    params = [
        {"name": "a", "default": None},
        {"name": "b", "default": "2"},
        {"name": "c", "default": None},
        {"name": "d", "default": "4"},
    ]
    result = _extract_key_params(params, max_params=3)
    assert len(result) == 3
    # Should prioritize required params
    assert result[0]["name"] == "a"
    assert result[1]["name"] == "c"
    assert result[2]["name"] in ("b", "d")


def test_extract_key_params_empty() -> None:
    """Test extracting key parameters from empty list."""
    result = _extract_key_params([])
    assert result == []


def test_extract_key_params_all_optional() -> None:
    """Test extracting key parameters when all are optional."""
    params = [
        {"name": "a", "default": "1"},
        {"name": "b", "default": "2"},
        {"name": "c", "default": "3"},
    ]
    result = _extract_key_params(params, max_params=2)
    assert len(result) == 2
    assert result[0]["name"] == "a"
    assert result[1]["name"] == "b"


def test_estimate_tokens() -> None:
    """Test token estimation."""
    text = "This is a simple test."
    result = _estimate_tokens(text)
    assert result > 0
    assert result == len(text) // 4


def test_estimate_tokens_empty() -> None:
    """Test token estimation for empty string."""
    result = _estimate_tokens("")
    assert result == 0


def test_estimate_tokens_long() -> None:
    """Test token estimation for long text."""
    text = "word " * 100
    result = _estimate_tokens(text)
    assert result > 0
    assert result == len(text) // 4


def test_generate_example_with_params() -> None:
    """Test generating an example with parameters."""
    signature = SignatureInfo(
        parameters=[
            {"name": "obj", "default": None, "annotation": "Any", "kind": "POSITIONAL"},
            {"name": "fp", "default": None, "annotation": "SupportsWrite[str]", "kind": "POSITIONAL"},
        ],
        return_type="None",
    )
    inspected = InspectedElement(
        path="json.dump",
        element_type=ElementType.FUNCTION,
        obj=None,
        signature=signature,
    )
    result = _generate_example(inspected)
    assert result == 'json.dump(data, open("file.txt", "w"))'


def test_generate_example_no_params() -> None:
    """Test generating an example without parameters."""
    signature = SignatureInfo(parameters=[], return_type=None)
    inspected = InspectedElement(
        path="json.loads",
        element_type=ElementType.FUNCTION,
        obj=None,
        signature=signature,
    )
    result = _generate_example(inspected)
    assert result == "json.loads(...)"


def test_format_llm_basic() -> None:
    """Test basic LLM format output."""
    signature = SignatureInfo(
        parameters=[
            {"name": "obj", "default": None, "annotation": "Any", "kind": "POSITIONAL"},
            {"name": "fp", "default": None, "annotation": "SupportsWrite[str]", "kind": "POSITIONAL"},
        ],
        return_type="None",
    )
    docstring = DocstringInfo(
        docstring="Serialize obj as a JSON stream to fp.",
        length=40,
        has_examples=False,
    )
    inspected = InspectedElement(
        path="json.dump",
        element_type=ElementType.FUNCTION,
        obj=None,
        signature=signature,
        docstring=docstring,
        module_path="json",
    )
    result = format_llm(inspected)
    data = json.loads(result)

    assert data["path"] == "json.dump"
    assert data["type"] == "function"
    assert "summary" in data
    assert "key_params" in data
    assert len(data["key_params"]) == 2
    assert "token_count" in data
    assert data["token_count"] > 0


def test_format_llm_with_examples() -> None:
    """Test LLM format with has_examples flag."""
    signature = SignatureInfo(
        parameters=[{"name": "s", "default": None, "annotation": "str", "kind": "POSITIONAL"}],
        return_type="Any",
    )
    docstring = DocstringInfo(
        docstring="Load JSON from string.",
        length=20,
        has_examples=True,
    )
    inspected = InspectedElement(
        path="json.loads",
        element_type=ElementType.FUNCTION,
        obj=None,
        signature=signature,
        docstring=docstring,
    )
    result = format_llm(inspected)
    data = json.loads(result)

    assert data.get("has_examples") is True


def test_format_llm_no_docstring() -> None:
    """Test LLM format with no docstring."""
    signature = SignatureInfo(
        parameters=[{"name": "x", "default": None, "annotation": "int", "kind": "POSITIONAL"}],
        return_type="int",
    )
    inspected = InspectedElement(
        path="test.func",
        element_type=ElementType.FUNCTION,
        obj=None,
        signature=signature,
        docstring=None,
    )
    result = format_llm(inspected)
    data = json.loads(result)

    assert data["summary"] == "No documentation available."


def test_get_formatter_llm() -> None:
    """Test getting the LLM formatter."""
    formatter = get_formatter("llm")
    assert formatter == format_llm


def test_llm_format_integration() -> None:
    """Test LLM format with actual Python function."""
    import json as json_module

    # Get actual function info
    from pydocq.analyzer.inspector import inspect_element
    from pydocq.analyzer.resolver import resolve_path

    resolved = resolve_path("json.dump")
    inspected = inspect_element(resolved)

    result = format_llm(inspected)
    data = json.loads(result)

    assert data["path"] == "json.dump"
    assert data["type"] == "function"
    assert "summary" in data
    assert "key_params" in data
    assert "token_count" in data
    # Verify token reduction - should be much smaller than full JSON
    assert data["token_count"] < 150  # Reasonable token count for LLM format
