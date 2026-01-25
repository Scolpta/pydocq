# Usage Examples Extraction

Extract code examples from docstrings in a structured, agent-consumable format.

## Usage

```bash
doc <element> --examples
doc <element> --examples --include-output
```

## Examples

### Basic Examples

```bash
doc pandas.DataFrame.merge --examples
```

Output:
```json
{
  "path": "pandas.DataFrame.merge",
  "examples": [
    {
      "code": "df1.merge(df2, on='id')",
      "description": "Merge two DataFrames on a column"
    },
    {
      "code": "df1.merge(df2, left_on='lkey', right_on='rkey')",
      "description": "Merge on different column names"
    },
    {
      "code": "df1.merge(df2, how='outer')",
      "description": "Outer join (keep all rows)"
    }
  ]
}
```

### With Expected Output

```bash
doc pandas.DataFrame.sort_values --examples --include-output
```

Output:
```json
{
  "path": "pandas.DataFrame.sort_values",
  "examples": [
    {
      "code": "df.sort_values('column')",
      "description": "Sort by single column",
      "output": "   column\n2      1\n0      2\n1      3"
    },
    {
      "code": "df.sort_values(['col1', 'col2'])",
      "description": "Sort by multiple columns"
    }
  ]
}
```

### Doctests

```bash
doc mypackage.validate --examples
```

For docstring with doctests:
```python
def validate(data):
    """
    Validate input data.

    >>> validate([1, 2, 3])
    True
    >>> validate([])
    False
    >>> validate(None)
    Traceback (most recent call last):
        ...
    ValueError: Data cannot be None
    """
```

Output:
```json
{
  "path": "mypackage.validate",
  "examples": [
    {
      "code": "validate([1, 2, 3])",
      "output": "True",
      "type": "doctest"
    },
    {
      "code": "validate([])",
      "output": "False",
      "type": "doctest"
    },
    {
      "code": "validate(None)",
      "output": "Traceback (most recent call last):\n    ...\nValueError: Data cannot be None",
      "type": "doctest_exception"
    }
  ]
}
```

## Docstring Format Support

### Google Style

```python
def process(data):
    """
    Process data.

    Examples:
        >>> process([1, 2, 3])
        [2, 4, 6]

        >>> process([])
        []
    """
```

### NumPy Style

```python
def process(data):
    """
    Process data.

    Examples
    --------
    >>> process([1, 2, 3])
    [2, 4, 6]
    """
```

### reStructured Text

```python
def process(data):
    """
    Process data.

    :Example:

    >>> process([1, 2, 3])
    [2, 4, 6]
    """
```

## Structured Example Fields

Each example includes:

```json
{
  "code": "function_call()",
  "description": "What this example demonstrates",
  "output": "Expected result (if available)",
  "type": "example|doctest|snippet",
  "language": "python",
  "context": {
    "requires_import": ["numpy"],
    "setup": "df = pd.DataFrame({'A': [1, 2, 3]})"
  }
}
```

## Use Cases for Agents

### Learning API Usage

```python
# Agent: "How do I use pandas.DataFrame.merge?"

1. doc pandas.DataFrame.merge --examples
2. Agent gets 3-5 concrete examples
3. Can generate code based on patterns
```

### Generating Tests

```python
# Agent: "Generate tests for mymodule.process"

1. doc mymodule.process --examples
2. Extract examples
3. Convert to test cases
4. Add edge cases based on signature
```

### Documentation Search

```python
# Agent: "Find example of filtering with query"

1. Search across package: doc pandas --examples --filter="query"
2. Returns examples matching "query"
3. Agent sees actual usage patterns
```

### Code Generation

```python
# Agent: "Write code to load CSV and group by column"

1. doc pandas.read_csv --examples  # Get load pattern
2. doc pandas.DataFrame.groupby --examples  # Get groupby pattern
3. Combine patterns into working code
```

## Finding Examples

### Automatic Detection

The CLI looks for:
- `Examples:` section in docstrings
- `>>>` doctest prompts
- Code blocks in markdown
- Common patterns (`Example`, `Usage`, `Snippet`)

### Manual Specification

Via SDK decorator:

```python
from docs_cli import metadata

@metadata(
    examples=[
        {
            "code": "process([1, 2, 3])",
            "description": "Basic usage",
            "output": "[2, 4, 6]"
        },
        {
            "code": "process([], default=0)",
            "description": "Empty input with default"
        }
    ]
)
def process(data, default=None):
    pass
```

## Quality Metrics

```bash
doc pandas.DataFrame --examples --stats
```

Output:
```json
{
  "total_examples": 5,
  "with_output": 3,
  "with_description": 5,
  "coverage": "good",  # good | partial | none
  "recommendations": [
    "Add example for merge with multiple columns",
    "Include output for left join example"
  ]
}
```

## Batch Examples

Get examples for entire package:

```bash
doc pandas --examples --output=examples.json
```

Creates a searchable database of all examples:

```json
{
  "pandas.read_csv": {
    "examples": [...]
  },
  "pandas.DataFrame.merge": {
    "examples": [...]
  }
}
```

Agents can then search this offline:

```python
# Agent loads pre-extracted examples
examples = json.load(open("examples.json"))

# Finds relevant patterns
for func, data in examples.items():
    for example in data["examples"]:
        if "merge" in example["code"]:
            # Found usage pattern
```
