# Deprecated Decorator

Mark elements as deprecated with migration metadata.

## Usage

```python
from docs_cli import deprecated

@deprecated(
    since="2.0",
    removed_in="3.0",
    use_instead="new_process()",
    reason="More consistent with other functions"
)
def old_process():
    pass
```

## Examples

### Basic Deprecation

```python
@deprecated(
    since="2.0",
    use_instead="concat()"
)
def append(self, other):
    pass
```

Query:
```bash
doc pandas.DataFrame.append --deprecation
```

Output:
```json
{
  "path": "pandas.DataFrame.append",
  "deprecated": true,
  "deprecation_info": {
    "since": "2.0",
    "use_instead": "concat()",
    "source": "decorator"
  }
}
```

### With Removal Version

```python
@deprecated(
    since="1.0",
    removed_in="2.0",
    use_instead="loc[] or iloc[]",
    reason="Confusing behavior, replaced by explicit indexers"
)
def ix(self):
    pass
```

Query:
```bash
doc pandas.DataFrame.ix --deprecation
```

Output:
```json
{
  "deprecated": true,
  "since": "1.0",
  "removed_in": "2.0",
  "use_instead": "loc[] or iloc[]",
  "reason": "Confusing behavior, replaced by explicit indexers",
  "urgency": "critical"
}
```

### With Migration Guide

```python
@deprecated(
    since="2.0",
    use_instead="new_func()",
    migration_guide="""
    Replace:
        old_func(data, opt=True)

    With:
        new_func(data, mode='strict')
    """
)
def old_func(data, opt=False):
    pass
```

Query includes migration guide:
```json
{
  "deprecated": true,
  "since": "2.0",
  "use_instead": "new_func()",
  "migration_guide": "Replace:\n    old_func(data, opt=True)\n\nWith:\n    new_func(data, mode='strict')"
}
```

### Class Deprecation

```python
@deprecated(
    since="1.5",
    removed_in="2.0",
    use_instead="Regular Series with sparse dtype",
    reason="SparseSeries is redundant"
)
class SparseSeries(Series):
    pass
```

### Parameter Deprecation

```python
from docs_cli import deprecated_param

def process(
    data,
    @deprecated_param(since="2.0", use_instead="mode='strict'")
    legacy_param=None,
    mode='auto'
):
    pass
```

Or simpler:

```python
from docs_cli import param

def process(
    data,
    legacy_param: param(deprecated="2.0", use_instead="mode") = None,
    mode='auto'
):
    pass
```

## Decorator Signature

```python
@deprecated(
    since,              # Version when deprecation started
    removed_in=None,    # Optional: version when it will be removed
    use_instead=None,   # What to use instead
    reason=None,        # Why it's deprecated
    migration_guide=None  # Detailed migration instructions
)
```

## Integration with Warnings

Combine with Python's warnings module:

```python
import warnings
from docs_cli import deprecated

@deprecated(since="2.0", use_instead="new_func()")
def old_func():
    warnings.warn(
        "old_func is deprecated, use new_func instead",
        DeprecationWarning,
        stacklevel=2
    )
```

Or automatic warning generation:

```python
from docs_cli import deprecated

@deprecated(since="2.0", auto_warn=True)
def old_func():
    pass
# Automatically shows warning when called
```

## Querying Deprecations

### Check Single Element

```bash
doc mymodule.old_func --deprecation
```

### Find All Deprecated in Package

```bash
doc pandas --deprecated
```

Output:
```json
{
  "deprecated_elements": [
    {"path": "pandas.DataFrame.append", "since": "2.0"},
    {"path": "pandas.DataFrame.ix", "since": "0.20", "removed_in": "1.0"},
    {"path": "pandas.SparseSeries", "since": "1.5", "removed_in": "2.0"}
  ]
}
```

### Filter by Removal Status

```bash
doc myproject --deprecated --removed-only
```

Only show items that are scheduled for removal.

## Use Cases for Agents

### Avoid Suggesting Deprecated Code

```python
# Agent: "How do I append rows to a DataFrame?"

1. doc pandas.DataFrame.append --deprecation
2. Sees deprecated in 2.0
3. Doesn't suggest append()
4. Suggests concat() instead
```

### Migration Assistance

```python
# Agent: "Update my code for pandas 2.0"

1. Scan code for deprecated functions
2. For each, check deprecation info
3. doc pandas.DataFrame.ix --deprecation
4. Gets: use_instead="loc[] or iloc[]"
5. Generates migration:
   df.ix[row] → df.loc[row]
```

### Deprecation Warnings

```python
# Agent: "Review my code"

Sees user calling old_func()

1. doc mymodule.old_func --deprecation
2. Warns user
3. "old_func is deprecated since 2.0, use new_func instead"
4. Offers to migrate
```

### Version Compatibility

```python
# Agent: "Is this code compatible with pandas 3.0?"

1. Check all used functions
2. For each, check deprecation
3. doc pandas.DataFrame.append --deprecation
4. Sees: removed_in="3.0"
5. "This code uses DataFrame.append which will be removed in 3.0"
```

## Deprecation Timeline

```bash
doc myproject --deprecation-timeline
```

Output:
```json
{
  "current_version": "2.1",
  "timeline": [
    {
      "element": "old_func",
      "deprecated": "2.0",
      "removed": "3.0",
      "status": "deprecated",
      "time_remaining": "~2 minor versions"
    },
    {
      "element": "ancient_func",
      "deprecated": "1.0",
      "removed": "2.0",
      "status": "removed",
      "action": "immediate replacement needed"
    }
  ]
}
```

## Batch Migration

```bash
doc myproject --generate-migration-plan --target-version 3.0
```

Output:
```json
{
  "migration_plan": [
    {
      "element": "DataFrame.append",
      "replacement": "pd.concat",
      "files_affected": ["data_processing.py", "utils.py"],
      "complexity": "low"
    },
    {
      "element": "DataFrame.ix",
      "replacement": "loc/iloc",
      "files_affected": ["legacy.py"],
      "complexity": "medium"
    }
  ]
}
```

## Storage

Deprecation info stored on function:

```python
>>> old_func.__doc_deprecation__
{
  'since': '2.0',
  'use_instead': 'new_func()',
  'reason': '...'
}
```

Accessible via CLI.

## Semantic Versioning Integration

For packages following semver:

```python
@deprecated(
    since="2.0.0",
    removed_in="3.0.0"
)
def func():
    pass
```

CLI can interpret version numbers:
- Major version bump → breaking changes allowed
- Can plan removal schedule based on semver

## Gradual Deprecation

```python
@deprecated(
    since="2.0",
    removed_in="3.0",
    stages=[
        {"version": "2.0", "action": "warning"},
        {"version": "2.5", "action": "loud warning"},
        {"version": "3.0", "action": "remove"}
    ]
)
def func():
    pass
```
