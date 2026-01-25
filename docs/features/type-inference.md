# Type Inference Summary

Summarize type information optimized for AI agent consumption.

## Usage

```bash
doc <element> --type-summary
doc <element> --type-summary --detailed
```

## Examples

### Function Types

```bash
doc pandas.DataFrame.__init__ --type-summary
```

Output:
```json
{
  "path": "pandas.DataFrame.__init__",
  "type": "method",
  "type_summary": {
    "accepts": [
      {
        "type": "dict",
        "description": "Dictionary of {column: array-like}",
        "example": "{'A': [1, 2, 3], 'B': ['x', 'y', 'z']}"
      },
      {
        "type": "list",
        "description": "List of records (dicts)",
        "example": "[{'A': 1, 'B': 'x'}, {'A': 2, 'B': 'y'}]"
      },
      {
        "type": "numpy.ndarray",
        "description": "2D NumPy array",
        "note": "Requires column names separately"
      },
      {
        "type": "None",
        "description": "Create empty DataFrame"
      }
    ],
    "returns": "None",
    "constraints": [
      "All arrays must have same length",
      "Column names must be hashable",
      "Dict keys are used as column names"
    ]
  }
}
```

### Return Type Variants

```bash
doc pandas.DataFrame.groupby --type-summary
```

Output:
```json
{
  "path": "pandas.DataFrame.groupby",
  "type_summary": {
    "accepts": [
      {
        "type": "str",
        "description": "Column name to group by"
      },
      {
        "type": "list[str]",
        "description": "Multiple column names"
      },
      {
        "type": "callable",
        "description": "Function applied to index"
      },
      {
        "type": "Series",
        "description": "Series with values to group by"
      }
    ],
    "returns": {
      "type": "DataFrameGroupBy | SeriesGroupBy",
      "depends_on": "called on DataFrame or Series",
      "note": "Returns iterator, not computed result"
    },
    "generic_over": ["T_FrameOrSeries"]
  }
}
```

### Union Types

```bash
doc pandas.read_csv --type-summary
```

Output:
```json
{
  "path": "pandas.read_csv",
  "type_summary": {
    "accepts": [
      {
        "type": "str",
        "description": "File path or URL"
      },
      {
        "type": "pathlib.Path",
        "description": "Path object"
      },
      {
        "type": "file-like",
        "description": "Object with read() method"
      }
    ],
    "returns": "DataFrame",
    "type_variants": {
      "filepath": "str | Path | file-like",
      "simplified": "Union[str, Path, IO[str]]"
    }
  }
}
```

## Detailed Mode

```bash
doc pandas.DataFrame --type-summary --detailed
```

Output includes:
```json
{
  "path": "pandas.DataFrame",
  "type_summary": {
    "attributes": [
      {
        "name": "shape",
        "type": "tuple[int, int]",
        "description": "(rows, columns)",
        "immutable": true
      },
      {
        "name": "columns",
        "type": "Index",
        "description": "Column labels",
        "mutable": true
      },
      {
        "name": "dtypes",
        "type": "Series",
        "description": "Data types per column",
        "note": "Index is column names"
      }
    ],
    "methods": {
      "returns_dataframe": [
        "sort_values",
        "fillna",
        "dropna"
      ],
      "returns_series": [
        "groupby",
        "__getitem__"
      ],
      "returns_scalar": [
        "count",
        "sum",
        "mean"
      ]
    }
  }
}
```

## Type Constraints

```bash
doc pandas.DataFrame.astype --type-summary
```

Output:
```json
{
  "path": "pandas.DataFrame.astype",
  "type_summary": {
    "accepts": [
      {
        "type": "dict",
        "description": "{column_name: dtype}",
        "constraint": "Column names must exist in DataFrame"
      },
      {
        "type": "str",
        "description": "Named dtype",
        "values": ["int", "float", "str", "bool", "category"],
        "constraint": "Must be valid numpy/pandas dtype"
      },
      {
        "type": "type",
        "description": "Python type object",
        "examples": [int, float, str]
      }
    ],
    "runtime_checks": [
      "Invalid conversion raises ValueError",
      "Incompatible conversion raises TypeError"
    ]
  }
}
```

## Generic Types

```bash
from typing import TypeVar, List

T = TypeVar('T')

def process(items: List[T]) -> T:
    ...

doc mymodule.process --type-summary
```

Output:
```json
{
  "type_summary": {
    "generic": true,
    "type_vars": ["T"],
    "constraint": "T must be consistent across input and output",
    "instantiations": [
      {"T": "int", "input": "List[int]", "output": "int"},
      {"T": "str", "input": "List[str]", "output": "str"}
    ]
  }
}
```

## Use Cases for Agents

### Type Compatibility

```python
# Agent: "Can I pass a list of dicts to DataFrame?"

1. doc pandas.DataFrame.__init__ --type-summary
2. Sees "list" in accepts
3. Check description: "List of records (dicts)"
4. Yes, compatible
```

### Finding Converters

```python
# Agent: "How to convert DataFrame to dict?"

1. doc pandas.DataFrame --type-summary --detailed
2. Look for "returns_dict" or returns "dict" type
3. Found: DataFrame.to_dict() returns dict
```

### Understanding Constraints

```python
# Agent: "Why does my code fail?"

User code: df.astype({"A": "invalid_type"})

1. doc pandas.DataFrame.astype --type-summary
2. Agent sees: "Must be valid numpy/pandas dtype"
3. Explains constraint to user
```

### Generating Type-Safe Code

```python
# Agent: "Write function to process DataFrame"

1. doc pandas.DataFrame --type-summary
2. Understands accepts: dict, list, ndarray
3. Generates type-safe code with Union:
   def load_data(source: Union[str, Path, dict, List[dict]]) -> pd.DataFrame:
       ...
```

## Type System Support

### Python Type Hints

```python
def process(data: list[int] | None) -> dict[str, int]:
    pass
```

Extracted as:
```json
{
  "accepts": "list[int] | None",
  "returns": "dict[str, int]"
}
```

### NumPy/Pandas Style

```python
def process(data: np.ndarray) -> pd.DataFrame:
    """
    Parameters
    ----------
    data : ndarray, shape (n, m)
        Input array
    """
```

Extracted from docstring:
```json
{
  "accepts": "np.ndarray",
  "shape_constraint": "(n, m)"
}
```

### String Annotations

```python
def process(data: "List[int]") -> "Dict[str, int]":
    pass
```

Resolved via `typing.get_type_hints()`:
```json
{
  "accepts": "List[int]",
  "returns": "Dict[str, int]"
}
```

## Comparison with Other Formats

### Regular `doc` command:
```json
{
  "signature": {
    "parameters": [
      {"name": "data", "annotation": "list[int] | None"}
    ]
  }
}
```

### `--type-summary`:
```json
{
  "type_summary": {
    "accepts": [
      {"type": "list[int]", "description": "..."},
      {"type": "None", "description": "..."}
    ],
    "simplified": "Accepts list of ints or None"
  }
}
```

## Inference Without Annotations

When type annotations are missing, infer from:

### Default Values
```python
def process(data=None):
    # → accepts: None (inferred)
```

### Docstring Types
```python
def process(data):
    """
    Parameters
    ----------
    data : list of int
    """
    # → accepts: list[int] (from docstring)
```

### Usage Patterns (experimental)
```python
def process(data):
    return len(data)  # → data has __len__
    # Could infer: Sized | Sequence | Collection
```
