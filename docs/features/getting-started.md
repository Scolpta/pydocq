# Getting Started with docs-cli

Learn how docs-cli helps AI agents understand Python code through structured documentation queries.

## What is docs-cli?

docs-cli is a **command-line tool** that extracts and structures Python documentation for **AI agent consumption**. Unlike traditional documentation tools designed for humans, docs-cli outputs machine-readable, structured data that agents can use to:

- Discover APIs without reading source code
- Understand function signatures and types
- Find usage examples automatically
- Navigate package relationships
- Generate code based on patterns

## Quick Example

```bash
# Instead of reading source code or parsing docstrings
$ doc pandas.DataFrame.merge

# Get structured, agent-consumable output:
{
  "path": "pandas.DataFrame.merge",
  "signature": {...},
  "docstring": "...",
  "examples": [...],
  "parameters": [...]
}
```

## Basic Concepts

### 1. Discovery - Finding What's Available

**Problem:** Agent doesn't know what functions exist in a package.

```bash
# List all public elements
doc pandas

# Output:
{
  "members": [
    {"name": "DataFrame", "type": "class"},
    {"name": "Series", "type": "class"},
    {"name": "read_csv", "type": "function"}
  ]
}
```

**Use when:** Agent needs to discover what's available in a package.

### 2. Path Resolution - Accessing Specific Elements

**Problem:** Agent needs information about a specific function or class.

```bash
# Get specific element
doc pandas.DataFrame

# Get method
doc pandas.DataFrame.merge

# Get nested element
doc pandas.core.frame.DataFrame.__init__
```

**Use when:** Agent knows the name and needs detailed information.

### 3. Structured Output - Agent-Consumable Data

**Problem:** Docstrings are unstructured text, hard for agents to parse.

```bash
# Get structured JSON
doc pandas.DataFrame.merge --format json

# Get type summary only
doc pandas.DataFrame.merge --type-summary

# Get examples only
doc pandas.DataFrame.merge --examples
```

**Use when:** Agent needs machine-readable data, not human text.

## Agent Workflows

### Workflow 1: Answer "How do I..." Questions

**User asks:** "How do I load a CSV file in pandas?"

```
Step 1: Search for relevant functions
→ doc pandas --search "CSV"

Step 2: Get details on best match
→ doc pandas.read_csv

Step 3: Extract examples
→ doc pandas.read_csv --examples

Step 4: Generate response
→ "Use pandas.read_csv('file.csv') to load CSV files"
```

### Workflow 2: Generate Code from Intent

**User asks:** "I want to merge two DataFrames on a column"

```
Step 1: Find merge-related functions
→ doc pandas --search "merge"

Step 2: Get signature
→ doc pandas.DataFrame.merge --type-summary

Step 3: Get examples
→ doc pandas.DataFrame.merge --examples

Step 4: Check for deprecations
→ doc pandas.DataFrame.merge --deprecation

Step 5: Generate code
→ df1.merge(df2, on='id')
```

### Workflow 3: Understand Code Relationships

**User asks:** "What does this function depend on?"

```
Step 1: Get function details
→ doc mymodule.process_data

Step 2: Get relationships
→ doc mymodule.process_data --relations=calls

Step 3: Analyze dependencies
→ "process_data() calls: validate_input(), transform(), save_result()"

Step 4: Check each dependency
→ doc mymodule.validate_input
→ doc mymodule.transform
→ doc mymodule.save_result
```

### Workflow 4: Find Alternatives for Deprecated Code

**User shows code using deprecated function**

```
Step 1: Check deprecation
→ doc pandas.DataFrame.ix --deprecation

Step 2: Get replacement info
→ "use_instead": "loc or iloc"

Step 3: Find similar functions
→ doc pandas.DataFrame.ix --similar

Step 4: Get details on replacement
→ doc pandas.DataFrame.loc --examples

Step 5: Suggest migration
→ "Replace df.ix[row] with df.loc[row]"
```

### Workflow 5: Optimize Performance

**User asks:** "Why is my code slow?"

```
Step 1: Analyze used functions
→ Agent identifies: slow_function()

Step 2: Check complexity
→ doc mymodule.slow_function --complexity

Step 3: Check performance notes
→ doc mymodule.slow_function --notes

Step 4: Find alternatives
→ doc mymodule --tag "perf:fast"

Step 5: Suggest optimization
→ "Use fast_function() instead (O(n) vs O(n²))"
```

## Feature Selection Guide

### For Discovering APIs

| Need | Use |
|------|-----|
| List what's in package | `doc <package>` ([Discovery](./discovery.md)) |
| Search by keyword | `doc <package> --search <keyword>` ([Search](./search.md)) |
| Find by category | `doc <package> --category <name>` ([Category](./sdk-category.md)) |
| Find similar functions | `doc <element> --similar` ([Similarity](./semantic-similarity.md)) |

### For Understanding Code

| Need | Use |
|------|-----|
| Get signature | `doc <element> --type-summary` ([Type Inference](./type-inference.md)) |
| See examples | `doc <element> --examples` ([Examples](./usage-examples.md)) |
| Check deprecations | `doc <element> --deprecation` ([Deprecation](./deprecation.md)) |
| Understand complexity | `doc <element> --complexity` ([Complexity](./complexity-analysis.md)) |

### For Finding Relationships

| Need | Use |
|------|-----|
| What calls this? | `doc <element> --relations=called_by` ([Relationships](./relationship-analysis.md)) |
| What does this call? | `doc <element> --relations=calls` |
| Inheritance hierarchy | `doc <class> --relations=inheritance` |

### For Advanced Queries

| Need | Use |
|------|-----|
| Complex queries | `doc <package> --query "<query>"` ([Query Language](./query-language.md)) |
| Instant queries | Build index first ([Doc Index](./doc-index.md)) |
| Custom behavior | Register hooks ([Agent Hooks](./agent-hooks.md)) |

## Integration with SDK Decorators

SDK decorators let developers add metadata that agents can use:

```python
# Developer adds metadata
@example("process(data)")
@category("data-processing")
@note("warning", "This mutates input")
def process(data):
    pass
```

Agent can now:
- Find by category: `doc mypackage --category data-processing`
- Get examples: `doc mypackage.process --examples`
- See warnings: `doc mypackage.process --notes`

See [SDK Decorators](./sdk-example.md) for details.

## Common Patterns

### Pattern 1: Exploratory Search

```
1. Broad search: doc pandas --search "filter"
2. Narrow down: doc pandas --search "filter rows"
3. Get specific: doc pandas.DataFrame.query
4. Get examples: doc pandas.DataFrame.query --examples
```

### Pattern 2: Code Generation

```
1. Identify need: "aggregate data"
2. Search: doc pandas --search "aggregate"
3. Get signature: doc pandas.DataFrame.groupby --type-summary
4. Get examples: doc pandas.DataFrame.groupby --examples
5. Generate code based on examples
```

### Pattern 3: Debugging Help

```
1. User error with function
2. Get complexity: doc func --complexity
3. Check notes: doc func --notes
4. Check examples: doc func --examples
5. Provide targeted help
```

## Next Steps

1. **Learn Core Features** - Start with [Discovery](./discovery.md) and [Path Resolution](./path-resolution.md)
2. **Explore SDK** - See [SDK Decorators](./sdk-example.md) to enhance documentation
3. **Check Roadmap** - See [Roadmap](./roadmap.md) for implementation plan
4. **Build Advanced Queries** - Learn [Query Language](./query-language.md)

## Tips for Agent Developers

### Start Simple

Begin with basic queries, add complexity as needed:
```python
# Start here
doc pandas.DataFrame.merge

# Then add specifics
doc pandas.DataFrame.merge --examples
doc pandas.DataFrame.merge --type-summary
```

### Combine Features

Features work better together:
```bash
# Search + filter
doc pandas --search "merge" --filter "not deprecated"

# Relations + complexity
doc mymodule.process --relations --complexity
```

### Use Indexes for Large Packages

For frequently-used packages, build indexes:
```bash
doc-index build pandas --output pandas.docs-index
doc pandas.DataFrame --use-index pandas.docs-index
```

### Handle Errors Gracefully

```python
try:
    result = query("pandas.NonExistent")
except NotFoundError:
    # Search for alternatives
    alternatives = search("pandas", "similar to NonExistent")
```

## Real-World Example

Complete workflow for helping a user:

```
User: "How do I handle missing values in pandas?"

Agent Process:
1. Search: doc pandas --search "missing values"
2. Results found: dropna, fillna, isna
3. Get details on each:
   - doc pandas.DataFrame.dropna --examples
   - doc pandas.DataFrame.fillna --examples
   - doc pandas.isna --examples
4. Check for warnings:
   - doc pandas.DataFrame.dropna --notes
5. Generate response:
   "You have several options:
    - dropna(): Remove missing values
    - fillna(): Fill with specific value
    - isna(): Detect missing values

    Here are examples for each..."
```

## Support and Contributing

- See [Roadmap](./roadmap.md) for what's planned
- Check individual feature docs for detailed examples
- SDK decorators allow extending functionality
