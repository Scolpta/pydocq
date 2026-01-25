# Relationship Analysis

Understanding how code elements relate to each other.

## Usage

```bash
doc <element> --relations
doc <element> --relations=inheritance    # Only inheritance
doc <element> --relations=calls          # Only function calls
```

## Examples

### Class Relationships

```bash
doc pandas.DataFrame --relations
```

Output:
```json
{
  "path": "pandas.DataFrame",
  "type": "class",
  "relations": {
    "inheritance": {
      "inherits_from": ["pandas.generic.NDFrame"],
      "inherited_by": ["pandas.core.series.Series", "pandas.core.sparse.frame.SparseDataFrame"]
    },
    "composition": {
      "uses": ["numpy.ndarray", "pandas.core.index.Index"],
      "used_by": ["pandas.read_csv", "pandas.concat"]
    }
  }
}
```

### Function Call Relationships

```bash
doc pandas.DataFrame.groupby --relations=calls
```

Output:
```json
{
  "path": "pandas.DataFrame.groupby",
  "type": "method",
  "relations": {
    "calls": [
      {
        "target": "pandas.core.groupby.GroupBy",
        "type": "constructor",
        "line": 1234
      },
      {
        "target": "pandas.core.common.is_list_like",
        "type": "function",
        "line": 1235
      }
    ],
    "called_by": [
      {
        "source": "pandas.read_csv",
        "context": "after loading data"
      }
    ]
  }
}
```

### Import Dependencies

```bash
doc pandas.core.frame --relations=imports
```

Output:
```json
{
  "path": "pandas.core.frame",
  "type": "module",
  "relations": {
    "imports": [
      {"module": "numpy", "as": "np"},
      {"module": "pandas._libs.lib", "items": ["maybe_convert_objects"]},
      {"module": "pandas.core.generic", "items": ["NDFrame"]}
    ],
    "imported_by": [
      "pandas",
      "pandas.tests.frame.test_api"
    ]
  }
}
```

## Relationship Types

### Inheritance

```bash
doc mymodule.BaseModel --relations=inheritance
```

Shows:
- Parent classes
- Child classes
- Mixin classes
- Abstract base classes

### Calls / Called By

```bash
doc mymodule.process_data --relations=calls
```

Shows:
- Functions/methods this element calls
- Functions/methods that call this element
- Call frequency (if available)

### Dependencies

```bash
doc mypackage --relations=dependencies
```

Shows:
- Required packages
- Optional dependencies
- Development dependencies

### Similar Elements

```bash
doc pandas.DataFrame --relations=similar
```

Shows:
- Classes with similar methods
- Functions with similar signatures
- Related by naming conventions

## Use Cases for Agents

### Impact Analysis

```python
# Agent: "What breaks if I change pandas.DataFrame.__init__?"

1. doc pandas.DataFrame.__init__ --relations=called_by
2. Returns: all functions that call __init__
3. Agent knows impact scope
```

### Finding Entry Points

```python
# Agent: "How do I create a DataFrame from code?"

1. doc pandas.DataFrame --relations=used_by
2. Find construction patterns in called_by
3. Returns: pandas.read_csv, pandas.DataFrame.__init__, pandas.from_dict
```

### Understanding Architecture

```python
# Agent: "What's the class hierarchy?"

1. doc pandas.DataFrame --relations=inheritance
2. Agent can walk up/down the tree
3. Understand shared behavior from base classes
```

## Implementation Notes

### Static Analysis (AST)

For "calls" relationships, parse the function body:

```python
import ast

def extract_calls(func_code):
    tree = ast.parse(func_code)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            yield unparse(node.func)
```

### Runtime Inspection

For "inheritance", use Python introspection:

```python
import inspect

def get_inheritance(cls):
    return {
        "bases": [c.__module__ + "." + c.__name__ for c in cls.__bases__],
        "subclasses": [c.__module__ + "." + c.__name__ for c in cls.__subclasses__()]
    }
```

### Module Level

For "imports", parse module-level imports:

```python
def extract_imports(module_path):
    tree = ast.parse(open(module_path).read())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            yield node.module
        elif isinstance(node, ast.ImportFrom):
            yield node.module
```

## Performance Considerations

- Shallow analysis (direct relationships only) by default
- Deep analysis with `--depth` flag
- Cache results for repeated queries

```bash
doc pandas.DataFrame --relations --depth=2  # Include indirect relationships
```

## Filtering

```bash
doc pandas.DataFrame --relations=calls --filter="external"
# Only show calls to other packages

doc pandas.DataFrame --relations=calls --filter="internal"
# Only show calls within same package
```
