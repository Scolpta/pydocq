# Documentation Index / Pre-computed Cache

Generate pre-computed indexes for instant package documentation access.

## Usage

```bash
# Build an index
doc-index build pandas --output pandas.docs-index

# Use index for queries
doc pandas.DataFrame --use-index pandas.docs-index

# Update existing index
doc-index update pandas.docs-index
```

## Examples

### Build Index

```bash
doc-index build pandas --output pandas.docs-index
```

Output:
```json
{
  "package": "pandas",
  "version": "2.1.0",
  "indexed_at": "2024-01-15T10:30:00Z",
  "elements_count": 5234,
  "index_size": "2.3 MB",
  "build_time_ms": 15420
}
```

### Query with Index

```bash
doc pandas.DataFrame --use-index pandas.docs-index
```

Returns instant results without importing pandas:
```json
{
  "path": "pandas.DataFrame",
  "type": "class",
  "docstring": "...",
  "members": [...]
}
```

Query time: ~5ms vs ~500ms with import.

### Incremental Update

```bash
doc-index update pandas.docs-index
```

Only re-indexes changed files:
```json
{
  "previous_build": "2024-01-14T10:00:00Z",
  "changed_files": 23,
  "update_time_ms": 1200
}
```

### Index Specific Modules

```bash
doc-index build pandas.core.frame --output frame.docs-index
```

Index only specific module for smaller footprint.

### Index with Custom Options

```bash
doc-index build pandas \
  --output pandas.docs-index \
  --include-source \
  --include-relationships \
  --include-examples \
  --compress
```

Options:
- `--include-source`: Include source code in index
- `--include-relationships`: Build call graph and inheritance
- `--include-examples`: Extract and index examples
- `--compress`: Use compression for smaller size

## Index Format

### Structure

```json
{
  "metadata": {
    "package": "pandas",
    "version": "2.1.0",
    "indexed_at": "2024-01-15T10:30:00Z",
    "format_version": "1.0"
  },
  "elements": {
    "pandas.DataFrame": {
      "type": "class",
      "docstring": "...",
      "source_file": "pandas/core/frame.py",
      "line": 123,
      "members": ["__init__", "merge", "groupby", ...],
      "metadata": {...}
    },
    "pandas.DataFrame.merge": {
      "type": "method",
      "signature": {...},
      "docstring": "...",
      "examples": [...],
      "metadata": {...}
    },
    ...
  },
  "relationships": {
    "pandas.DataFrame": {
      "inherits_from": ["pandas.generic.NDFrame"],
      "inherited_by": [...],
      "calls": [...],
      "called_by": [...]
    },
    ...
  },
  "search_index": {
    "names": [...],
    "docstrings": [...],
    "keywords": [...]
  },
  "categories": {
    "visualization": [...],
    "io": [...],
    ...
  }
}
```

### Binary Format

For better performance, use binary format:

```bash
doc-index build pandas --output pandas.docs-index --format binary
```

Creates compact binary format with faster random access.

## Index Management

### List Indexed Packages

```bash
doc-index list
```

Output:
```json
{
  "indexes": [
    {
      "path": "pandas.docs-index",
      "package": "pandas",
      "version": "2.1.0",
      "size": "2.3 MB",
      "indexed_at": "2024-01-15T10:30:00Z"
    },
    {
      "path": "numpy.docs-index",
      "package": "numpy",
      "version": "1.24.0",
      "size": "1.8 MB",
      "indexed_at": "2024-01-14T15:20:00Z"
    }
  ]
}
```

### Index Info

```bash
doc-index info pandas.docs-index
```

Output:
```json
{
  "package": "pandas",
  "version": "2.1.0",
  "indexed_at": "2024-01-15T10:30:00Z",
  "build_time_ms": 15420,
  "elements": {
    "total": 5234,
    "classes": 234,
    "functions": 4521,
    "methods": 479
  },
  "size": {
    "compressed": "2.3 MB",
    "uncompressed": "8.7 MB"
  },
  "includes": ["source", "relationships", "examples", "metadata"]
}
```

### Validate Index

```bash
doc-index validate pandas.docs-index
```

Checks index integrity:
```json
{
  "valid": true,
  "errors": [],
  "warnings": [
    "Element pandas.OldClass not found in current version"
  ]
}
```

### Merge Indexes

```bash
doc-index merge pandas.docs-index numpy.docs-index --output combined.docs-index
```

Combines multiple indexes into one for unified queries.

### Remove Index

```bash
doc-index remove pandas.docs-index
```

Deletes index file.

## Use Cases for Agents

### Instant Package Loading

```python
# Agent: "Tell me about pandas"

1. Load index: pandas.docs-index (2.3 MB)
2. Takes ~50ms to load
3. No import, no dependencies
4. Has full documentation in memory
5. Can answer queries instantly
```

### Offline Documentation

```python
# Agent working without internet

1. Pre-load indexes for common packages
2. pandas.docs-index, numpy.docs-index, etc.
3. Can provide documentation offline
4. No need to install packages
```

### Quick Search

```python
# Agent: "Find all functions related to CSV"

1. Search in index: pandas.docs-index
2. Uses pre-built search index
3. Results in ~5ms
4. "read_csv, to_csv, read_csv_chunked, ..."
```

### Version Comparison

```python
# Agent: "What changed between pandas 1.5 and 2.0?"

1. Load both indexes
2. pandas-1.5.docs-index, pandas-2.0.docs-index
3. Compare element by element
4. Report differences
```

### Distribution

Share indexes with other agents:
```json
{
  "agent": {
    "name": "code-assistant",
    "documentation_indexes": [
      "https://example.com/indexes/pandas.docs-index",
      "https://example.com/indexes/numpy.docs-index"
    ]
  }
}
```

Agents download and use pre-built indexes.

## Index Synchronization

### Auto-Update

```bash
doc-index watch pandas.docs-index
```

Watches package for changes and auto-updates index.

### Scheduled Updates

```bash
doc-index schedule pandas.docs-index --daily
```

Updates index daily.

### Remote Indexes

```bash
doc-index download pandas --from https://example.com/indexes
```

Downloads pre-built index from remote server.

```bash
doc-index upload pandas.docs-index --to https://example.com/indexes
```

Uploads index for sharing.

## Index Queries

### Search in Index

```bash
doc-index search pandas.docs-index "merge"
```

Searches within pre-built index without loading.

### Filter in Index

```bash
doc-index filter pandas.docs-index --category visualization
```

Filters elements by category using index metadata.

### Export from Index

```bash
doc-index export pandas.docs-index --format json --output pandas-doc.json
```

Exports index to JSON for external tools.

### Import to Index

```bash
doc-index import pandas-doc.json --output pandas.docs-index
```

Creates index from external JSON.

## Index Optimization

### Compress Index

```bash
doc-index optimize pandas.docs-index --compress
```

Reduces index size with compression:
```json
{
  "before": "8.7 MB",
  "after": "2.3 MB",
  "compression_ratio": "73.5%"
}
```

### Prune Index

```bash
doc-index optimize pandas.docs-index --prune-private
```

Removes private elements from index:
```json
{
  "before": 5234,
  "after": 3842,
  "removed": 1392,
  "removed_type": "private (_prefix)"
}
```

### Compact Index

```bash
doc-index optimize pandas.docs-index --compact
```

Removes unused data and reorganizes for faster access.

## Index Statistics

```bash
doc-index stats pandas.docs-index
```

Output:
```json
{
  "package": "pandas",
  "elements": {
    "classes": 234,
    "functions": 4521,
    "methods": 479,
    "total": 5234
  },
  "coverage": {
    "with_docstring": 5102 (97.5%),
    "with_metadata": 1234 (23.6%),
    "with_examples": 2341 (44.7%),
    "deprecated": 45 (0.9%)
  },
  "relationships": {
    "inheritance_links": 456,
    "call_links": 12456
  },
  "search_index": {
    "terms": 45678,
    "unique_terms": 12345
  }
}
```

## Index Versioning

### Version Tracking

```bash
doc-index build pandas --output pandas.docs-index --version-tag v2.1.0
```

Tags index with package version.

### Compare Index Versions

```bash
doc-index diff pandas-2.0.docs-index pandas-2.1.docs-index
```

Shows differences between versions.

## Multi-Package Index

```bash
doc-index build \
  pandas \
  numpy \
  matplotlib \
  --output scipy-stack.docs-index
```

Creates single index for multiple packages.

Query across packages:
```bash
doc --use-index scipy-stack.docs-index --query "DataFrame.merge"
```

## Index Caching

### Memory Cache

```python
from docs_cli import load_index

# Load index once
index = load_index("pandas.docs-index")

# Reuse for multiple queries
df_info = index.get("pandas.DataFrame")
merge_info = index.get("pandas.DataFrame.merge")
```

### LRU Cache

```bash
doc --use-index pandas.docs-index --cache-size 100
```

Keeps last 100 queries in memory.

## Index Formats

### JSON Format

Human-readable, debuggable:
```bash
doc-index build pandas --format json
```

### Binary Format

Fast, compact:
```bash
doc-index build pandas --format binary
```

### SQLite Format

Queryable with SQL:
```bash
doc-index build pandas --format sqlite
```

Allows SQL queries on documentation:
```bash
sqlite3 pandas.docs-index.db "SELECT * FROM elements WHERE type='class'"
```

## Index Security

### Signature

```bash
doc-index build pandas --sign
```

Adds cryptographic signature to index.

```bash
doc-index verify pandas.docs-index
```

Verifies index signature.

### Encryption

```bash
doc-index build pandas --encrypt
```

Encrypts index with agent's key.

## Index API

```python
from docs_cli.index import Index

# Load index
index = Index.load("pandas.docs-index")

# Query
df = index.get("pandas.DataFrame")

# Search
results = index.search("merge")

# Filter
vis_funcs = index.filter(category="visualization")

# Relationships
calls = index.get_calls("pandas.DataFrame.__init__")

# Export
index.export_json("output.json")
```

Programmatic access to index for agents.
