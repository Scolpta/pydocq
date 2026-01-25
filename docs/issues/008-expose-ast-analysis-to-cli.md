# Issue FEAT-001: Expose AST File Analysis to CLI

## Description

The `ast_analyzer.py` module provides static file analysis without importing code, but this functionality is not exposed through the CLI interface. Users cannot analyze Python files without installing or importing their dependencies.

## Problem Details

### Current State

**Implementation exists but is CLI-inaccessible:**

```python
# pydocq/analyzer/ast_analyzer.py:315
def analyze_file(file_path: str) -> ASTModuleInfo:
    """Analyze a Python file using AST.

    Args:
        file_path: Path to Python file

    Returns:
        ASTModuleInfo with complete analysis

    Raises:
        ASTSecurityError: If file path is dangerous
        FileNotFoundError: If file doesn't exist
        SyntaxError: If file has invalid syntax
    """
    tree = parse_file(file_path)
    return analyze_module(tree, file_path)
```

### Limitations

| Limitation | Impact | Severity |
|------------|--------|----------|
| **CLI-only access** | Can't use from command line | High |
| **No file element targeting** | Can't analyze specific class/function | Medium |
| **Missing integration** | Separate workflow from main query | Medium |
| **Undocumented feature** | Users don't know it exists | Low |

### Use Cases Blocked

1. **Analyze code with missing dependencies**
   ```bash
   # This FAILS - requires package to be installed
   $ pydocq some_package.MyClass

   # This SHOULD WORK - analyzes source without importing
   $ pydocq --analyze-file ./src/some_package.py MyClass
   ```

2. **Security analysis of untrusted code**
   ```bash
   # Want to inspect suspicious code without executing it
   $ pydocq --analyze-file ./untrusted.py
   ```

3. **CI/CD integration**
   ```bash
   # Generate documentation without installing all dependencies
   $ pydocq --analyze-file src/ --format markdown > API.md
   ```

4. **Quick exploration of repositories**
   ```bash
   # Understand structure without setup
   $ pydocq --analyze-file ./utils.py
   ```

## Impact Assessment

| Impact Type | Severity | Description |
|-------------|----------|-------------|
| Feature Parity | 🟡 Medium | Core functionality exists but inaccessible |
| Security | 🟢 Low | AST analyzer is already secure |
| User Experience | 🟡 Medium | Users confused by missing feature |
| Adoption | 🟡 Medium | Limits tool to installed packages only |

## Recommended Implementation

### Option 1: Add to Existing Command (Recommended)

Add `--analyze-file` flag to existing query command:

```python
# pydocq/cli.py

@app.command()
def query(
    target: str = Option(None, "--target", "-t", help="Target element (package, class, function)"),
    analyze_file: str = Option(None, "--analyze-file", help="Analyze Python file without importing"),
    element: str = Option(None, "--element", "-e", help="Specific element to extract from file"),
    format: str = Option("json", "--format", "-f", help="Output format"),
    # ... existing options
) -> None:
    """Query Python package documentation."""
    if analyze_file:
        # Use AST analysis
        return _handle_ast_analysis(analyze_file, element, format)

    if target:
        # Use existing runtime analysis
        # ... existing code
```

**Usage:**
```bash
# Analyze entire file
pydocq --analyze-file ./src/utils.py

# Analyze specific class
pydocq --analyze-file ./src/utils.py --element MyClass

# Analyze specific function
pydocq --analyze-file ./src/utils.py --element my_function
```

### Option 2: Separate Command

Add dedicated `analyze` command:

```python
# pydocq/cli.py

@app.command()
def analyze(
    file_path: str = Argument(..., help="Path to Python file to analyze"),
    element: str = Option(None, "--element", "-e", help="Specific element to extract"),
    format: str = Option("json", "--format", "-f", help="Output format"),
) -> None:
    """Analyze Python source file without importing it.

    FILE_PATH is the path to the .py file to analyze.

    Examples:
        pydocq analyze src/utils.py
        pydocq analyze src/utils.py --element MyClass
        pydocq analyze src/utils.py --element my_function --format markdown
    """
    from pydocq.analyzer.ast_analyzer import analyze_file, ASTSecurityError

    try:
        # Analyze the file
        result = analyze_file(file_path)

        # If specific element requested, extract it
        if element:
            extracted = _extract_element(result, element)
            if not extracted:
                sys.stderr.write(f"Element '{element}' not found in file\n")
                raise Exit(code=1)
            output_dict = _format_ast_element(extracted)
        else:
            output_dict = _format_ast_module(result)

        # Output in requested format
        if format == "json":
            sys.stdout.write(json.dumps(output_dict, indent=2))
        else:
            formatter = get_formatter(format)
            output = formatter(output_dict)
            sys.stdout.write(output)

    except ASTSecurityError as e:
        sys.stderr.write(f"Security error: {e}\n")
        raise Exit(code=1)
    except FileNotFoundError:
        sys.stderr.write(f"File not found: {file_path}\n")
        raise Exit(code=1)
    except SyntaxError as e:
        sys.stderr.write(f"Syntax error in {file_path}: {e}\n")
        raise Exit(code=1)


def _extract_element(module_info: ASTModuleInfo, element_name: str) -> ASTFunctionInfo | ASTClassInfo | None:
    """Extract a specific element from module analysis.

    Args:
        module_info: Module analysis result
        element_name: Name of element to extract

    Returns:
        Element info if found, None otherwise
    """
    # Search in functions
    for func in module_info.functions:
        if func.name == element_name:
            return func

    # Search in classes
    for cls in module_info.classes:
        if cls.name == element_name:
            return cls

        # Search in class methods
        for method in cls.methods:
            if method.name == element_name:
                return method

    return None


def _format_ast_module(module_info: ASTModuleInfo) -> dict:
    """Format AST module info for JSON output."""
    return {
        "path": module_info.path,
        "type": "module",
        "docstring": module_info.docstring,
        "functions": [
            {
                "name": f.name,
                "lineno": f.lineno,
                "args": f.args,
                "returns": f.returns,
                "docstring": f.docstring,
            }
            for f in module_info.functions
        ],
        "classes": [
            {
                "name": c.name,
                "lineno": c.lineno,
                "bases": c.bases,
                "docstring": c.docstring,
                "methods": [
                    {
                        "name": m.name,
                        "lineno": m.lineno,
                        "args": m.args,
                        "returns": m.returns,
                    }
                    for m in c.methods
                ],
            }
            for c in module_info.classes
        ],
        "imports": [
            {
                "module": i.module,
                "names": i.names,
                "is_from": i.is_from,
                "lineno": i.lineno,
            }
            for i in module_info.imports
        ],
    }


def _format_ast_element(element: ASTFunctionInfo | ASTClassInfo) -> dict:
    """Format AST element info for JSON output."""
    if isinstance(element, ASTFunctionInfo):
        return {
            "name": element.name,
            "type": "function",
            "lineno": element.lineno,
            "args": element.args,
            "returns": element.returns,
            "is_async": element.is_async,
            "docstring": element.docstring,
            "decorators": element.decorator_list,
        }
    else:  # ASTClassInfo
        return {
            "name": element.name,
            "type": "class",
            "lineno": element.lineno,
            "bases": element.bases,
            "docstring": element.docstring,
            "decorators": element.decorators,
            "methods": [
                {
                    "name": m.name,
                    "lineno": m.lineno,
                    "args": m.args,
                    "returns": m.returns,
                }
                for m in element.methods
            ],
        }
```

**Usage:**
```bash
# Analyze entire file
pydocq analyze src/utils.py

# Analyze specific class
pydocq analyze src/utils.py --element MyClass

# Analyze specific function
pydocq analyze src/utils.py --element my_function --format markdown
```

### Option 3: Hybrid Approach (Most Flexible)

Support both interfaces:

```bash
# Option 1: Flag-based (backward compatible)
pydocq --analyze-file ./src/utils.py

# Option 2: Command-based (more discoverable)
pydocq analyze ./src/utils.py
```

## Output Format Examples

### Entire File Analysis

```bash
$ pydocq analyze src/utils.py
```

**Output:**
```json
{
  "path": "src/utils.py",
  "type": "module",
  "docstring": "Utility functions for data processing.",
  "functions": [
    {
      "name": "parse_json",
      "lineno": 12,
      "args": ["data", "strict"],
      "returns": "dict",
      "is_async": false,
      "docstring": "Parse JSON data with optional strict validation."
    }
  ],
  "classes": [
    {
      "name": "DataProcessor",
      "lineno": 45,
      "bases": [],
      "docstring": "Process and transform data.",
      "methods": [
        {
          "name": "process",
          "lineno": 52,
          "args": ["self", "data"],
          "returns": "ProcessedData"
        }
      ]
    }
  ],
  "imports": [
    {
      "module": "json",
      "names": ["load", "dump"],
      "is_from": true,
      "lineno": 3
    }
  ]
}
```

### Specific Element Analysis

```bash
$ pydocq analyze src/utils.py --element DataProcessor
```

**Output:**
```json
{
  "name": "DataProcessor",
  "type": "class",
  "lineno": 45,
  "bases": [],
  "docstring": "Process and transform data.",
  "decorators": [],
  "methods": [
    {
      "name": "__init__",
      "lineno": 48,
      "args": ["self", "config"],
      "returns": null
    },
    {
      "name": "process",
      "lineno": 52,
      "args": ["self", "data"],
      "returns": "ProcessedData"
    }
  ]
}
```

## Testing

### Unit Tests

```python
# tests/test_ast_cli.py
import pytest
import tempfile
from pathlib import Path
from pydocq.cli import analyze

class TestASTCLI:
    """Test suite for AST CLI functionality."""

    def test_analyze_simple_file(self, tmp_path):
        """Test analyzing a simple Python file."""
        # Create test file
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def hello(name: str) -> str:
    '''Say hello.'''
    return f"Hello, {name}"

class Greeter:
    '''Greeter class.'''
    def greet(self, name: str) -> str:
        return f"Hi, {name}"
""")

        # Analyze
        result = analyze(str(test_file), element=None, format="json")

        # Assertions
        assert result["type"] == "module"
        assert len(result["functions"]) == 1
        assert result["functions"][0]["name"] == "hello"
        assert len(result["classes"]) == 1
        assert result["classes"][0]["name"] == "Greeter"

    def test_analyze_specific_function(self, tmp_path):
        """Test analyzing a specific function."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def add(a: int, b: int) -> int:
    return a + b

def subtract(a: int, b: int) -> int:
    return a - b
""")

        result = analyze(str(test_file), element="add", format="json")

        assert result["name"] == "add"
        assert result["type"] == "function"
        assert result["args"] == ["a", "b"]

    def test_analyze_specific_class(self, tmp_path):
        """Test analyzing a specific class."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
class MyClass:
    def method1(self):
        pass

class OtherClass:
    def method2(self):
        pass
""")

        result = analyze(str(test_file), element="MyClass", format="json")

        assert result["name"] == "MyClass"
        assert result["type"] == "class"
        assert len(result["methods"]) == 2  # __init__ + method1

    def test_file_not_found(self):
        """Test error handling for missing file."""
        with pytest.raises(SystemExit):
            analyze("nonexistent.py", None, "json")

    def test_syntax_error(self, tmp_path):
        """Test error handling for invalid syntax."""
        test_file = tmp_path / "invalid.py"
        test_file.write_text("def broken(\n")  # Invalid syntax

        with pytest.raises(SystemExit):
            analyze(str(test_file), None, "json")

    def test_security_validation(self):
        """Test that dangerous paths are rejected."""
        import pytest
        from pydocq.analyzer.ast_analyzer import ASTSecurityError

        test_cases = [
            "../../etc/passwd",
            "/etc/passwd",
            "../.ssh/id_rsa",
            "~/../file.py",
        ]

        for path in test_cases:
            with pytest.raises((SystemExit, ASTSecurityError)):
                analyze(path, None, "json")

    def test_markdown_format(self, tmp_path):
        """Test markdown output format."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def test_func():
    '''Test function.'''
    pass
""")

        result = analyze(str(test_file), None, "markdown")

        assert isinstance(result, str)
        assert "test_func" in result
        assert "Test function" in result
```

### Integration Tests

```python
# tests/test_ast_integration.py
def test_analyze_real_package():
    """Test analyzing a real package file."""
    # Analyze pydocq's own files
    result = analyze("pydocq/cli.py", None, "json")

    assert result["type"] == "module"
    assert "query" in [f["name"] for f in result["functions"]]

def test_consistency_with_runtime():
    """Test that AST analysis matches runtime where possible."""
    import ast
    import tempfile

    # Create a simple file
    test_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
    test_file.write("""
def simple_func(x: int) -> int:
    return x * 2
""")
    test_file.close()

    # AST analysis
    ast_result = analyze(test_file.name, "simple_func", "json")

    # Runtime analysis (import it)
    import sys
    import importlib.util

    spec = importlib.util.spec_from_file_location("test_module", test_file.name)
    module = importlib.util.module_from_spec(spec)
    sys.modules["test_module"] = module
    spec.loader.exec_module(module)

    # Compare
    assert ast_result["name"] == "simple_func"
    assert ast_result["args"] == ["x"]

    # Cleanup
    import os
    os.unlink(test_file.name)
    del sys.modules["test_module"]
```

## Implementation Priority

1. **Immediate (P0):** Implement Option 2 (separate command)
2. **Short-term (P1):** Add Option 1 (flag-based) for backward compatibility
3. **Documentation (P1):** Update README with examples
4. **Testing (P0):** Add comprehensive test suite

## Migration Plan

### Phase 1: Core Implementation (Week 1)
- [ ] Add `analyze` command to CLI
- [ ] Implement `_extract_element()` helper
- [ ] Implement `_format_ast_module()` and `_format_ast_element()`
- [ ] Add error handling for security, file not found, syntax errors

### Phase 2: Testing (Week 1)
- [ ] Add unit tests for file analysis
- [ ] Add tests for element extraction
- [ ] Add error handling tests
- [ ] Add integration tests with real files

### Phase 3: Documentation (Week 2)
- [ ] Update README with AST analysis examples
- [ ] Add security documentation
- [ ] Add usage examples for CI/CD

### Phase 4: Enhanced Features (Optional)
- [ ] Add directory analysis (analyze all files in dir)
- [ ] Add output to file option
- [ ] Add diff mode (compare two files)

## Benefits

| Benefit | Impact |
|---------|--------|
| **No Installation Required** | Analyze code without dependencies |
| **Security** | Safe analysis of untrusted code |
| **CI/CD Friendly** | Generate docs in pipeline |
| **Quick Exploration** | Understand repos without setup |
| **Error Detection** | Find syntax errors before runtime |

## Related Issues

- [FEAT-002: LLM-Optimized Output Format](./009-llm-output-format.md)
- [SEC-002: File System Access Without Validation](./002-file-system-access-without-validation.md)

## References

- [AST Module Documentation](https://docs.python.org/3/library/ast.html)
- [Existing AST Analyzer](../pydocq/analyzer/ast_analyzer.py)

## Checklist

- [ ] Add `analyze` command to CLI
- [ ] Implement element extraction logic
- [ ] Implement JSON formatting for AST results
- [ ] Add support for all output formats (json, markdown, yaml, etc.)
- [ ] Add comprehensive error handling
- [ ] Add unit tests for file analysis
- [ ] Add unit tests for element extraction
- [ ] Add security tests
- [ ] Add integration tests
- [ ] Update README with examples
- [ ] Update CLI help text
- [ ] Add security documentation
