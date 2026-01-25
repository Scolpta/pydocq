# pydocq

`pydocq` is a command-line interface tool for querying Python package documentation, specifically designed for AI agents. It provides structured, machine-readable JSON metadata about Python packages, classes, functions, and methods.

## Features

### Core Functionality

- **Path Resolution**: Query any Python element using dot notation (e.g., `pandas.DataFrame.merge`)
- **Runtime Introspection**: Extract signatures, docstrings, and source locations using Python's inspect module
- **Member Discovery**: List and categorize all members of modules and classes
- **Type Annotation Parsing**: Parse and analyze complex type annotations (Optional, Union, generics)
- **AST Static Analysis**: Analyze Python source code without importing it
- **Search Functionality**: Search elements by name pattern, docstring content, type, or metadata

### SDK Decorators

Add custom metadata to your code using decorators:

- `@metadata(**kwargs)`: Add arbitrary metadata
- `@example(code, description)`: Add code examples
- `@deprecated(reason, since, version)`: Mark as deprecated
- `@param(name, **info)`: Document parameters
- `@returns(**info)`: Document return values
- `@category(*categories)`: Categorize elements
- `@tag(*tags)`: Add tags
- `@when(version, condition)`: Add version information
- `@note(text)`: Add notes
- `@author(name, email)`: Add author information
- `@see_also(*references)`: Add cross-references

### Output Formats

- **json**: Structured, machine-readable JSON (default)
- **raw**: Human-readable text format
- **signature**: Minimal signature-only output
- **markdown**: Markdown documentation format
- **yaml**: YAML structure

## Installation

```bash
pip install pydocq
```

## Usage

### Basic Query

```bash
# Query a module
pydocq json

# Query a function
pydocq json.dumps

# Query a class
pydocq pandas.DataFrame

# Query a method
pydocq pandas.DataFrame.merge
```

### Output Options

```bash
# Verbose output (includes SDK metadata)
pydocq --verbose my_package.MyClass

# Compact output (only path, type, module_path)
pydocq --compact json.dumps

# Include source location
pydocq --include-source os.path.join

# Include SDK metadata
pydocq --include-metadata my_module.my_func

# Exclude docstring or signature
pydocq --no-docstring json.dumps
pydocq --no-signature json.dumps
```

### Output Formats

```bash
# JSON (default)
pydocq --format json json.dumps

# Raw text format
pydocq --format raw json.dumps

# Signature only
pydocq --format signature json.dumps

# Markdown format
pydocq --format markdown pandas.DataFrame

# YAML format
pydocq --format yaml json.dumps
```

### Member Discovery

```bash
# List all members of a module
pydocq --list-members json

# List all members including private ones
pydocq --list-members --include-private json

# List class members
pydocq --list-members builtins.str

# List class members including inherited
pydocq --list-members --include-inherited my_package.MyClass
```

## Using SDK Decorators

```python
from pydocq import metadata, example, deprecated, tag

@metadata(category="api", version="1.0")
@tag("important", "stable")
@example("result = my_function(42)", "Basic usage")
@deprecated("Use new_function instead", since="1.0", version="2.0")
def my_function(x: int) -> int:
    """Process an integer value.

    Args:
        x: The input value

    Returns:
        The processed value
    """
    return x * 2
```

Query with metadata:

```bash
pydocq --include-metadata my_module.my_function
```

Output:

```json
{
  "path": "my_module.my_function",
  "type": "function",
  "module_path": "my_module",
  "signature": {
    "parameters": [
      {
        "name": "x",
        "kind": "POSITIONAL_OR_KEYWORD",
        "annotation": "int",
        "default": null
      }
    ],
    "return_type": "int"
  },
  "docstring": {
    "docstring": "Process an integer value...",
    "length": 123
  },
  "sdk_metadata": {
    "category": "api",
    "version": "1.0",
    "tags": ["important", "stable"],
    "example": {"code": "result = my_function(42)", "description": "Basic usage"},
    "deprecated": {"reason": "Use new_function instead", "since": "1.0", "version": "2.0"}
  }
}
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/pydocq.git
cd pydocq

# Install with uv
uv pip install -e .

# Or with pip
pip install -e .
```

### Running Tests

```bash
# Install development dependencies
uv pip install pytest pytest-cov

# Run tests
pytest

# Run tests with coverage
pytest --cov=pydocq --cov-report=html
```

### Building for Distribution

```bash
# Build with uv
uv build

# Or with pip
python -m build

# The built package will be in dist/
```

## Project Structure

```
pydocq/
├── pydocq/
│   ├── __init__.py
│   ├── cli.py              # CLI interface
│   ├── analyzer/
│   │   ├── resolver.py      # Path resolution
│   │   ├── inspector.py     # Runtime introspection
│   │   ├── formatter.py     # JSON formatting
│   │   ├── discovery.py     # Member discovery
│   │   ├── errors.py        # Error handling
│   │   ├── type_parser.py   # Type annotation parsing
│   │   ├── ast_analyzer.py  # AST static analysis
│   │   ├── output_formats.py # Output formatters
│   │   └── search.py        # Search functionality
│   └── sdk/
│       ├── __init__.py
│       └── decorators.py     # SDK decorators
├── tests/
│   ├── test_cli.py
│   ├── test_resolver.py
│   ├── test_inspector.py
│   ├── test_formatter.py
│   ├── test_discovery.py
│   ├── test_errors.py
│   ├── test_type_parser.py
│   ├── test_ast_analyzer.py
│   ├── test_output_formats.py
│   ├── test_sdk_decorators.py
│   └── test_search.py
├── docs/                    # Internal documentation
├── README.md
├── LICENSE
├── pyproject.toml
└── .python-version
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

Built with:
- Typer for CLI interface
- Python's inspect module for runtime introspection
- Python's AST module for static analysis
- pytest for testing

## Changelog

### 0.2.0 (2025-01-25)

Security and Quality Improvements:
- Add input sanitization to prevent dynamic import vulnerabilities (SEC-001)
- Add file path validation to AST analyzer (SEC-002)
- Document and verify AST doesn't execute code (SEC-003)
- Extract duplicate type detection logic to centralized module (QUAL-001)
- Consolidate exception hierarchies into unified system (QUAL-002)
- Remove orphaned main.py placeholder file (QUAL-003)
- Add depth limits and cycle detection to search functions (QUAL-004)
- Rename docs_cli directory to pydocq for consistency
- All 231 tests pass

### 0.1.0 (2025-01-24)

- Initial release
- Path resolution for Python packages
- Runtime introspection with inspect module
- Member discovery for modules and classes
- Type annotation parsing
- AST static analysis
- SDK decorators for custom metadata
- Search functionality
- Multiple output formats (JSON, raw, signature, markdown, YAML)
- Comprehensive test coverage (178 tests)
