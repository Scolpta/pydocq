# Note Decorator

Add freeform notes (warnings, tips, gotchas) to elements.

## Usage

```python
from docs_cli import note

@note("warning", "This function mutates the input list")
@note("tip", "Use process_copy() for non-mutating version")
def process(data):
    pass
```

## Examples

### Single Note

```python
@note("warning", "This function is deprecated")
def old_function():
    pass
```

Query:
```bash
doc mymodule.old_function --notes
```

Output:
```json
{
  "path": "mymodule.old_function",
  "notes": [
    {
      "type": "warning",
      "message": "This function is deprecated"
    }
  ]
}
```

### Multiple Notes

```python
@note("warning", "This function mutates the input list")
@note("tip", "Use process_copy() for non-mutating version")
@note("performance", "O(n²) - slow for large datasets")
def process(data):
    pass
```

Or with list:
```python
@note([
    ("warning", "This function mutates the input list"),
    ("tip", "Use process_copy() for non-mutating version"),
    ("performance", "O(n²) - slow for large datasets")
])
def process(data):
    pass
```

Query:
```bash
doc mymodule.process --notes
```

Output:
```json
{
  "notes": [
    {"type": "warning", "message": "This function mutates the input list"},
    {"type": "tip", "message": "Use process_copy() for non-mutating version"},
    {"type": "performance", "message": "O(n²) - slow for large datasets"}
  ]
}
```

### Note Types

```python
@note("warning", "Deprecated in version 2.0")
@note("error", "Will fail if input is None")
@note("tip", "Use async version for better performance")
@note("info", "This function is thread-safe")
@note("gotcha", "Does not work with empty lists")
@note("performance", "O(n²) complexity - slow for large data")
@note("security", "Ensure input is sanitized before use")
@note("usage", "Call close() when done to free resources")
def func():
    pass
```

## Standard Note Types

### Warning
```python
@note("warning", "This function may raise exceptions on invalid input")
```

### Tip
```python
@note("tip", "Use the batch version for multiple items")
```

### Gotcha
```python
@note("gotcha", "Modifies input in place, use copy() first")
```

### Performance
```python
@note("performance", "Loads entire file into memory - not suitable for large files")
```

### Security
```python
@note("security", "Never log sensitive data from this function")
```

### Usage
```python
@note("usage", "Must be called within a context manager")
```

### Info
```python
@note("info", "This function is cached and may return stale data")
```

### Error
```python
@note("error", "Will raise ValueError if input contains NaN")
```

## Query by Note Type

### Find Warnings

```bash
doc mypackage --notes warning
```

Output:
```json
{
  "note_type": "warning",
  "matches": [
    {"path": "mypackage.process", "note": "This function mutates the input list"},
    {"path": "mypackage.old_func", "note": "This function is deprecated"}
  ]
}
```

### Find Performance Notes

```bash
doc mypackage --notes performance
```

### Find All Notes

```bash
doc mypackage --all-notes
```

Output:
```json
{
  "notes": [
    {"path": "func1", "type": "warning", "message": "..."},
    {"path": "func2", "type": "tip", "message": "..."},
    {"path": "func3", "type": "gotcha", "message": "..."}
  ]
}
```

## Use Cases for Agents

### Warning Users

```python
# Agent: "How do I use process()?"

1. doc mymodule.process --notes
2. Sees warning: "This function mutates the input list"
3. Warns user: "Be careful, process() modifies your input in place"
4. Suggests alternative: "Use process_copy() if you need to keep the original"
```

### Providing Tips

```python
# Agent: "This function is slow"

1. doc mymodule.slow_func --notes
2. Sees tip: "Use async version for better performance"
3. Suggests: "Try slow_func_async() instead"
```

### Explaining Gotchas

```python
# Agent: "Why does my code fail?"

1. doc mymodule.process --notes
2. Sees gotcha: "Does not work with empty lists"
3. User's input is empty
4. Explains: "This function doesn't support empty lists, add a check first"
```

### Security Warnings

```python
# Agent: "Review my code"

Sees user logging result of sensitive_function()

1. doc sensitive_function --notes
2. Sees: "Never log sensitive data from this function"
3. Warns: "You're logging sensitive data, this is a security issue"
```

### Performance Guidance

```python
# User: "Process this 100MB file"

1. Agent checks notes for suggested function
2. doc mymodule.load_file --notes
3. Sees: "Loads entire file into memory - not suitable for large files"
4. Suggests: "Use load_chunked() instead for large files"
```

### Usage Context

```python
# Agent: "How do I use Database?"

1. doc mypackage.Database --notes
2. Sees: "Must be called within a context manager"
3. Shows example:
   with Database() as db:
       db.query(...)
```

## Note Priorities

```python
@note("warning", "Deprecated", priority="high")
@note("tip", "Use batch version", priority="low")
```

Query:
```bash
doc mypackage --notes --min-priority high
```

Shows only high-priority notes.

## Note Conditions

```python
@note(
    "warning",
    "May fail with large datasets",
    condition="data_size > 1GB"
)
def process(data):
    pass
```

Output:
```json
{
  "notes": [
    {
      "type": "warning",
      "message": "May fail with large datasets",
      "condition": "data_size > 1GB"
    }
  ]
}
```

Agent can warn user based on their actual data size.

## Note Formatting

```python
@note("tip", """
For better performance, consider:
- Using the batch version
- Pre-allocating output array
- Disabling validation if input is trusted
""")
def process(data):
    pass
```

Multi-line notes are supported.

## Note Links

```python
@note("info", "See docs: https://example.com/docs/process")
@note("related", "See also: process_async, process_batch")
def process(data):
    pass
```

Notes can include references to documentation or related functions.

## Combining with Other Decorators

```python
@category("data-processing")
@note("warning", "Mutates input")
@note("performance", "O(n²)")
@deprecated("Use new_process instead")
@tag("legacy")
def process(data):
    pass
```

All metadata queryable together.

## Note Search

```bash
doc mypackage --note-search "mutate"
```

Finds all notes containing "mutate":
```json
{
  "matches": [
    {"path": "process", "note": "Mutates input in place"},
    {"path": "transform", "note": "May mutate depending on parameters"}
  ]
}
```

## Storage

Notes stored on function:

```python
>>> func.__doc_notes__
[
  {'type': 'warning', 'message': 'This function mutates input'},
  {'type': 'tip', 'message': 'Use copy() first'}
]
```

## Notes by Category

```python
@note.category("performance", [
    "O(n²) complexity",
    "High memory usage",
    "Not suitable for real-time"
])
@note.category("usage", [
    "Must call initialize() first",
    "Remember to call cleanup() when done"
])
def process():
    pass
```

Organizes related notes by category.

## Dynamic Notes

```python
def add_runtime_note(func, note_type, message):
    """Add a note at runtime."""
    if not hasattr(func, '__doc_notes__'):
        func.__doc_notes__ = []
    func.__doc_notes__.append({'type': note_type, 'message': message})
    return func

# Used to add notes based on runtime analysis
```

## Note Validation

```bash
doc mypackage --validate-notes
```

Checks for:
- Duplicate notes
- Empty note messages
- Invalid note types
- Notes contradicting other decorators (e.g., warning note but not tagged as experimental)

## Note Templates

```python
# .docs-cli/config.yaml
note_templates:
  mutation_warning:
    type: "warning"
    message: "This function mutates {input_type} in place"

  performance_warning:
    type: "performance"
    message: "O({complexity}) complexity - {guidance}"

Usage:
```python
@note.template("mutation_warning", input_type="list")
@note.template("performance_warning", complexity="n²", guidance="use batch version for large data")
def process(data):
    pass
```
