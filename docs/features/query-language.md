# Query Language for Documentation

Powerful query language for searching and filtering documentation.

## Usage

```bash
doc pandas --query "functions where param:DataFrame and returns:DataFrame and not deprecated"
doc pandas --query "classes where methods > 10 and category:visualization"
doc pandas --query "functions where calls contains DataFrame.groupby"
```

## Examples

### Basic Queries

#### Find by Type

```bash
doc pandas --query "classes"
```

Output: All classes in pandas.

```bash
doc pandas --query "functions"
```

Output: All functions.

#### Find by Parameter Type

```bash
doc pandas --query "functions where param:DataFrame"
```

Output: All functions that accept DataFrame parameter.

```bash
doc pandas --query "functions where param:int and param:str"
```

Output: Functions accepting both int and str.

#### Find by Return Type

```bash
doc pandas --query "functions where returns:DataFrame"
```

Output: Functions returning DataFrame.

```bash
doc pandas --query "functions where returns:DataFrame|Series"
```

Output: Functions returning DataFrame OR Series.

### Complex Queries

#### Multiple Conditions

```bash
doc pandas --query "functions where param:DataFrame and returns:DataFrame"
```

Functions that take and return DataFrame.

#### Negation

```bash
doc pandas --query "functions where param:DataFrame and not deprecated"
```

Non-deprecated functions accepting DataFrame.

#### Comparisons

```bash
doc pandas --query "functions where params > 3"
```

Functions with more than 3 parameters.

```bash
doc pandas --query "classes where methods > 20"
```

Classes with more than 20 methods.

#### Category Filtering

```bash
doc pandas --query "functions where category:visualization"
```

Functions in visualization category.

```bash
doc pandas --query "functions where tag:experimental"
```

Functions tagged as experimental.

### Relationship Queries

#### Find Callers

```bash
doc pandas --query "functions where calls DataFrame.groupby"
```

Functions that call DataFrame.groupby.

#### Find Callees

```bash
doc pandas.DataFrame --query "methods where calls external"
```

Methods that call external functions.

#### Inheritance

```bash
doc pandas --query "classes where inherits_from NDFrame"
```

Classes that inherit from NDFrame.

```bash
doc pandas --query "classes where inherited_by length > 0"
```

Classes that have subclasses.

### Text Search

#### Docstring Search

```bash
doc pandas --query "functions where docstring contains 'merge'"
```

Functions with 'merge' in docstring.

#### Name Search

```bash
doc pandas --query "functions where name starts with 'to_'"
```

Functions whose names start with 'to_'.

```bash
doc pandas --query "functions where name matches '.*_csv$'"
```

Functions ending with '_csv' (regex).

### Metadata Queries

#### SDK Metadata

```bash
doc pandas --query "functions where meta.performance = 'fast'"
```

Functions marked as fast.

```bash
doc pandas --query "functions where meta.thread_safe = true"
```

Thread-safe functions.

#### Notes

```bash
doc pandas --query "functions where note type = 'warning'"
```

Functions with warning notes.

#### Examples

```bash
doc pandas --query "functions where examples count > 3"
```

Functions with more than 3 examples.

## Query Syntax

### SELECT Clause

```sql
SELECT classes
SELECT functions, methods
SELECT *  # All elements
```

### WHERE Clause

```sql
WHERE param:DataFrame
WHERE returns:int
WHERE category:visualization
WHERE tag:experimental
WHERE deprecated = true
WHERE params > 3
WHERE docstring contains "merge"
```

### Operators

#### Comparison

```
=          # Equals
!=         # Not equals
>          # Greater than
<          # Less than
>=         # Greater or equal
<=         # Less or equal
```

#### Logical

```
and        # Both conditions
or         # Either condition
not        # Negation
```

#### String

```
contains   # Contains substring
starts     # Starts with
ends       # Ends with
matches    # Regex match
```

#### Membership

```
in         # In list
not in     # Not in list
```

### Functions

#### Aggregate

```
count()    # Count of elements
sum()      # Sum of values
avg()      # Average
min()      # Minimum
max()      # Maximum
```

#### String

```
length()   # String length
lower()    # Lowercase
upper()    # Uppercase
```

## Examples by Use Case

### Find Alternative Functions

```bash
doc pandas --query "functions where returns:DataFrame and not deprecated and docstring contains 'combine'"
```

### Find Public API

```bash
doc pandas --query "functions where not name starts with '_' and not tag:internal"
```

### Find Complex Functions

```bash
doc pandas --query "functions where complexity > 10"
```

### Find Well-Documented

```bash
doc pandas --query "functions where docstring length > 100 and examples count > 0"
```

### Find Deprecated

```bash
doc pandas --query "functions where deprecated = true order by deprecated_since desc"
```

## Query Chaining

### Pipe Queries

```bash
doc pandas \
  --query "functions where param:DataFrame" \
  --query "not deprecated" \
  --query "returns:DataFrame"
```

Applies filters sequentially.

### Save and Reuse

```bash
# Save query
doc pandas --query "functions where param:DataFrame" --save-query dataframe-funcs

# Use saved query
doc pandas --use-query dataframe-funcs
```

## Query Builder

### Interactive Mode

```bash
doc --query-builder
```

Interactive query building:
```
> Select type: [class|function|method] > function
> Filter by param: DataFrame
> Filter by returns: DataFrame
> Exclude deprecated: yes
>
> Query: functions where param:DataFrame and returns:DataFrame and not deprecated
> Execute? [y/n]: y
```

### Query Templates

```bash
# Save template
doc --save-template public-api \
  --query "functions where not name starts with '_' and not tag:internal"

# Use template
doc pandas --use-template public-api
```

## Query Optimization

### Query Plan

```bash
doc pandas --query "functions where param:DataFrame and returns:DataFrame" --explain
```

Output:
```json
{
  "query": "functions where param:DataFrame and returns:DataFrame",
  "plan": [
    {"step": "filter", "criterion": "type=function", "estimated_rows": 4521},
    {"step": "filter", "criterion": "param:DataFrame", "estimated_rows": 234},
    {"step": "filter", "criterion": "returns:DataFrame", "estimated_rows": 123}
  ],
  "estimated_time_ms": 15
}
```

### Query Cache

```bash
doc pandas --query "functions where param:DataFrame" --cache
```

Caches query result for reuse.

### Query Index

```bash
doc pandas --build-query-index
```

Builds index for faster queries.

## Query Results

### Format Output

```bash
doc pandas --query "functions where param:DataFrame" --format json
doc pandas --query "functions where param:DataFrame" --format table
doc pandas --query "functions where param:DataFrame" --format csv
```

### Limit Results

```bash
doc pandas --query "functions where param:DataFrame" --limit 10
```

First 10 results.

### Pagination

```bash
doc pandas --query "functions where param:DataFrame" --page 2 --per-page 20
```

Page 2, 20 per page.

### Sorting

```bash
doc pandas --query "functions where param:DataFrame" --sort name
doc pandas --query "functions where param:DataFrame" --sort params desc
doc pandas --query "functions where param:DataFrame" --sort complexity asc
```

## Query Analysis

### Query Statistics

```bash
doc pandas --query "functions where param:DataFrame" --stats
```

Output:
```json
{
  "query": "functions where param:DataFrame",
  "results": 234,
  "total_scanned": 4521,
  "execution_time_ms": 12,
  "filters": [
    {"criterion": "type=function", "filtered": 0},
    {"criterion": "param:DataFrame", "filtered": 4287}
  ]
}
```

### Query Suggestions

```bash
doc pandas --suggest-query "I want functions that work with DataFrames"
```

Natural language to query:
```
Suggested query: functions where param:DataFrame or returns:DataFrame
Execute? [y/n]:
```

## Query History

### View History

```bash
doc --query-history
```

Output:
```
1. functions where param:DataFrame
2. classes where methods > 20
3. functions where tag:experimental
```

### Re-run Query

```bash
doc --query-history --rerun 1
```

Re-runs first query from history.

## Query Validation

### Validate Query

```bash
doc pandas --query "functions where invalid_param:value" --validate
```

Output:
```
Error: Unknown field 'invalid_param'
Available fields: param, returns, category, tag, deprecated, ...
```

### Dry Run

```bash
doc pandas --query "functions where param:DataFrame" --dry-run
```

Shows query plan without executing.

## Advanced Queries

### Subqueries

```bash
doc pandas --query "functions where param in (select classes where name = 'DataFrame')"
```

### Joins

```bash
doc pandas --query "functions where param = DataFrame.name and returns = Series.name"
```

### Aggregation

```bash
doc pandas --query "category, count(*) group by category"
```

Output:
```json
{
  "visualization": 15,
  "io": 25,
  "processing": 45
}
```

### Having Clause

```bash
doc pandas --query "category, count(*) group by category having count(*) > 10"
```

Categories with more than 10 elements.

## Query API

```python
from docs_cli import QueryEngine

engine = QueryEngine("pandas")

# Build query
query = (engine
  .select("functions")
  .where("param:DataFrame")
  .where_not("deprecated")
  .sort("name"))

# Execute
results = query.execute()

# Iterate
for func in results:
    print(func.name, func.signature)
```

Programmatic query building.

## Query Language Reference

### Fields

| Field | Type | Example |
|-------|------|---------|
| name | string | `where name starts with 'to_'` |
| type | enum | `where type = function` |
| param | type | `where param:DataFrame` |
| returns | type | `where returns:int` |
| params | number | `where params > 3` |
| docstring | text | `where docstring contains 'merge'` |
| category | string | `where category:visualization` |
| tag | string | `where tag:experimental` |
| deprecated | bool | `where deprecated = true` |
| complexity | number | `where complexity > 10` |
| methods | number | `where methods > 20` (classes) |

### Values

| Type | Examples |
|-------|----------|
| string | `'text'`, `"text"` |
| number | `42`, `3.14` |
| bool | `true`, `false` |
| type | `DataFrame`, `int`, `str|None` |
| list | `['a', 'b']` |
| regex | `'.*_csv$'` |

## Query Best Practices

### Use Specific Filters

```bash
# Good
doc pandas --query "functions where param:DataFrame and category:io"

# Less efficient
doc pandas --query "functions where docstring contains 'DataFrame'"
```

### Exclude Unnecessary

```bash
# Good
doc pandas --query "functions where param:DataFrame and not deprecated"

# Includes unnecessary results
doc pandas --query "functions where param:DataFrame"
```

### Use Indexes

```bash
# With index
doc pandas --use-index pandas.docs-index --query "functions where param:DataFrame"

# Slower without index
doc pandas --query "functions where param:DataFrame"
```

### Limit Results

```bash
# Good for exploration
doc pandas --query "functions where param:DataFrame" --limit 20

# For comprehensive results, paginate
doc pandas --query "functions where param:DataFrame" --per-page 50
```
