# Metadata SDK

Low-level decorator for adding custom metadata to Python elements.

## Philosophy

The SDK is **non-opinionated**:
- Generic storage mechanism
- No prescribed schema
- Users define their own metadata structure
- Agent decides what to extract

## Basic Usage

```python
from docs_cli import metadata

@metadata(
    category="data-processing",
    side_effects=["io_write", "database"],
    performance="O(n)",
    thread_safe=False
)
def process_data(data):
    """Process the input data."""
    pass
```

The decorator stores metadata on the function:

```python
>>> process_data.__doc_metadata__
{
  'category': 'data-processing',
  'side_effects': ['io_write', 'database'],
  'performance': 'O(n)',
  'thread_safe': False
}
```

## How It Works

```python
def metadata(**data):
    """Store arbitrary metadata on a function/class."""
    def decorator(obj):
        obj.__doc_metadata__ = data
        return obj
    return decorator
```

That's it. No validation, no schema, just storage.

## Use Cases

### Semantic Information

```python
@metadata(
    category="pipeline",
    stage="transform",
    input_type="dataset",
    output_type="processed_dataset"
)
def transform(data):
    pass
```

### Constraints

```python
@metadata(
    preconditions=["len(data) > 0", "data is not None"],
    postconditions=["returns dict", "result.status == 'success'"]
)
def validate(data):
    pass
```

### Deprecation

```python
@metadata(
    deprecated=True,
    deprecated_in="2.0",
    use_instead="new_function"
)
def old_function():
    pass
```

### Agent-Specific Hints

```python
@metadata(
    llm_priority="high",          # Show this first
    llm_context="important",      # Include in summaries
    llm_examples=[                # Usage examples
        "process(data)",
        "process(data, optimize=True)"
    ]
)
def process(data, optimize=False):
    pass
```

### Custom Fields

```python
@metadata(
    my_custom_field="anything",
    project_specific={...},
    nested={
        "deep": {
            "structure": "works"
        }
    }
)
def func():
    pass
```

## Works on Any Callable

```python
# Functions
@metadata(category="utils")
def helper():
    pass

# Classes
@metadata(domain="data-structures")
class DataStore:
    pass

# Methods
class Processor:
    @metadata(thread_safe=True)
    def process(self):
        pass

# Async functions
@metadata(requires="async_context")
async def async_process():
    pass
```

## CLI Integration

Metadata is automatically included in CLI output:

```bash
doc mypackage.process_data

# Output:
{
  "name": "process_data",
  "type": "function",
  "docstring": "Process the input data.",
  "signature": {...},
  "metadata": {
    "category": "data-processing",
    "side_effects": ["io_write", "database"],
    "performance": "O(n)",
    "thread_safe": false
  }
}
```

## Combining with Other Decorators

```python
@metadata(category="api")
@route("/users")
@login_required
def get_users():
    pass
```

The metadata decorator preserves other decorators:

```python
>>> get_users.__doc_metadata__
{'category': 'api'}
```

## Alternative: File-Based Metadata

Instead of decorating code, use YAML files:

```yaml
# .docs-cli/metadata.yaml
process_data:
  category: data-processing
  side_effects: [io_write, database]
  performance: O(n)

validate:
  preconditions:
    - len(data) > 0
    - data is not None
```

**Trade-off:**
- Decorators: Co-located with code, always in sync
- Files: No code modification, but can get out of sync
