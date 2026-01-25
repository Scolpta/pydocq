# When / Context Decorator

Specify in which context a function should (or shouldn't) be used.

## Usage

```python
from docs_cli import when

@when(
    use_case="large datasets",
    description="Use this when data doesn't fit in memory"
)
def read_chunked(filepath):
    pass

@when(
    not_recommended="production",
    reason="Not optimized for performance",
    alternative="use process_fast instead"
)
def process_slow(data):
    pass
```

## Examples

### Use Case Specification

```python
@when(
    use_case="small data",
    description="For datasets under 1000 rows"
)
def process_in_memory(data):
    pass

@when(
    use_case="large data",
    description="For datasets that don't fit in memory"
)
def process_chunked(filepath):
    pass
```

Query:
```bash
doc mymodule.process --context
```

Output:
```json
{
  "functions": [
    {
      "path": "mymodule.process_in_memory",
      "use_case": "small data",
      "description": "For datasets under 1000 rows"
    },
    {
      "path": "mymodule.process_chunked",
      "use_case": "large data",
      "description": "For datasets that don't fit in memory"
    }
  ]
}
```

### Not Recommended Contexts

```python
@when(
    not_recommended="production",
    reason="No error handling, not suitable for production",
    alternative="use robust_process() instead"
)
def quick_process(data):
    pass

@when(
    not_recommended="large datasets",
    reason="O(n²) complexity, very slow on large data",
    alternative="use vectorized_process() for better performance"
)
def naive_process(data):
    pass
```

Query:
```bash
doc mymodule.quick_process --context
```

Output:
```json
{
  "not_recommended": {
    "context": "production",
    "reason": "No error handling, not suitable for production",
    "alternative": "robust_process()"
  }
}
```

### Requirements / Preconditions

```python
@when(
    requires=["network access", "API key"],
    setup="Set API_KEY environment variable"
)
def fetch_data(url):
    pass

@when(
    requires="GPU",
    description="Needs CUDA-compatible GPU",
    setup="Install torch with CUDA support"
)
def train_model(data):
    pass
```

### Performance Contexts

```python
@when(
    performance="fast",
    complexity="O(n)",
    description="Linear time, suitable for large datasets"
)
def fast_process(data):
    pass

@when(
    performance="slow",
    complexity="O(n²)",
    description="Quadratic time, use only for small datasets"
)
def accurate_process(data):
    pass
```

### Thread Safety Contexts

```python
@when(
    thread_safe=True,
    description="Can be safely called from multiple threads"
)
def process(data):
    pass

@when(
    thread_safe=False,
    warning="Not thread-safe, use locks or process sequentially"
)
def process_unsafe(data):
    pass
```

### Async Contexts

```python
@when(
    must_use_await=True,
    description="Must be awaited, blocking if called directly"
)
async def fetch_data(url):
    pass

@when(
    blocking_call=True,
    warning="This function blocks, avoid in async contexts"
)
def blocking_operation():
    pass
```

## Query Contexts

### Find by Use Case

```bash
doc mypackage --context "large data"
```

Output:
```json
{
  "context": "large data",
  "matching_functions": [
    {
      "path": "mypackage.process_chunked",
      "use_case": "large data",
      "recommended": true
    },
    {
      "path": "mypackage.naive_process",
      "not_recommended": "large datasets",
      "recommended": false
    }
  ]
}
```

### Find Requirements

```bash
doc mypackage --requires "GPU"
```

Output:
```json
{
  "requires": "GPU",
  "functions": [
    {"path": "mypackage.train_model", "requires": "GPU"},
    {"path": "mypackage.inference", "requires": "GPU"}
  ]
}
```

### Find Thread-Safe Functions

```bash
doc mypackage --thread-safe
```

Output:
```json
{
  "thread_safe": true,
  "functions": [
    {"path": "mypackage.process"},
    {"path": "mypackage.compute"}
  ]
}
```

## Decorator Options

```python
@when(
    # Positive context
    use_case=None,              # When to use this function
    requires=None,              # What this function requires

    # Negative context
    not_recommended=None,       # When NOT to use this function
    warnings=[],                # Contextual warnings

    # Alternatives
    alternative=None,           # What to use instead

    # Metadata
    description=None,           # Context description
    setup=None,                 # Setup instructions
    examples=[]                 # Example scenarios
)
```

## Complex Contexts

### Multiple Contexts

```python
@when(
    use_case="development",
    description="Quick validation during development"
)
@when(
    not_recommended="production",
    reason="Not thoroughly tested"
)
def dev_validate(data):
    pass
```

### Conditional Recommendations

```python
@when(
    use_case="data < 1000 rows",
    description="Fast for small data",
    alternative="use chunked version for larger data"
)
def process_small(data):
    pass

@when(
    use_case="data >= 1000 rows",
    description="Handles large datasets efficiently"
)
def process_large(data):
    pass
```

## Use Cases for Agents

### Context-Aware Recommendations

```python
# User: "I want to process a 10GB CSV file"

1. Agent checks context decorators
2. Finds process_small (not recommended for large data)
3. Finds process_large (recommended for large data)
4. Suggests: "Use process_large() for your 10GB file"
```

### Warning Users

```python
# Agent: "How do I validate my data?"

1. User is in production environment
2. doc mypackage.dev_validate --context
3. Sees: not_recommended="production"
4. Warns: "dev_validate is not recommended for production. Use validate() instead."
```

### Setup Guidance

```python
# User: "I want to use train_model()"

1. doc mypackage.train_model --context
2. Sees: requires="GPU"
3. Provides setup: "train_model requires a GPU. Install torch with CUDA support."
4. Helps user get started
```

### Performance Guidance

```python
# User: "Which should I use: fast or accurate?"

1. Agent checks both functions
2. fast_process: performance="fast", complexity="O(n)"
3. accurate_process: performance="slow", complexity="O(n²)"
4. Explains trade-off
5. "fast_process is O(n) and suitable for large datasets. accurate_process is O(n²) but more precise."
```

### Avoiding Mistakes

```python
# Agent: "Review my code"

Sees: user calls blocking_operation() in async function

1. doc blocking_operation --context
2. Sees: blocking_call=True, warning="avoid in async contexts"
3. Warns user: "blocking_operation is blocking and shouldn't be used in async code"
4. Suggests async alternative
```

## Context Scenarios

### Development vs Production

```python
@when(
    use_case="development",
    features=["verbose logging", "debug mode", "no caching"]
)
def dev_process(data):
    pass

@when(
    use_case="production",
    features=["optimized", "error handling", "monitoring"]
)
def prod_process(data):
    pass
```

### Data Size Scenarios

```python
@when(use_case="< 1MB")
def process_tiny(data):
    pass

@when(use_case="1MB - 100MB")
def process_medium(data):
    pass

@when(use_case="> 100MB")
def process_large(data):
    pass
```

### Time Constraints

```python
@when(
    use_case="real-time",
    max_latency_ms=10,
    description="For real-time processing"
)
def fast_process(data):
    pass

@when(
    use_case="batch",
    description="For batch processing, higher latency acceptable"
)
def thorough_process(data):
    pass
```

## Storage

Context stored on function:

```python
>>> process.__doc_context__
{
  'use_case': 'large data',
  'description': 'For datasets that don't fit in memory',
  'not_recommended': None
}
```

## Context Validation

```bash
doc mypackage --validate-contexts
```

Checks for:
- Conflicting contexts
- Missing alternatives for not_recommended
- Missing setup for requirements

## Combining with Other Decorators

```python
@category("data-processing")
@when(use_case="large data", performance="slow")
@deprecated("Use new_process instead")
@returns(DataFrame)
def process_large(data):
    pass
```

All context information is queryable together.
