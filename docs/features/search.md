# Search Across Package

Discover elements by searching across entire packages with flexible criteria.

## Usage

```bash
doc <package> --search <query>
doc <package> --search --filter <criteria>
```

## Examples

### Search by Docstring Content

```bash
doc pandas --search "missing data"
```

Output:
```json
{
  "query": "missing data",
  "matches": [
    {
      "path": "pandas.DataFrame.dropna",
      "type": "method",
      "relevance": 0.95,
      "context": "Remove missing values"
    },
    {
      "path": "pandas.DataFrame.fillna",
      "type": "method",
      "relevance": 0.92,
      "context": "Fill NA/NaN values"
    },
    {
      "path": "pandas.isna",
      "type": "function",
      "relevance": 0.89,
      "context": "Detect missing values"
    }
  ]
}
```

### Search by Category/Metadata

```bash
doc pandas --search "category:visualization"
```

Output:
```json
{
  "query": "category:visualization",
  "matches": [
    {
      "path": "pandas.DataFrame.plot",
      "type": "method",
      "metadata": {"category": "visualization"}
    },
    {
      "path": "pandas.plotting.hist",
      "type": "function",
      "metadata": {"category": "visualization"}
    }
  ]
}
```

### Search by Decorator

```bash
doc flask --search "decorator:route"
```

Output:
```json
{
  "query": "decorator:route",
  "matches": [
    {
      "path": "flask.Flask.route",
      "type": "method",
      "decorators": ["@route"]
    }
  ]
}
```

### Search by Parameter Type

```bash
doc pandas --search "param:DataFrame"
```

Output:
```json
{
  "query": "param:DataFrame",
  "matches": [
    {
      "path": "pandas.concat",
      "type": "function",
      "params": [
        {"name": "objs", "type": "Iterable[DataFrame] | DataFrame"}
      ],
      "match_reason": "Accepts DataFrame parameter"
    },
    {
      "path": "pandas.merge",
      "type": "function",
      "params": [
        {"name": "left", "type": "DataFrame"},
        {"name": "right", "type": "DataFrame"}
      ]
    }
  ]
}
```

### Search by Return Type

```bash
doc pandas --search "returns:DataFrame"
```

Output:
```json
{
  "query": "returns:DataFrame",
  "matches": [
    {
      "path": "pandas.read_csv",
      "type": "function",
      "returns": "DataFrame"
    },
    {
      "path": "pandas.DataFrame.sort_values",
      "type": "method",
      "returns": "DataFrame"
    }
  ]
}
```

## Search Operators

### Text Search

```bash
doc pandas --search "group by"          # Phrase search
doc pandas --search "group AND by"      # AND operator
doc pandas --search "merge OR join"     # OR operator
doc pandas --search "filter NOT drop"   # NOT operator
```

### Field-Specific Search

```bash
doc pandas --search "name:group*"       # Wildcard on name
doc pandas --search "docstring:time*"   # In docstring
doc pandas --search "type:function"     # By type
```

### Comparison

```bash
doc pandas --search "complexity:>10"    # Cyclomatic complexity > 10
doc pandas --search "params:>3"         # More than 3 parameters
doc pandas --search "deprecated:true"   # Only deprecated items
```

## Search Filters

### By Element Type

```bash
doc pandas --search --filter "type:class"
doc pandas --search --filter "type:function"
doc pandas --search --filter "type:method"
```

### By Visibility

```bash
doc pandas --search --filter "public"       # Public only
doc pandas --search --filter "private"      # Private only (_prefix)
doc pandas --search --filter "all"          # Everything
```

### By Deprecation

```bash
doc pandas --search --filter "deprecated:true"
doc pandas --search --filter "stable:true"
```

### By Complexity

```bash
doc pandas --search --filter "complexity:low"    # complexity < 5
doc pandas --search --filter "complexity:medium" # complexity 5-10
doc pandas --search --filter "complexity:high"   # complexity > 10
```

## Combined Search

```bash
doc pandas --search "filter" --filter "type:function" --filter "deprecated:false"
```

Output:
```json
{
  "query": "filter",
  "filters": ["type:function", "deprecated:false"],
  "matches": [
    {
      "path": "pandas.DataFrame.filter",
      "type": "function",
      "deprecated": false
    }
  ]
}
```

## Fuzzy Search

```bash
doc pandas --search "merg" --fuzzy
```

Output:
```json
{
  "query": "merg",
  "fuzzy": true,
  "matches": [
    {
      "path": "pandas.merge",
      "type": "function",
      "distance": 0
    },
    {
      "path": "pandas.DataFrame.merge",
      "type": "method",
      "distance": 0
    },
    {
      "path": "pandas.core.merge.merge_ordered",
      "type": "function",
      "distance": 2
    }
  ]
}
```

## Search in Specific Module

```bash
doc pandas.core.frame --search "column"
```

Output:
```json
{
  "scope": "pandas.core.frame",
  "query": "column",
  "matches": [
    {"path": "pandas.DataFrame.columns", "type": "property"},
    {"path": "pandas.DataFrame.rename_column", "type": "method"}
  ]
}
```

## Output Formats

### Summary (default)

```bash
doc pandas --search "aggregate"
```

### Detailed

```bash
doc pandas --search "aggregate" --detailed
```

Output includes full metadata for each match.

### Count Only

```bash
doc pandas --search "aggregate" --count
# Output: 15 matches
```

### Paths Only

```bash
doc pandas --search "aggregate" --paths-only
# Output:
# pandas.DataFrame.agg
# pandas.core.groupby.GroupBy.agg
# pandas.core.window.Rolling.aggregate
```

## Use Cases for Agents

### Discovering Unknown APIs

```python
# Agent: "How do I handle missing values in pandas?"

1. doc pandas --search "missing values"
2. Gets list: dropna, fillna, isna, notna
3. Agent can explore each: doc pandas.DataFrame.dropna
4. Synthesizes recommendations
```

### Finding Design Patterns

```python
# Agent: "Find all caching functions"

1. doc myproject --search "decorator:cache"
2. Gets all @cache decorated functions
3. Agent understands caching strategy
4. Can suggest where to add caching
```

### Refactoring Support

```python
# Agent: "Find all functions that process DataFrames"

1. doc pandas --search "param:DataFrame"
2. Returns all functions accepting DataFrames
3. Agent identifies processing pipeline
4. Can suggest refactoring patterns
```

### Alternative Discovery

```python
# Agent: "What are alternatives to deprecated append?"

1. doc pandas --search "returns:DataFrame" --filter "type:function"
2. Finds all DataFrame-returning functions
3. Agent filters for similar functionality
4. Suggests: concat, merge, join
```

### Category-Based Discovery

```python
# Agent: "Show me all visualization functions"

1. User has metadata on functions:
   @metadata(category="visualization")

2. doc myproject --search "category:visualization"
3. Agent gets organized list by category
4. Can explain entire visualization API
```

## Search Performance

### Indexing

For large packages, CLI builds search index:

```bash
doc pandas --build-index
# Index saved to: .docs-cli/pandas.index
```

Subsequent searches use index:

```bash
doc pandas --search "merge" --use-index
# Much faster
```

### Incremental Search

```bash
doc pandas --search --interactive
# Interactive search mode
# Type query, see results instantly
```

## Search Statistics

```bash
doc pandas --search --stats
```

Output:
```json
{
  "package": "pandas",
  "indexed_elements": 5234,
  "searchable_fields": [
    "name",
    "docstring",
    "parameters",
    "return_type",
    "metadata"
  ],
  "last_indexed": "2024-01-15T10:30:00Z"
}
```

## Batch Search

```bash
doc pandas --search --batch queries.txt --output results.json
```

File `queries.txt`:
```
missing data
group by
merge
join
```

Output:
```json
{
  "missing data": {...},
  "group by": {...},
  "merge": {...},
  "join": {...}
}
```

## Search History

```bash
doc pandas --search --history
```

Output:
```json
{
  "recent_searches": [
    "missing data",
    "category:visualization",
    "param:DataFrame"
  ]
}
```

Re-run previous search:
```bash
doc pandas --search --repeat 1  # Run first search from history
```

## See Also

- **[Discovery](./discovery.md)** - List package contents (simpler, good for overview)
- **[Query Language](./query-language.md)** - More powerful SQL-like queries
- **[Semantic Similarity](./semantic-similarity.md)** - Find similar elements by meaning, not just text
- **[Category Decorator](./sdk-category.md)** - Add categories to elements for better search
- **[Tag Decorator](./sdk-tag.md)** - Add tags for flexible filtering
