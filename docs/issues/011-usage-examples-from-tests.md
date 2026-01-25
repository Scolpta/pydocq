# Issue FEAT-004: Usage Examples from Test Files

## Description

Automatically extract real usage examples from test files and documentation. This provides AI agents with actual usage patterns rather than just theoretical docstrings.

## Problem Details

### Current Limitations

**Docstrings can be outdated or incomplete:**

```python
# In source code
def my_function(data: list) -> dict:
    """Process data.

    Args:
        data: Input data

    Returns:
        Processed data
    """
    # Docstring doesn't show real usage!
    return process(data)
```

**Test files show real usage:**

```python
# In tests/test_my_module.py
def test_my_function_with_empty_list():
    """Test processing empty list."""
    result = my_function([])
    assert result == {"empty": True}

def test_my_function_with_nested_data():
    """Test processing nested structures."""
    result = my_function([{"key": "value"}])
    assert result["count"] == 1
```

### Limitations of Current Approach

| Limitation | Impact | Severity |
|------------|--------|----------|
| **Docstrings Lie** | Examples may not match actual API | High |
| **Edge Cases** | Docs show happy path, tests show edge cases | Medium |
| **Discoverability** | Agents can't see real-world usage | High |
| **Maintenance** | Doc examples require manual updates | Medium |
| **Completeness** | Not all functions have docstring examples | Medium |

### Use Cases

1. **AI agents learning real usage patterns**
   ```bash
   $ pydocq pandas.DataFrame.merge --examples-from tests/
   ```

2. **Generating accurate code examples**
   ```bash
   $ pydocq json.dump --examples
   # Shows: json.dump(data, open('file.json', 'w'))
   # From: tests/test_json.py:42
   ```

3. **Understanding edge cases**
   ```bash
   $ pydocq parse_date --examples
   # Shows tests for:
   # - ISO format dates
   # - Empty strings
   # - Invalid formats
   ```

## Impact Assessment

| Impact Type | Severity | Description |
|-------------|----------|-------------|
| Accuracy | 🟢 High | Real examples vs theoretical |
| Completeness | 🟡 Medium | Functions without docs get examples |
| Agent Capability | 🟢 High | Agents see real usage patterns |
| Maintenance | 🟢 Low | Auto-updated with tests |
| Performance | 🟡 Medium | Requires test file scanning |

## Recommended Implementation

### Phase 1: Grep-Based Extraction (Quick Win)

```python
# pydocq/analyzer/example_extractor.py

import re
from pathlib import Path
from typing import List
from dataclasses import dataclass

@dataclass
class UsageExample:
    """Extracted usage example."""
    code: str
    source_file: str
    line_number: int
    context: str


def extract_examples_from_tests(
    function_name: str,
    test_dirs: List[str] = None
) -> List[UsageExample]:
    """Extract usage examples from test files using grep-like approach.

    Args:
        function_name: Name of function to find examples for
        test_dirs: List of test directory paths

    Returns:
        List of usage examples
    """
    if test_dirs is None:
        test_dirs = ["tests/", "test/", "tests/"]

    examples = []

    # Search pattern: function_name(
    # Match: function_name(...), capturing context
    pattern = rf'([^\n]*{re.escape(function_name)}\s*\([^)]*\)[^\n]*)'

    for test_dir in test_dirs:
        test_path = Path(test_dir)
        if not test_path.exists():
            continue

        # Find all Python files
        for py_file in test_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                lines = content.split('\n')

                # Search for pattern
                for i, line in enumerate(lines):
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        code_snippet = match.group(1).strip()

                        # Filter out non-call lines
                        if not _is_valid_call(code_snippet, function_name):
                            continue

                        # Get context (previous line + current line)
                        context = _get_context(lines, i)

                        examples.append(UsageExample(
                            code=code_snippet,
                            source_file=str(py_file),
                            line_number=i + 1,
                            context=context
                        ))

                        # Limit examples per function
                        if len(examples) >= 10:
                            return examples

            except Exception:
                # Skip files that can't be read
                continue

    return examples


def _is_valid_call(code: str, function_name: str) -> bool:
    """Check if code is a valid function call.

    Args:
        code: Code snippet to check
        function_name: Function name to match

    Returns:
        True if valid call
    """
    # Must have opening parenthesis
    if '(' not in code:
        return False

    # Skip definitions
    if code.strip().startswith('def '):
        return False

    # Skip imports
    if 'import ' in code or 'from ' in code:
        return False

    # Skip comments
    if code.strip().startswith('#'):
        return False

    return True


def _get_context(lines: List[str], line_idx: int) -> str:
    """Get context around a line.

    Args:
        lines: All lines in file
        line_idx: Index of current line

    Returns:
        Context string (previous 2 lines + current line)
    """
    start = max(0, line_idx - 2)
    end = min(len(lines), line_idx + 2)
    context_lines = lines[start:end]

    # Add line numbers
    context = '\n'.join(
        f"{i + start + 1}: {line}"
        for i, line in enumerate(context_lines)
    )

    return context
```

### Add CLI Option

```python
# pydocq/cli.py

@app.command()
def query(
    target: str,
    examples_from: str = Option(
        None,
        "--examples-from",
        help="Extract usage examples from test directory"
    ),
    # ... existing options
) -> None:
    """Query Python package documentation."""
    # ... existing inspection code

    output_dict = format_json(inspected, ...)

    # Add examples if requested
    if examples_from:
        from pydocq.analyzer.example_extractor import extract_examples_from_tests

        # Get function name from path
        func_name = target.split('.')[-1]

        # Extract examples
        examples = extract_examples_from_tests(func_name, [examples_from])

        # Format for output
        output_dict["usage_examples"] = [
            {
                "code": ex.code,
                "source": f"{ex.source_file}:{ex.line_number}",
                "context": ex.context
            }
            for ex in examples
        ]

    sys.stdout.write(json.dumps(output_dict, indent=2))
```

**Usage:**
```bash
# Extract from tests/ directory
pydocq my_function --examples-from tests/

# Extract from custom location
pydocq pandas.DataFrame.merge --examples-from ./pandas/tests/

# Combine with --for-ai
pydocq json.dump --for-ai --examples-from tests/
```

### Phase 2: AST-Based Extraction (Advanced)

```python
# pydocq/analyzer/example_extractor.py

import ast
from typing import List, Set

def extract_examples_ast(
    function_name: str,
    test_dirs: List[str] = None
) -> List[UsageExample]:
    """Extract examples using AST parsing for better accuracy.

    This Phase 2 implementation:
    - Parses test files with AST
    - Identifies actual function calls
    - Extracts argument values
    - Captures assertion context

    Args:
        function_name: Function to find
        test_dirs: Test directories

    Returns:
        List of usage examples with full context
    """
    if test_dirs is None:
        test_dirs = ["tests/"]

    examples = []
    visited: Set[str] = set()

    for test_dir in test_dirs:
        test_path = Path(test_dir)
        if not test_path.exists():
            continue

        for py_file in test_path.rglob("*.py"):
            if str(py_file) in visited:
                continue
            visited.add(str(py_file))

            try:
                examples.extend(
                    _extract_from_file_ast(py_file, function_name)
                )

                if len(examples) >= 10:
                    return examples

            except Exception:
                continue

    return examples


def _extract_from_file_ast(
    file_path: Path,
    function_name: str
) -> List[UsageExample]:
    """Extract examples from a single file using AST.

    Args:
        file_path: Path to test file
        function_name: Function name to find

    Returns:
        List of examples
    """
    examples = []

    try:
        source = file_path.read_text()
        tree = ast.parse(source)
        lines = source.split('\n')

        for node in ast.walk(tree):
            # Look for function calls
            if isinstance(node, ast.Call):
                # Check if this is our target function
                if _is_call_to_function(node, function_name):
                    # Extract the call
                    call_code = ast.unparse(node)

                    # Get context
                    line_num = node.lineno - 1
                    context = _get_context(lines, line_num)

                    examples.append(UsageExample(
                        code=call_code,
                        source_file=str(file_path),
                        line_number=node.lineno,
                        context=context
                    ))

    except Exception:
        pass

    return examples


def _is_call_to_function(node: ast.Call, function_name: str) -> bool:
    """Check if AST node is a call to target function.

    Args:
        node: AST Call node
        function_name: Function name to match

    Returns:
        True if this is a call to our target
    """
    # Get function name from call
    func = node.func

    # Direct call: function_name(...)
    if isinstance(func, ast.Name):
        return func.id == function_name

    # Attribute call: obj.function_name(...)
    if isinstance(func, ast.Attribute):
        return func.attr == function_name

    # Method call: obj.method().function_name(...)
    if isinstance(func, ast.Call):
        return _is_call_to_function(func, function_name)

    return False
```

## Output Examples

### Example 1: Simple Function

**Input:**
```bash
$ pydocq json.dump --examples-from tests/
```

**Output:**
```json
{
  "path": "json.dump",
  "type": "function",
  "signature": {...},
  "usage_examples": [
    {
      "code": "json.dump({'a': 1}, fp)",
      "source": "tests/test_json.py:42",
      "context": "41: def test_dump_simple_dict():\n42:     json.dump({'a': 1}, fp)\n43:     assert ..."
    },
    {
      "code": "json.dump(data, open('out.json', 'w'), indent=2)",
      "source": "tests/test_json.py:85",
      "context": "84: def test_dump_with_indent():\n85:     json.dump(data, open('out.json', 'w'), indent=2)\n86:     ..."
    },
    {
      "code": "json.dump([], fp)",
      "source": "tests/test_json.py:120",
      "context": "119: def test_dump_empty_list():\n120:     json.dump([], fp)\n121:     ..."
    }
  ]
}
```

### Example 2: Method

**Input:**
```bash
$ pydocq pandas.DataFrame.merge --examples-from tests/
```

**Output:**
```json
{
  "path": "pandas.DataFrame.merge",
  "type": "method",
  "usage_examples": [
    {
      "code": "df1.merge(df2, on='key')",
      "source": "tests/frame/test_merge.py:45",
      "context": "44: def test_merge_on_column():\n45:     result = df1.merge(df2, on='key')\n46:     assert ..."
    },
    {
      "code": "df.merge(other, left_on='lkey', right_on='rkey')",
      "source": "tests/frame/test_merge.py:89",
      "context": "..."
    },
    {
      "code": "df1.merge(df2, how='outer')",
      "source": "tests/frame/test_merge.py:134",
      "context": "..."
    }
  ]
}
```

### Example 3: With --for-ai

**Input:**
```bash
$ pydocq json.dump --for-ai --examples-from tests/
```

**Output:**
```json
{
  "path": "json.dump",
  "summary": "Serialize Python object to JSON file",
  "key_params": [...],
  "common_usage": "Save data to JSON file",
  "example_concise": "json.dump(data, open('file.json', 'w'))",
  "real_world_examples": [
    {
      "usage": "simple_dict",
      "code": "json.dump({'a': 1}, fp)",
      "source": "tests/test_json.py:42"
    },
    {
      "usage": "with_indent",
      "code": "json.dump(data, open('out.json', 'w'), indent=2)",
      "source": "tests/test_json.py:85"
    }
  ],
  "token_count": 75
}
```

## Testing

### Unit Tests

```python
# tests/test_example_extraction.py
import pytest
import tempfile
from pathlib import Path
from pydocq.analyzer.example_extractor import extract_examples_from_tests

class TestExampleExtraction:
    """Test suite for usage example extraction."""

    def test_extract_simple_call(self):
        """Test extracting simple function call."""
        # Create test file
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("""
def test_my_func():
    result = my_function(arg1, arg2)
    assert result == expected
""")

            examples = extract_examples_from_tests("my_function", [tmpdir])

            assert len(examples) == 1
            assert "my_function" in examples[0].code
            assert "arg1" in examples[0].code

    def test_extract_multiple_calls(self):
        """Test extracting multiple calls."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("""
def test_1():
    my_function(a)

def test_2():
    my_function(b, c)

def test_3():
    my_function(d, e, f)
""")

            examples = extract_examples_from_tests("my_function", [tmpdir])

            assert len(examples) == 3

    def test_filters_non_calls(self):
        """Test that non-call lines are filtered out."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("""
def my_function():  # Not a call
    pass

# my_function() in comment

result = my_function()  # Actual call
""")

            examples = extract_examples_from_tests("my_function", [tmpdir])

            # Should only find the actual call
            assert len(examples) == 1
            assert "result = my_function()" in examples[0].code

    def test_includes_context(self):
        """Test that context is included."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("""
def test_something():
    # Setup
    data = prepare_data()

    # Call function
    result = my_function(data)

    # Assert
    assert result is not None
""")

            examples = extract_examples_from_tests("my_function", [tmpdir])

            assert len(examples) == 1
            # Context should include surrounding lines
            assert len(examples[0].context.split('\n')) >= 3
```

## Implementation Priority

1. **Phase 1 (P1):** Implement grep-based extraction
2. **Phase 1 (P1):** Add `--examples-from` CLI flag
3. **Phase 2 (P2):** Implement AST-based extraction
4. **Testing (P1):** Add comprehensive tests
5. **Documentation (P1):** Update README

## Migration Plan

### Phase 1: Grep-Based (Week 1-2)
- [ ] Implement `extract_examples_from_tests()`
- [ ] Add `--examples-from` CLI flag
- [ ] Implement filtering logic
- [ ] Add context extraction

### Phase 2: Testing (Week 2)
- [ ] Add unit tests for extraction
- [ ] Test on real projects
- [ ] Benchmark performance
- [ ] Validate accuracy

### Phase 3: AST-Based (Week 3-4)
- [ ] Implement AST-based extraction
- [ ] Add argument value extraction
- [ ] Add assertion context
- [ ] Compare accuracy vs grep-based

### Phase 4: Integration (Week 4)
- [ ] Integrate with `--for-ai` flag
- [ ] Add to output formats
- [ ] Update documentation
- [ ] Create examples

## Benefits

| Benefit | Impact |
|---------|--------|
| **Real Examples** | Actual usage vs theoretical |
| **Edge Cases** | Shows how code handles errors |
| **Auto-Updated** | Tests are always current |
| **Accuracy** | Tests don't lie |
| **Completeness** | Even undocumented functions have examples |

## Related Issues

- [FEAT-002: LLM-Optimized Output Format](./009-llm-output-format.md)
- [FEAT-003: Combined --for-ai Flag](./010-combined-ai-flag.md)

## References

- [AST Module Documentation](https://docs.python.org/3/library/ast.html)
- [Python `re` Module](https://docs.python.org/3/library/re.html)

## Checklist

- [ ] Implement `extract_examples_from_tests()` function
- [ ] Implement `_is_valid_call()` helper
- [ ] Implement `_get_context()` helper
- [ ] Add `--examples-from` CLI flag
- [ ] Implement AST-based extraction
- [ ] Implement `_is_call_to_function()` AST helper
- [ ] Add unit tests for grep extraction
- [ ] Add unit tests for AST extraction
- [ ] Test on real projects
- [ ] Benchmark performance
- [ ] Integrate with --for-ai flag
- [ ] Update README with examples
- [ ] Create tutorial documentation
