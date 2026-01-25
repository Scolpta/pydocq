# Example Decorator

Add usage examples directly in code via decorator.

## Usage

```python
from docs_cli import example

@example("process([1, 2, 3])")
@example("process([], default=0)")
def process(data, default=None):
    pass
```

## Examples

### Basic Examples

```python
from docs_cli import example

@example("read_csv('data.csv')")
@example("read_csv('data.csv', sep=';')")
@example("read_csv('data.csv', usecols=['A', 'B'])")
def read_csv(filepath, sep=',', usecols=None):
    """Read a CSV file."""
    pass
```

Query:
```bash
doc mymodule.read_csv --examples
```

Output:
```json
{
  "path": "mymodule.read_csv",
  "examples": [
    {
      "code": "read_csv('data.csv')",
      "source": "decorator"
    },
    {
      "code": "read_csv('data.csv', sep=';')",
      "source": "decorator"
    },
    {
      "code": "read_csv('data.csv', usecols=['A', 'B'])",
      "source": "decorator"
    }
  ]
}
```

### Example with Description

```python
@example(
    "DataFrame.merge(other, on='id')",
    description="Basic merge on column"
)
@example(
    "DataFrame.merge(other, left_on='lkey', right_on='rkey')",
    description="Merge on different column names"
)
def merge(self, other, on=None, left_on=None, right_on=None):
    pass
```

Query:
```bash
doc mymodule.DataFrame.merge --examples
```

Output:
```json
{
  "examples": [
    {
      "code": "DataFrame.merge(other, on='id')",
      "description": "Basic merge on column"
    },
    {
      "code": "DataFrame.merge(other, left_on='lkey', right_on='rkey')",
      "description": "Merge on different column names"
    }
  ]
}
```

### Example with Expected Output

```python
@example(
    "process([1, 2, 3])",
    output="[2, 4, 6]"
)
@example(
    "process([])",
    output="[]"
)
def process(data):
    pass
```

Query:
```bash
doc mymodule.process --examples --include-output
```

Output:
```json
{
  "examples": [
    {
      "code": "process([1, 2, 3])",
      "output": "[2, 4, 6]"
    },
    {
      "code": "process([])",
      "output": "[]"
    }
  ]
}
```

### Example with Setup

```python
@example(
    "df.groupby('category').sum()",
    setup="df = DataFrame({'category': ['A', 'B', 'A'], 'value': [1, 2, 3]})",
    description="Group by category and sum values"
)
def groupby(self, by):
    pass
```

Output includes setup code:
```json
{
  "example": {
    "code": "df.groupby('category').sum()",
    "setup": "df = DataFrame({'category': ['A', 'B', 'A'], 'value': [1, 2, 3]})",
    "description": "Group by category and sum values"
  }
}
```

## Decorator Signature

```python
@example(
    code,                    # The example code (string)
    description=None,        # Optional description
    output=None,             # Expected output
    setup=None,              # Setup code (e.g., df = ...)
    run=False,               # Whether to execute example to verify
    tags=[]                  # Tags for categorization
)
```

## Multiple Decorators

Stack multiple examples:

```python
@example("func(1)")
@example("func(2)")
@example("func(3, opt=True)")
def func(x, opt=False):
    pass
```

Or use single decorator with list:

```python
@example([
    "func(1)",
    "func(2)",
    "func(3, opt=True)"
])
def func(x, opt=False):
    pass
```

## Integration with Docstrings

The CLI combines examples from:
1. Decorator examples (structured)
2. Docstring examples (doctests, code blocks)

```bash
doc mymodule.process --examples
```

Output includes both sources:
```json
{
  "examples": [
    {
      "code": "process([1, 2, 3])",
      "source": "decorator"
    },
    {
      "code": "process(df)",
      "source": "docstring"
    }
  ]
}
```

## Use Cases for Agents

### Reliable Example Extraction

```python
# Agent: "Show me examples of pandas.merge"

1. doc pandas.DataFrame.merge --examples
2. Gets decorator examples (if available)
3. Falls back to docstring examples
4. Always structured, parseable
5. Can generate code based on patterns
```

### Code Generation

```python
# Agent: "Generate code to merge two DataFrames"

1. doc pandas.DataFrame.merge --examples
2. Finds example matching use case
3. Adapts to user's variable names
4. df1.merge(df2, on='id')
```

### Test Generation

```python
# Agent: "Generate tests for mymodule.process"

1. doc mymodule.process --examples
2. Each example becomes a test case
3. Generates:
   def test_process_example_1():
       result = process([1, 2, 3])
       assert result == [2, 4, 6]
```

### Example Validation

```python
# With run=True in decorator

@example("process([1, 2, 3])", output="[2, 4, 6]", run=True)
def process(data):
    pass

# CLI can verify example actually works
```

## Tags for Categorization

```python
@example(
    "func(x, y=1)",
    tags=["basic", "common"]
)
@example(
    "func(x, y=1, z=2)",
    tags=["advanced"]
)
def func(x, y=1, z=None):
    pass
```

Query by tag:
```bash
doc mymodule.func --examples --tags basic
```

Output:
```json
{
  "examples": [
    {
      "code": "func(x, y=1)",
      "tags": ["basic", "common"]
    }
  ]
}
```

## Conditional Examples

```python
@example(
    "func(x)",
    condition="x is list"
)
@example(
    "func(x, parallel=True)",
    condition="x is large dataset"
)
def func(x, parallel=False):
    pass
```

Output:
```json
{
  "examples": [
    {
      "code": "func(x)",
      "condition": "x is list"
    },
    {
      "code": "func(x, parallel=True)",
      "condition": "x is large dataset"
    }
  ]
}
```

## Example Metadata

```python
@example(
    "func(data)",
    metadata={
        "complexity": "simple",
        "estimated_time": "0.1s",
        "memory_usage": "low"
    }
)
```

Helps agents understand example characteristics.

## Storage

Examples stored on function:

```python
>>> func.__doc_examples__
[
    {"code": "func(x)", "description": "..."},
    {"code": "func(x, opt=True)", "description": "..."}
]
```

Accessible via CLI:
```bash
doc mymodule.func --examples
```
