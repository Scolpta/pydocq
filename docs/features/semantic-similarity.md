# Semantic Similarity

Find semantically similar code elements to discover alternatives and understand relationships.

## Usage

```bash
doc <element> --similar
doc <package> --similar --to <query>
```

## Examples

### Find Similar Functions

```bash
doc pandas.DataFrame.merge --similar
```

Output:
```json
{
  "path": "pandas.DataFrame.merge",
  "similar_to": [
    {
      "path": "pandas.DataFrame.join",
      "similarity": 0.92,
      "type": "method",
      "reasons": [
        "Both combine DataFrames",
        "Both handle key-based matching",
        "Both support inner/outer/left/right joins"
      ],
      "differences": [
        "join() uses index by default",
        "merge() is more flexible with column specification"
      ]
    },
    {
      "path": "pandas.concat",
      "similarity": 0.85,
      "type": "function",
      "reasons": [
        "Combines multiple DataFrames",
        "Handles axis parameter",
        "Supports different join types"
      ],
      "differences": [
        "concat() stacks data along axis",
        "merge() matches on keys/columns"
      ]
    },
    {
      "path": "pandas.DataFrame.append",
      "similarity": 0.78,
      "type": "method",
      "reasons": ["Adds rows to DataFrame"],
      "differences": [
        "append() only adds rows",
        "append() is deprecated (use concat instead)"
      ],
      "deprecated": true
    }
  ]
}
```

### Find Similar by Query

```bash
doc pandas --similar --to "filter rows by condition"
```

Output:
```json
{
  "query": "filter rows by condition",
  "matches": [
    {
      "path": "pandas.DataFrame.query",
      "similarity": 0.95,
      "reason": "Filter rows using expression string",
      "example": "df.query('age > 18')"
    },
    {
      "path": "pandas.DataFrame.loc",
      "similarity": 0.89,
      "reason": "Label-based indexing for filtering",
      "example": "df.loc[df['age'] > 18]"
    },
    {
      "path": "pandas.DataFrame.__getitem__",
      "similarity": 0.82,
      "reason": "Boolean indexing",
      "example": "df[df['age'] > 18]"
    },
    {
      "path": "pandas.DataFrame.filter",
      "similarity": 0.65,
      "reason": "Filters items (columns or rows) by labels",
      "note": "Different from boolean indexing"
    }
  ]
}
```

### Find Similar Classes

```bash
doc pandas.Series --similar
```

Output:
```json
{
  "path": "pandas.Series",
  "similar_to": [
    {
      "path": "pandas.DataFrame",
      "similarity": 0.88,
      "reasons": [
        "Both are data structures",
        "Share similar methods (groupby, sort_values, etc.)",
        "Both support indexing and slicing"
      ],
      "differences": [
        "Series is 1D, DataFrame is 2D",
        "Series represents single column, DataFrame multiple columns"
      ]
    },
    {
      "path": "numpy.ndarray",
      "similarity": 0.75,
      "reasons": [
        "Both are array-like",
        "Support vectorized operations",
        "Used for numerical data"
      ],
      "differences": [
        "Series has labeled index",
        "Series supports mixed types",
        "Series has more methods"
      ]
    }
  ]
}
```

### Find Replacements for Deprecated

```bash
doc pandas.DataFrame.ix --similar
```

Output:
```json
{
  "path": "pandas.DataFrame.ix",
  "deprecated": true,
  "replacements": [
    {
      "path": "pandas.DataFrame.loc",
      "similarity": 0.95,
      "use_case": "Label-based indexing",
      "migration": "Replace df.ix[row] with df.loc[row]"
    },
    {
      "path": "pandas.DataFrame.iloc",
      "similarity": 0.93,
      "use_case": "Position-based indexing",
      "migration": "Replace df.ix[pos] with df.iloc[pos]"
    }
  ]
}
```

## Similarity Computation

### Text-Based Similarity

Compares names and docstrings:

```bash
doc mymodule.process_data --similar --by text
```

Uses NLP techniques:
- TF-IDF vectorization
- Cosine similarity
- Word embeddings

### Signature-Based Similarity

Compares function signatures:

```bash
doc mymodule.process_data --similar --by signature
```

Compares:
- Parameter names and types
- Return types
- Parameter count

### Usage-Based Similarity

Analyzes actual usage patterns:

```bash
doc mymodule.process_data --similar --by usage
```

Looks at:
- Common call patterns
- Parameter combinations
- Context in which it's used

### Structural Similarity

For classes and modules:

```bash
doc pandas.DataFrame --similar --by structure
```

Compares:
- Methods and properties
- Inheritance hierarchy
- Relationships to other elements

## Similarity Metrics

### Overall Similarity Score

```json
{
  "similarity": 0.92,
  "confidence": "high",
  "factors": {
    "text_similarity": 0.88,
    "signature_similarity": 0.95,
    "semantic_similarity": 0.91
  }
}
```

### Aspect-Based Similarity

```bash
doc pandas.DataFrame.merge --similar --breakdown
```

Output:
```json
{
  "aspects": {
    "purpose": 0.95,
    "parameters": 0.82,
    "behavior": 0.88,
    "use_cases": 0.91
  },
  "overall": 0.89
}
```

## Use Cases for Agents

### Discovering Alternatives

```python
# Agent: "What are alternatives to df.merge()?"

1. doc pandas.DataFrame.merge --similar
2. Gets similar functions: join, concat
3. Explains differences
4. "join() is simpler for index-based merging, concat() for stacking"
```

### Finding Unknown Features

```python
# Agent: "I want to filter rows"

1. doc pandas --similar --to "filter rows"
2. Gets list: query, loc, __getitem__, filter
3. Explains each
4. "For boolean conditions, use query() or boolean indexing"
5. "For label-based selection, use loc"
```

### Understanding Relationships

```python
# Agent: "How are Series and DataFrame related?"

1. doc pandas.Series --similar
2. Sees DataFrame in similar list
3. Explains relationship
4. "Series is like a single-column DataFrame"
5. "They share many methods through common base class"
```

### Migration Assistance

```python
# Agent: "I used df.ix, what now?"

1. doc pandas.DataFrame.ix --similar
2. Gets replacements: loc, iloc
3. Explains which to use based on usage pattern
4. "If you used labels: switch to loc"
5. "If you used positions: switch to iloc"
```

### API Exploration

```python
# Agent: "What else can I do with DataFrames?"

1. doc pandas.DataFrame --similar --to "data transformation"
2. Discovers: transform, apply, map, agg
3. Explains each
4. Helps user choose right tool
```

### Code Review

```python
# Agent: "Review my code"

Sees: user using append() in loop.

1. doc pandas.DataFrame.append --similar
2. Sees concat with higher similarity and not deprecated
3. Suggests: "Use concat([df1, df2]) instead of repeated append()"
4. Explains why: "concat is more efficient and not deprecated"
```

## Similarity Thresholds

```bash
doc pandas.DataFrame.merge --similar --min-similarity 0.8
```

Only show results with similarity >= 0.8.

## Similarity by Category

```bash
doc pandas --similar --category "data aggregation"
```

Output:
```json
{
  "category": "data aggregation",
  "matches": [
    {"path": "pandas.DataFrame.agg", "relevance": 0.95},
    {"path": "pandas.DataFrame.groupby", "relevance": 0.92},
    {"path": "pandas.core.window.Rolling.mean", "relevance": 0.87}
  ]
}
```

## Bidirectional Similarity

```bash
doc pandas.DataFrame.merge pandas.DataFrame.join --compare
```

Output:
```json
{
  "comparison": {
    "merge": {
      "similar_to": ["join", "concat", "append"]
    },
    "join": {
      "similar_to": ["merge", "concat"]
    },
    "mutual_similarity": 0.92,
    "key_differences": [
      "merge() specifies columns, join() uses index",
      "join() is more concise for simple cases"
    ]
  }
}
```

## Similarity Graph

```bash
doc pandas.DataFrame --similar --graph --output similarity.html
```

Generates interactive graph showing relationships between similar elements.

## Learning from User Feedback

```bash
doc pandas.DataFrame.merge --similar --feedback
```

Interactive mode where user provides feedback:

```
Found similar functions:
1. join (0.92)
2. concat (0.85)

Is concat relevant for "combine dataframes"? (y/n)
> y

Recorded: concat is relevant for "combine dataframes" query
```

Improves future similarity recommendations.

## Context-Aware Similarity

```bash
doc pandas.DataFrame --similar --context "I have time series data"
```

Output prioritizes time-series related functions:
```json
{
  "context": "time series data",
  "matches": [
    {"path": "pandas.DataFrame.resample", "relevance": 0.95},
    {"path": "pandas.DataFrame.rolling", "relevance": 0.92},
    {"path": "pandas.DataFrame.shift", "relevance": 0.88}
  ]
}
```

## Cross-Package Similarity

```bash
doc pandas.DataFrame --similar --across-packages
```

Finds similar structures in other packages:
```json
{
  "similar_in_other_packages": [
    {
      "package": "polars",
      "element": "polars.DataFrame",
      "similarity": 0.85
    },
    {
      "package": "dask",
      "element": "dask.dataframe.DataFrame",
      "similarity": 0.82
    }
  ]
}
```
