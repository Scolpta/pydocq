# Version / Deprecation Info

Track deprecation status and version information for code elements.

## Usage

```bash
doc <element> --deprecation
doc <element> --deprecation --check-compat 3.0  # Check compatibility with version
```

## Examples

### Deprecated Method

```bash
doc pandas.DataFrame.append --deprecation
```

Output:
```json
{
  "path": "pandas.DataFrame.append",
  "deprecated": true,
  "deprecation_info": {
    "deprecated_in": "2.0",
    "removed_in": "3.0",
    "use_instead": "pandas.concat",
    "reason": "append() has inconsistent behavior with other DataFrame methods",
    "migration_guide": "Use pd.concat([df1, df2]) instead of df1.append(df2)"
  }
}
```

### Active Element

```bash
doc pandas.DataFrame.merge --deprecation
```

Output:
```json
{
  "path": "pandas.DataFrame.merge",
  "deprecated": false,
  "version_info": {
    "added_in": "0.1",
    "last_modified": "2.1",
    "stable": true
  }
}
```

### Class Deprecation

```bash
doc pandas.SparseSeries --deprecation
```

Output:
```json
{
  "path": "pandas.SparseSeries",
  "deprecated": true,
  "deprecation_info": {
    "deprecated_in": "1.0",
    "removed_in": "2.0",
    "use_instead": "pandas.Series with sparse dtype",
    "reason": "SparseSeries is replaced by regular Series with sparse dtype"
  },
  "alternatives": [
    "pd.Series([], dtype='Sparse[int]')",
    "pd.Series_sparse([], dtype='Sparse[float]')"
  ]
}
```

## Compatibility Check

```bash
doc pandas.DataFrame --check-compat 3.0
```

Output:
```json
{
  "target_version": "3.0",
  "compatibility": "partial",
  "issues": [
    {
      "member": "append",
      "problem": "removed_in",
      "version": "3.0",
      "suggestion": "Use pd.concat() instead"
    },
    {
      "member": ".ix",
      "problem": "removed_in",
      "version": "1.0",
      "suggestion": "Use .loc or .iloc"
    }
  ],
  "safe_to_use": [
    "merge",
    "groupby",
    "sort_values"
  ]
}
```

## Version Information Sources

### From Docstrings

```python
def old_function():
    """
    .. deprecated:: 2.0
       Use new_function() instead.
    """
```

### From Decorators

```python
from docs_cli import metadata

@metadata(
    deprecated=True,
    deprecated_in="2.0",
    removed_in="3.0",
    use_instead="new_package.new_function"
)
def old_function():
    pass
```

### From Comments

```python
# TODO: Remove in version 3.0 (deprecated in 2.0)
# Use new_function() instead
def old_function():
    pass
```

## Automatic Detection

### DeprecationWarning Decorator

```python
import warnings

@warnings.deprecated("Use new_function instead")
def old_function():
    pass
```

Detected by CLI:
```json
{
  "deprecated": true,
  "source": "decorator",
  "message": "Use new_function instead"
}
```

### Docstring Patterns

Patterns detected:
- `.. deprecated::`
- `.. versionchanged::`
- `DEPRECATED`
- `@deprecated`

## Use Cases for Agents

### Avoid Suggesting Deprecated Code

```python
# Agent: "How do I add rows to a DataFrame?"

Bad (without deprecation check):
1. doc pandas.DataFrame --search "add rows"
2. Finds append()
3. Suggests: df.append(new_row)  # Deprecated!

Good (with deprecation check):
1. doc pandas.DataFrame.append --deprecation
2. Sees deprecated in 2.0
3. Suggests: pd.concat([df, new_row])  # Current best practice
```

### Migration Assistance

```python
# Agent: "Migrate this code from pandas 1.5 to 2.0"

1. doc pandas.DataFrame --check-compat 2.0
2. Identifies all deprecated usage
3. Generates migration script automatically
4. "Your code uses DataFrame.append, deprecated in 2.0. Replacing with pd.concat()..."
```

### Version-Aware Recommendations

```python
# Agent: "Suggest code for pandas 2.0"

1. User specifies target version
2. Agent checks deprecation for all suggestions
3. Only recommends non-deprecated APIs
4. "Note: In pandas 2.0, use .merge() instead of .append()"
```

### Library Upgrade Planning

```python
# Agent: "What breaks if I upgrade to pandas 3.0?"

1. doc pandas --check-compat 3.0
2. Returns all removed items
3. Agent can suggest migration plan
4. "Start by replacing .append() calls, then upgrade"
```

## Batch Depprecation Report

```bash
doc pandas --deprecation-report --output=deprecations.json
```

Output:
```json
{
  "pandas": "2.1.0",
  "scan_date": "2024-01-15",
  "deprecated_items": [
    {
      "path": "pandas.DataFrame.append",
      "deprecated_in": "2.0",
      "removed_in": "3.0",
      "urgency": "high"
    },
    {
      "path": "pandas.DataFrame.ix",
      "deprecated_in": "0.20",
      "removed_in": "1.0",
      "urgency": "critical"
    }
  ],
  "summary": {
    "total": 2,
    "removed_in_next": 1,
    "future_removal": 1
  }
}
```

## Urgency Levels

```bash
doc pandas.DataFrame.append --deprecation
```

Output includes urgency:
```json
{
  "deprecated": true,
  "removed_in": "3.0",
  "current_version": "2.1",
  "urgency": "medium",  # critical | high | medium | low | info
  "time_until_removed": "1 minor version",
  "recommendation": "Plan migration within next few releases"
}
```

### Urgency Criteria

- **critical**: Already removed in current stable
- **high**: Will be removed in next version
- **medium**: Will be removed in 2-3 versions
- **low**: Early deprecation warning
- **info**: Planned future deprecation

## Version History

```bash
doc pandas.DataFrame --version-history
```

Output:
```json
{
  "path": "pandas.DataFrame",
  "version_history": [
    {
      "version": "0.1",
      "changes": ["Initial release"]
    },
    {
      "version": "1.0",
      "changes": [
        "Added: merge() method",
        "Removed: ix[] indexer"
      ]
    },
    {
      "version": "2.0",
      "changes": [
        "Deprecated: append() method",
        "Changed: default value of 'copy' parameter"
      ]
    }
  ]
}
```

## Semantic Versioning

For packages following semver:

```bash
doc mypackage --semver 2.1.0
```

Checks compatibility with semantic versioning rules:
```json
{
  "package_version": "2.1.0",
  "requested": "2.1.0",
  "compatible": true,
  "breaking_changes": [],
  "api_changes": [
    "Added: new_process() function"
  ]
}
```

## Integration with Dependency Management

```bash
# Check all dependencies for deprecations
doc . --check-deps
```

Scans `requirements.txt` or `pyproject.toml`:
```json
{
  "dependencies": [
    {
      "name": "pandas",
      "version": "2.0.3",
      "deprecated_items": 5,
      "upgrade_available": "2.1.0"
    },
    {
      "name": "numpy",
      "version": "1.20.0",
      "deprecated_items": 0,
      "upgrade_available": "1.24.0"
    }
  ]
}
```
