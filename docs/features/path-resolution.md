# Path Resolution

How the CLI resolves package paths to actual Python elements.

## Path Syntax

```
[package].[module].[element]
```

### Examples

```bash
# Package level
doc pandas

# Module level
doc pandas.core

# Class level
doc pandas.DataFrame
doc pandas.core.frame.DataFrame

# Method/Function level
doc pandas.DataFrame.__init__
doc pandas.DataFrame.groupby
doc pandas.read_csv
```

## Resolution Algorithm

### Step 1: Import the module

```python
import importlib

# "pandas.DataFrame" → import pandas.core.frame
# "pandas" → import pandas
```

The CLI walks the path segments and imports progressively:

1. `pandas` → import `pandas`
2. `pandas.core` → import `pandas.core`
3. `pandas.core.frame` → import `pandas.core.frame`

### Step 2: Navigate to element

```python
import inspect

module = importlib.import_module("pandas.core.frame")
DataFrame = getattr(module, "DataFrame")
```

For nested elements (methods, properties), use `inspect`:

```python
# pandas.DataFrame.groupby
cls = getattr(module, "DataFrame")
method = getattr(cls, "groupby")
```

### Step 3: Validate element type

Ensure the resolved element is queryable:

- **class**: has members, methods, properties
- **function**: has signature, docstring
- **module**: has sub-modules, classes, functions

## Error Handling

```bash
doc pandas.NonExistent
# → Error: Element "NonExistent" not found in pandas

doc invalid_package
# → Error: Package "invalid_package" not found (not installed)

doc pandas.DataFrame.invalid_method
# → Error: Method "invalid_method" not found in pandas.DataFrame
```

## Relative vs Absolute Paths

### Absolute Paths (Recommended)

```bash
doc pandas.DataFrame
doc pandas.core.frame.DataFrame
```

### Implicit Module Resolution

The CLI can find classes even without full module path:

```bash
doc pandas.DataFrame
# → Finds pandas.core.frame.DataFrame automatically
# → Uses inspect.getmodule() to resolve
```

This works by:
1. Getting the object: `getattr(pandas, "DataFrame")`
2. Asking Python where it's from: `inspect.getmodule(DataFrame)`
3. Returning full path: `pandas.core.frame.DataFrame`

## Special Cases

### Dotted names in functions

```python
def api.v1.endpoint():  # Function name with dots
    pass
```

Resolution:
```bash
doc mymodule."api.v1.endpoint"  # Quote the dotted name
```

### Aliased imports

```python
# In package/__init__.py
from .very_long_module_name import ShortName
```

Resolution:
```bash
doc package.ShortName  # Resolves to very_long_module_name
```

## Output Includes Resolved Path

Every query returns the fully resolved path:

```bash
doc pandas.DataFrame

# Output includes:
{
  "path": "pandas.core.frame.DataFrame",
  "import_path": "pandas.DataFrame",
  "source_file": "pandas/core/frame.py",
  "line": 123
}
```
