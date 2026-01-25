# Output Formats

Structured data formats for AI agent consumption.

## Default Format: JSON

```bash
doc pandas.DataFrame
```

Output:
```json
{
  "path": "pandas.DataFrame",
  "type": "class",
  "docstring": "Two-dimensional, size-mutable, potentially heterogeneous tabular data.",
  "source_location": {
    "file": "pandas/core/frame.py",
    "line": 123
  },
  "members": [
    {
      "name": "__init__",
      "type": "method",
      "docstring": "Initialize DataFrame.",
      "signature": {
        "parameters": [
          {
            "name": "data",
            "type": "Any | None",
            "default": "null"
          }
        ],
        "returns": {
          "type": "None"
        }
      }
    }
  ],
  "metadata": {}
}
```

## Format Options

### `--format json` (default)

Full structured metadata:

```bash
doc pandas.DataFrame --format json
```

### `--format raw`

Docstring only, plain text:

```bash
doc pandas.DataFrame --format raw
```

Output:
```
Two-dimensional, size-mutable, potentially heterogeneous tabular data.

Parameters
----------
data : ndarray, Iterable, dict, or DataFrame
    Dict can contain Series, arrays, constants, or list-like objects.
...
```

### `--format schema`

JSON Schema representation of the element:

```bash
doc pandas.DataFrame.__init__ --format schema
```

Output:
```json
{
  "type": "object",
  "properties": {
    "data": {
      "type": ["array", "object", "null"],
      "description": "Input data structure"
    }
  }
}
```

### `--format signature`

Type signature only:

```bash
doc pandas.DataFrame.append --format signature
```

Output:
```
(other: DataFrame, sort: bool = False, verify_integrity: bool = False) -> DataFrame
```

## Filtering Output

### `--include-source`

Include source code in output:

```bash
doc pandas.DataFrame --include-source
```

Output includes:
```json
{
  "path": "pandas.DataFrame",
  "source": "class DataFrame:\n    def __init__(...):\n        ..."
}
```

### `--include-docstring-only`

Skip metadata, only docstring:

```bash
doc pandas.DataFrame --include-docstring-only
```

### `--members-only`

List members without details:

```bash
doc pandas.DataFrame --members-only
```

Output:
```json
{
  "members": ["__init__", "groupby", "merge", "join", ...]
}
```

## Compact vs Pretty Output

### Pretty (default)

```bash
doc pandas.DataFrame
```

Human-readable JSON with indentation.

### Compact

```bash
doc pandas.DataFrame --compact
```

Single-line JSON, minimal whitespace.

## Element Type Schemas

### Function Output

```json
{
  "path": "pandas.read_csv",
  "type": "function",
  "docstring": "Read a comma-separated values (csv) file into DataFrame.",
  "signature": {
    "parameters": [
      {
        "name": "filepath_or_buffer",
        "type": "str | Path",
        "required": true
      },
      {
        "name": "sep",
        "type": "str",
        "default": ",",
        "required": false
      }
    ],
    "returns": {
      "type": "pandas.DataFrame"
    }
  },
  "decorators": ["@deprecate_kwarg"],
  "source_location": {...},
  "metadata": {}
}
```

### Class Output

```json
{
  "path": "pandas.DataFrame",
  "type": "class",
  "docstring": "...",
  "bases": ["pandas.generic.NDFrame"],
  "members": [
    {
      "name": "__init__",
      "type": "method"
    },
    {
      "name": "groupby",
      "type": "method"
    },
    {
      "name": "shape",
      "type": "property"
    }
  ],
  "source_location": {...},
  "metadata": {}
}
```

### Module Output

```json
{
  "path": "pandas.core.frame",
  "type": "module",
  "docstring": "DataFrame data structure",
  "imports": [
    "pandas._libs.lib",
    "numpy"
  ],
  "classes": ["DataFrame"],
  "functions": [],
  "source_location": {...},
  "metadata": {}
}
```

## Streaming for Large Results

For packages with many members:

```bash
doc pandas --stream
```

Outputs each element as a separate JSON line (NDJSON):

```json
{"name": "DataFrame", "type": "class", ...}
{"name": "Series", "type": "class", ...}
{"name": "read_csv", "type": "function", ...}
```

Useful for processing with other tools:

```bash
doc pandas --stream | jq 'select(.type == "class")'
```
