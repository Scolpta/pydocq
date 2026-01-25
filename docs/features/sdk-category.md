# Category Decorator

Categorize elements to help agents organize and search by functional domain.

## Usage

```python
from docs_cli import category

@category("data-processing")
def read_csv(filepath):
    pass

@category("visualization")
def plot(data):
    pass

@category("data-processing")
@category("io")  # Multiple categories
def read_json(filepath):
    pass
```

## Examples

### Single Category

```python
@category("data-transformation")
def transform(data):
    pass

@category("aggregation")
def groupby(data, key):
    pass
```

Query:
```bash
doc mypackage.transform --category
```

Output:
```json
{
  "path": "mypackage.transform",
  "category": "data-transformation"
}
```

### Multiple Categories

```python
@category("io")
@category("file-format")
@category("csv")
def read_csv(filepath):
    pass
```

Query:
```bash
doc mypackage.read_csv --category
```

Output:
```json
{
  "path": "mypackage.read_csv",
  "categories": ["io", "file-format", "csv"]
}
```

### Hierarchical Categories

```python
@category("data/io")
@category("data/io/csv")
def read_csv(filepath):
    pass

@category("data/io/json")
def read_json(filepath):
    pass
```

Query by hierarchy:
```bash
doc mypackage --category "data/io"
```

Returns both `read_csv` and `read_json`.

### Class-Level Categories

```python
@category("data-structures")
class DataFrame:
    pass

@category("visualization")
@category("charts")
class BarChart:
    pass
```

### Method-Level Categories

```python
class DataFrame:
    @category("filtering")
    def query(self, expr):
        pass

    @category("aggregation")
    def groupby(self, key):
        pass
```

## Query by Category

### List All in Category

```bash
doc pandas --category visualization
```

Output:
```json
{
  "category": "visualization",
  "members": [
    {"path": "pandas.DataFrame.plot", "type": "method"},
    {"path": "pandas.plotting.hist", "type": "function"},
    {"path": "pandas.plotting.scatter", "type": "function"}
  ]
}
```

### Multiple Categories

```bash
doc mypackage --category data-processing --category io
```

Output members in either category.

### Category Tree

```bash
doc mypackage --category-tree
```

Output:
```json
{
  "categories": {
    "data": {
      "io": {
        "csv": ["read_csv", "to_csv"],
        "json": ["read_json", "to_json"]
      },
      "processing": {
        "transform": ["transform", "apply"],
        "aggregate": ["groupby", "agg"]
      }
    },
    "visualization": {
      "charts": ["plot", "bar", "hist"],
      "tables": ["style", "format"]
    }
  }
}
```

## Decorator Options

### With Description

```python
@category("data-processing", description="Functions for processing and transforming data")
def process(data):
    pass
```

### With Tags

```python
@category("io", tags=["file", "csv", "input"])
def read_csv(filepath):
    pass

@category("io", tags=["file", "csv", "output"])
def to_csv(df, filepath):
    pass
```

Filter by tags:
```bash
doc mypackage --category io --tags output
```

## Use Cases for Agents

### Discovering Features by Domain

```python
# Agent: "What visualization functions are available?"

1. doc pandas --category visualization
2. Gets list of visualization functions
3. "pandas has plot(), hist(), scatter(), bar() for visualization"
4. Can explain each one
```

### Organizing Explanations

```python
# Agent: "Explain pandas API"

1. Get category tree
2. Organize explanation by categories
3. "Data IO: read_csv, read_json, ...\nData Processing: transform, groupby, ...\nVisualization: ..."
```

### Finding Related Functions

```python
# Agent: "What else can I do with CSV files?"

1. doc pandas --category csv
2. Gets all CSV-related functions
3. "read_csv, to_csv, read_csv_chunked, ..."
```

### Structured Recommendations

```python
# Agent: "I want to filter and plot data"

1. Check categories: filtering, visualization
2. Find functions in those categories
3. "Use query() for filtering, then plot() for visualization"
```

### Package Overview

```python
# Agent: "What does this package provide?"

1. doc mypackage --category-tree
2. Shows category structure
3. "This package provides:\n- Data IO (CSV, JSON)\n- Processing (transform, aggregate)\n- Visualization"
```

## Category Inheritance

Classes inherit categories to methods:

```python
@category("data-structures")
class DataFrame:
    def groupby(self):
        pass  # Inherits "data-structures" category

    @category("aggregation")  # Additional category
    def agg(self):
        pass  # Has both "data-structures" and "aggregation"
```

## Module-Level Categories

```python
# mypackage/io/__init__.py
from docs_cli import package_category

@package_category("data-io")
```

All functions in module get this category unless overridden.

## Category Aliases

```python
@category("data-processing", aliases=["processing", "transform"])
def process(data):
    pass
```

Query:
```bash
doc mypackage --category processing  # Finds process()
```

## Category Metadata

```python
@category(
    "visualization",
    icon="📊",
    color="blue",
    priority=1
)
def plot(data):
    pass
```

For UI/organization purposes.

## Category Statistics

```bash
doc mypackage --category-stats
```

Output:
```json
{
  "categories": {
    "data-processing": {
      "count": 25,
      "functions": 20,
      "classes": 5
    },
    "visualization": {
      "count": 15,
      "functions": 15,
      "classes": 0
    }
  },
  "uncategorized": 8
}
```

## Combining with Other Decorators

```python
@category("data-processing")
@deprecated(since="2.0", use_instead="new_process")
@example("process(data)")
@returns(DataFrame)
def process(data):
    pass
```

All metadata is preserved and queryable.

## Storage

Categories stored on function:

```python
>>> process.__doc_categories__
['data-processing']
>>> process.__doc_category_metadata__
{'description': '...', 'tags': [...]}
```

## Standard Categories

Suggested standard categories for consistency:

- **Data IO**: `data-io`, `csv`, `json`, `database`
- **Processing**: `data-processing`, `transform`, `aggregate`, `filter`
- **Visualization**: `visualization`, `charts`, `plots`
- **Utilities**: `utils`, `helpers`, `validation`
- **API**: `api`, `routes`, `endpoints`
- **Testing**: `testing`, `mocks`, `fixtures`

Projects can define their own taxonomy.

## Category Validation

```python
from docs_cli import validate_categories

@validate_categories(["data-io", "data-processing", "visualization"])
@category("invalid-category")  # Error during linting
def func():
    pass
```

Ensures consistent category usage across project.
