# Source Diff / Change Detection

Compare different versions of code elements to understand what changed.

## Usage

```bash
doc <element> --diff <version_range>
doc <element> --diff <commit1>..<commit2>
doc <element> --diff --git HEAD~5
```

## Examples

### Version Comparison

```bash
doc pandas.DataFrame.merge --diff v1.5.0..v2.0.0
```

Output:
```json
{
  "path": "pandas.DataFrame.merge",
  "versions": {
    "from": "v1.5.0",
    "to": "v2.0.0"
  },
  "changes": [
    {
      "type": "parameter_added",
      "name": "validate",
      "default": null,
      "description": "Validate the merge keys on uniqueness"
    },
    {
      "type": "parameter_changed",
      "name": "how",
      "old": "str",
      "new": "Literal['inner', 'outer', 'left', 'right', 'cross']",
      "reason": "Stricter type checking"
    },
    {
      "type": "parameter_renamed",
      "old_name": "left_index",
      "new_name": "left_on_index",
      "deprecated": true
    },
    {
      "type": "docstring_updated",
      "old": "Merge DataFrame objects...",
      "new": "Merge DataFrame or named Series objects...",
      "reason": "Added Series support"
    }
  ],
  "breaking": false,
  "migration_notes": [
    "left_index still works but is deprecated",
    "New validate parameter can affect behavior in edge cases"
  ]
}
```

### Git Commit Comparison

```bash
doc mymodule.process --diff abc123..def456
```

Output:
```json
{
  "path": "mypackage.mymodule.process",
  "commits": {
    "from": "abc123",
    "to": "def456"
  },
  "changes": [
    {
      "type": "implementation_changed",
      "diff": "-    if condition:\n-        return old_way()\n+    if condition:\n+        return new_way()",
      "location": "line 45-47"
    },
    {
      "type": "exception_added",
      "exception": "ValueError",
      "condition": "when data is empty",
      "reason": "Better error handling"
    }
  ]
}
```

### Signature Change Detection

```bash
doc pandas.DataFrame.__init__ --diff v2.0..v2.1
```

Output:
```json
{
  "signature_changes": {
    "old": {
      "parameters": [
        {"name": "data", "type": "Any | None"},
        {"name": "index", "type": "Index | None"}
      ]
    },
    "new": {
      "parameters": [
        {"name": "data", "type": "Any | None"},
        {"name": "index", "type": "Index | Sequence | None"},
        {"name": "dtype", "type": "Dtype | None", "added": true}
      ]
    },
    "compatible": true,
    "backwards_compatible": true
  }
}
```

### Class Structure Changes

```bash
doc pandas.DataFrame --diff v1.0..v2.0
```

Output:
```json
{
  "path": "pandas.DataFrame",
  "structural_changes": [
    {
      "type": "method_added",
      "name": "explode",
      "description": "Transform each element into a row"
    },
    {
      "type": "method_removed",
      "name": "ix",
      "reason": "Deprecated in favor of loc/iloc",
      "replacement": "Use .loc or .iloc"
    },
    {
      "type": "inheritance_changed",
      "old_base": ["pandas.generic.NDFrame"],
      "new_base": ["pandas.core.frame.FrameBase"]
    },
    {
      "type": "property_changed",
      "name": "columns",
      "old_type": "Index",
      "new_type": "Index (immutable)"
    }
  ]
}
```

## Change Types

### Signature Changes
- `parameter_added` - New parameter added
- `parameter_removed` - Parameter removed (breaking)
- `parameter_changed` - Type or default changed
- `parameter_renamed` - Parameter renamed
- `return_type_changed` - Return type changed

### Behavioral Changes
- `implementation_changed` - Logic changed without signature change
- `exception_added` - New exception raised
- `exception_removed` - No longer raises exception
- `performance_changed` - Performance characteristics changed

### Documentation Changes
- `docstring_updated` - Docstring modified
- `docstring_added` - Previously undocumented
- `examples_added` - New usage examples

### Structural Changes
- `method_added` - New method in class
- `method_removed` - Method removed from class
- `inheritance_changed` - Base classes changed
- `moved` - Element moved to different location

## Breaking Change Detection

```bash
doc pandas --diff v1.5..v2.0 --breaking-only
```

Output:
```json
{
  "breaking_changes": [
    {
      "element": "pandas.DataFrame.ix",
      "type": "method_removed",
      "reason": "Removed in favor of loc/iloc",
      "migration": "Replace df.ix[...] with df.loc[...] or df.iloc[...]"
    },
    {
      "element": "pandas.read_csv",
      "type": "parameter_changed",
      "parameter": "squeeze",
      "old": "bool",
      "new": "bool | None",
      "breaking": true,
      "reason": "Default value changed from True to None"
    }
  ]
}
```

## Diff Formats

### Summary

```bash
doc pandas.DataFrame --diff v1.5..v2.0 --summary
```

Output:
```json
{
  "summary": {
    "total_changes": 5,
    "breaking": 1,
    "additions": 3,
    "removals": 1,
    "modified": 1
  }
}
```

### Unified Diff

```bash
doc mymodule.process --diff HEAD~1 --unified
```

Output standard unified diff format:
```diff
--- a/mypackage/mymodule.py
+++ b/mypackage/mymodule.py
@@ -42,7 +42,9 @@ def process(data):
         if not data:
-            return None
+            raise ValueError("Data cannot be empty")
+
+        result = transform(data)
```

### Markdown Diff

```bash
doc mymodule.process --diff HEAD~1 --markdown
```

Output formatted as Markdown with changes highlighted.

## Use Cases for Agents

### Migration Assistance

```python
# Agent: "Migrate code from pandas 1.5 to 2.0"

1. User provides code using pandas 1.5
2. Agent checks all used functions:
   doc pandas.DataFrame.merge --diff v1.5..v2.0
   doc pandas.DataFrame.ix --diff v1.5..v2.0
3. Identifies breaking changes
4. Generates migrated code
5. "Replaced df.ix with df.loc, updated merge() parameters"
```

### Understanding Changes

```python
# Agent: "What changed in version 2.0?"

1. doc pandas --diff v1.5..v2.0 --summary
2. Gets overview of changes
3. User asks about specific change
4. Agent explains: "DataFrame.merge now has a validate parameter"
```

### Debugging Version Issues

```python
# Agent: "My code broke after upgrade"

User: "It worked in pandas 1.5 but fails in 2.0"

1. Agent analyzes failing function
2. doc pandas.DataFrame.func --diff v1.5..v2.0
3. Finds breaking change
4. "In 2.0, this function raises ValueError when input is empty"
```

### Release Notes Generation

```python
# Agent: "Generate release notes"

1. Scan all changes between versions
2. doc mypackage --diff v1.0..v2.0
3. Categorize changes (features, fixes, breaking)
4. Generate formatted release notes
5. "## Breaking Changes\n\n- DataFrame.ix removed..."
```

### Dependency Updates

```python
# Agent: "Check if I can upgrade pandas"

1. Check user's code for pandas usage
2. For each used element, check diff
3. Identify potential issues
4. "You use DataFrame.ix which is removed in 2.0. Replace it first."
```

## Working with Git

### Compare with Git

```bash
cd /path/to/repo
doc mymodule.process --diff --git HEAD~5
```

Compares current version with 5 commits ago.

### Compare Branches

```bash
doc mymodule.process --diff --git main..feature-branch
```

### Compare with Staged Changes

```bash
doc mymodule.process --diff --git --staged
```

### Diff Working Directory

```bash
doc mymodule.process --diff --git --working-dir
```

## Batch Diff

```bash
doc mypackage --diff v1.0..v2.0 --output diff_report.json
```

Output:
```json
{
  "package": "mypackage",
  "versions": {"from": "v1.0", "to": "v2.0"},
  "elements": {
    "mymodule.process": {...},
    "mymodule.transform": {...}
  },
  "summary": {
    "total_elements": 25,
    "changed_elements": 12,
    "breaking_changes": 3
  }
}
```

## Visual Diff

```bash
doc mymodule.process --diff HEAD~1 --visual --output diff.html
```

Generates HTML with side-by-side comparison and syntax highlighting.

## Ignoring Changes

```bash
doc mypackage --diff v1.0..v2.0 --ignore docstring --ignore whitespace
```

Only show significant changes, not documentation or formatting.

## Change Impact Analysis

```bash
doc pandas.DataFrame --diff v1.5..v2.0 --impact
```

Output:
```json
{
  "impact_analysis": {
    "api_surface_changed": "low",
    "breaking_changes": 1,
    "affected_methods": 15,
    "users_affected": "high",
    "migration_effort": "medium",
    "estimated_migration_time": "2-4 hours for typical codebase"
  }
}
```

## Reverse Diff

```bash
doc pandas.DataFrame --diff v2.0..v1.5 --reverse
```

Shows what needs to be done to downgrade from 2.0 to 1.5.
