# Execution Tracing

Execute functions and trace their runtime behavior for deep understanding.

## Usage

```bash
doc <element> --trace [--args <args>] [--kwargs <kwargs>]
doc <element> --trace --file <input_file>
```

## Examples

### Basic Function Trace

```bash
doc pandas.read_csv --trace --file example.csv
```

Output:
```json
{
  "path": "pandas.read_csv",
  "execution": {
    "duration_ms": 45.2,
    "return_value": "DataFrame(100 rows x 5 columns)",
    "calls": [
      {
        "function": "open",
        "module": "builtins",
        "args": ["example.csv"],
        "duration_ms": 2.1,
        "return": "IO object"
      },
      {
        "function": "TextFileReader.__init__",
        "module": "pandas.io.parsers",
        "duration_ms": 3.4
      },
      {
        "function": "TextFileReader.read",
        "module": "pandas.io.parsers",
        "duration_ms": 38.2,
        "calls": [
          {
            "function": "parse_csv",
            "duration_ms": 32.1
          },
          {
            "function": "build_index",
            "duration_ms": 4.1
          }
        ]
      },
      {
        "function": "DataFrame.__init__",
        "module": "pandas.core.frame",
        "duration_ms": 1.5
      }
    ],
    "exceptions": [],
    "memory_peak_mb": 12.4
  }
}
```

### Trace with Arguments

```bash
doc pandas.DataFrame.sort_values --trace --args "df" --kwargs "by='name'"
```

Output:
```json
{
  "path": "pandas.DataFrame.sort_values",
  "execution": {
    "arguments": {
      "self": "DataFrame(100 rows)",
      "by": "'name'",
      "ascending": "True (default)"
    },
    "duration_ms": 3.2,
    "steps": [
      {
        "operation": "validate_column",
        "column": "name",
        "result": "exists"
      },
      {
        "operation": "get_indexer_for_column",
        "duration_ms": 0.5
      },
      {
        "operation": "argsort",
        "algorithm": "quicksort",
        "duration_ms": 2.1
      },
      {
        "operation": "reindex",
        "duration_ms": 0.6
      }
    ]
  }
}
```

### Exception Tracing

```bash
doc pandas.DataFrame.__setitem__ --trace --args "df" --kwargs "key='invalid', value=1"
```

Output:
```json
{
  "path": "pandas.DataFrame.__setitem__",
  "execution": {
    "raised_exception": true,
    "exception": {
      "type": "KeyError",
      "message": "'invalid'",
      "traceback": [
        "    at __setitem__, line 456: validate_key(key)",
        "    at validate_key, line 89: key not in self.columns"
      ],
      "trace_calls": [
        {
          "function": "__setitem__",
          "line": 456,
          "operation": "validate_key"
        },
        {
          "function": "validate_key",
          "line": 89,
          "operation": "check membership",
          "failed": true
        }
      ]
    },
    "duration_ms": 0.3,
    "partial_execution": true
  }
}
```

### Performance Profile

```bash
doc pandas.DataFrame.groupby --trace --profile
```

Output:
```json
{
  "path": "pandas.DataFrame.groupby",
  "execution": {
    "duration_ms": 12.4,
    "performance_profile": {
      "total_time": 12.4,
      "time_by_operation": [
        {"operation": "validate_columns", "time_ms": 1.2, "percent": 9.7},
        {"operation": "create_grouping", "time_ms": 8.5, "percent": 68.5},
        {"operation": "build_metadata", "time_ms": 2.7, "percent": 21.8}
      ],
      "bottlenecks": [
        {
          "operation": "create_grouping",
          "reason": "O(n) hash table construction",
          "optimization_suggestion": "Consider pre-sorting data"
        }
      ]
    }
  }
}
```

### Memory Tracking

```bash
doc pandas.read_csv --trace --file large.csv --memory
```

Output:
```json
{
  "execution": {
    "duration_ms": 234.5,
    "memory_profile": {
      "initial_mb": 45.2,
      "peak_mb": 234.8,
      "final_mb": 189.5,
      "allocations": [
        {"operation": "read file", "memory_mb": 45.2},
        {"operation": "parse data", "memory_mb": 123.4},
        {"operation": "build index", "memory_mb": 21.1},
        {"operation": "construct DataFrame", "memory_mb": 45.1}
      ],
      "garbage_collections": 2,
      "memory_leaked_mb": 0
    }
  }
}
```

## Trace Modes

### Call Tree

```bash
doc mymodule.process --trace --tree
```

Output:
```json
{
  "call_tree": {
    "function": "process",
    "duration_ms": 45.2,
    "children": [
      {
        "function": "validate_input",
        "duration_ms": 2.1,
        "children": []
      },
      {
        "function": "transform",
        "duration_ms": 38.5,
        "children": [
          {
            "function": "load_data",
            "duration_ms": 15.2
          },
          {
            "function": "apply_transform",
            "duration_ms": 20.1
          },
          {
            "function": "save_result",
            "duration_ms": 3.2
          }
        ]
      },
      {
        "function": "format_output",
        "duration_ms": 4.6
      }
    ]
  }
}
```

### Flat Profile

```bash
doc mymodule.process --trace --flat
```

Output:
```
Function                     Calls    Time    % Time
--------------------------------------------------------
process                      1        45.2    100.0
  ├─ validate_input          1        2.1     4.7
  ├─ transform               1        38.5    85.2
  │   ├─ load_data           1        15.2    33.6
  │   ├─ apply_transform     1        20.1    44.5
  │   └─ save_result         1        3.2     7.1
  └─ format_output           1        4.6     10.1
```

### Timeline View

```bash
doc mymodule.process --trace --timeline
```

Output:
```json
{
  "timeline": [
    {"time_ms": 0, "event": "start", "function": "process"},
    {"time_ms": 0.5, "event": "call", "function": "validate_input"},
    {"time_ms": 2.6, "event": "return", "function": "validate_input"},
    {"time_ms": 2.6, "event": "call", "function": "transform"},
    {"time_ms": 17.8, "event": "call", "function": "load_data"},
    {"time_ms": 33.0, "event": "return", "function": "load_data"},
    {"time_ms": 33.0, "event": "call", "function": "apply_transform"},
    {"time_ms": 53.1, "event": "return", "function": "apply_transform"},
    {"time_ms": 53.1, "event": "call", "function": "save_result"},
    {"time_ms": 56.3, "event": "return", "function": "save_result"},
    {"time_ms": 56.3, "event": "return", "function": "transform"},
    {"time_ms": 56.3, "event": "call", "function": "format_output"},
    {"time_ms": 60.9, "event": "return", "function": "format_output"},
    {"time_ms": 60.9, "event": "end", "function": "process"}
  ]
}
```

## Use Cases for Agents

### Understanding Behavior

```python
# Agent: "What does pandas.read_csv actually do?"

1. doc pandas.read_csv --trace --file data.csv
2. Sees call tree: open → parse → build_index → construct
3. Explains each step
4. "First it opens the file, then parses CSV into arrays, builds an index, and finally constructs the DataFrame"
```

### Performance Debugging

```python
# Agent: "Why is my code slow?"

1. Trace the slow function
2. Identify bottleneck
3. "apply_transform takes 85% of time (38ms out of 45ms total)"
4. Suggests optimization
5. "Consider vectorizing this operation or using parallel processing"
```

### Exception Explanation

```python
# Agent: "Why does this fail?"

User code fails with exception.

1. Trace with same arguments
2. See exact failure point
3. "Function fails at validate_key step because column 'invalid' doesn't exist"
4. Explains why validation happens there
5. Suggests fix
```

### Learning API Usage

```python
# Agent: "How does groupby work internally?"

1. doc pandas.DataFrame.groupby --trace --args "df" --kwargs "by='category'"
2. Sees steps: validate → create_groups → build_metadata → return GroupBy object
3. Explains it's lazy (returns GroupBy, not computed result)
4. "The actual computation happens when you call .agg() or .apply()"
```

### Memory Investigation

```python
# Agent: "Why does this use so much memory?"

1. Trace with --memory
2. See memory allocations
3. "Peak memory is 234MB, with 123MB allocated during parse_data step"
4. Suggests chunking or streaming
5. "Use read_csv(chunksize=1000) to process in smaller batches"
```

### Comparing Implementations

```python
# Agent: "Which is faster: merge or join?"

1. Trace both operations
2. Compare durations and profiles
3. "merge: 12.4ms, join: 8.2ms"
4. Explains difference
5. "join is faster because it's optimized for index-based merging"
```

## Trace Filtering

```bash
doc mymodule.process --trace --include "external"
```

Only trace calls to external modules (not local functions).

```bash
doc mymodule.process --trace --exclude "builtins"
```

Exclude built-in function calls.

```bash
doc mymodule.process --trace --min-duration 1.0
```

Only show calls taking more than 1ms.

## Conditional Tracing

```bash
doc mymodule.process --trace --condition "duration_ms > 10"
```

Only show operations taking more than 10ms.

```bash
doc mymodule.process --trace --exception-only
```

Only trace if an exception is raised.

## Replay Trace

```bash
doc mymodule.process --trace --record --output trace.json
```

Save trace for later analysis:

```bash
doc --replay trace.json
```

Replay and analyze trace offline.

## Trace Comparison

```bash
doc mymodule.process --trace --args "small_data" --output trace1.json
doc mymodule.process --trace --args "large_data" --output trace2.json
doc --compare-traces trace1.json trace2.json
```

Output:
```json
{
  "comparison": {
    "small_data": {"duration_ms": 5.2},
    "large_data": {"duration_ms": 45.3},
    "difference": "+40.1ms",
    "bottleneck_diff": "apply_transform takes 3x longer on large data"
  }
}
```

## Visual Trace

```bash
doc mymodule.process --trace --visual --output trace.html
```

Generates interactive flame graph or timeline visualization.

## Safety Considerations

### Dry Run

```bash
doc mymodule.destructive_operation --trace --dry-run
```

Trace without actually executing (static analysis only).

### Sandbox

```bash
doc untrusted.module --trace --sandbox
```

Execute in isolated environment (limited resources, no file system access).

### Timeout

```bash
doc mymodule.slow_function --trace --timeout 5.0
```

Abort if execution takes longer than 5 seconds.
