# Package Discovery

Listing what's available in a package.

## Usage

```bash
doc <package>                    # List public elements
doc <package> --include-private  # Include private elements
doc <package>.<module>           # List module contents
```

## Examples

```bash
doc pandas
# → Lists: DataFrame, Series, read_csv, ...

doc pandas.core.frame
# → Lists DataFrame class and its members

doc myproject --include-private
# → Shows everything, including _internal functions
```

## Output Format

```json
{
  "path": "pandas",
  "type": "package",
  "members": [
    {
      "name": "DataFrame",
      "type": "class",
      "path": "pandas.DataFrame",
      "docstring": "Two-dimensional tabular data structure."
    },
    {
      "name": "Series",
      "type": "class",
      "path": "pandas.Series",
      "docstring": "One-dimensional array with axis labels."
    },
    {
      "name": "read_csv",
      "type": "function",
      "path": "pandas.read_csv",
      "signature": {
        "params": [
          {"name": "filepath", "type": "str | Path"},
          {"name": "sep", "type": "str", "default": ","}
        ]
      }
    }
  ]
}
```

## Discovery Strategy

The CLI uses multiple strategies to find public elements, in order:

### 1. `__all__` (Preferred)

If the package defines `__all__`, use it:

```python
# package/__init__.py
__all__ = ["PublicClass", "public_function"]
```

### 2. Parse `__init__.py` imports

Analyze what's imported in the package's `__init__.py`:

```python
# package/__init__.py
from .module import PublicClass
from .utils import public_function

# These are considered public
```

### 3. Fallback: Filter by naming convention

List non-private symbols (not starting with `_`):

```python
def public_func(): pass
def _internal_func(): pass  # Excluded
```

## Internal Projects: Explicit Declaration

For better control, explicitly declare public symbols:

### Option A: Use `__all__`

```python
# myproject/__init__.py
from .core import Processor, Transformer
from .utils import helper

__all__ = ["Processor", "Transformer"]
```

### Option B: Decorator (Future SDK Feature)

```python
from docs_cli import public

@public
class Processor:
    pass

def _internal_helper():
    pass  # Won't appear in discovery
```

## Output Filtering

```bash
doc pandas --filter "type:class"           # Only classes
doc pandas --filter "docstring:na"         # Contains "na" in docstring
doc pandas --filter "decorator:cache"      # Has @cache decorator
```

## See Also

- **[Search](./search.md)** - Advanced search across packages with more complex criteria
- **[Path Resolution](./path-resolution.md)** - How the CLI resolves paths to elements
- **[Query Language](./query-language.md)** - For even more powerful queries
- **[Category Decorator](./sdk-category.md)** - Organize elements with categories for easier discovery
