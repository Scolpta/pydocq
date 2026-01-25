# Returns Decorator

Document return values with constraints, descriptions, and examples.

## Usage

```python
from docs_cli import returns

@returns(
    type="DataFrame",
    description="Processed data with new columns"
)
def process(df):
    pass

@returns(
    type="tuple[int, bool]",
    description="(count, success) where count is items processed and success indicates if all succeeded"
)
def process_all(items):
    pass
```

## Examples

### Basic Return Documentation

```python
@returns(
    type="DataFrame",
    description="DataFrame with processed data"
)
def process(data):
    pass

@returns(
    type="int",
    description="Number of items processed",
    min=0
)
def count_items(items):
    pass
```

Query:
```bash
doc mymodule.process --returns
```

Output:
```json
{
  "path": "mymodule.process",
  "returns": {
    "type": "DataFrame",
    "description": "DataFrame with processed data"
  }
}
```

### Multiple Return Values

```python
@returns(
    type="tuple[DataFrame, dict]",
    description="(df, metadata) where df is the result and metadata contains processing info",
    fields=[
        {"name": "df", "type": "DataFrame", "description": "Processed data"},
        {"name": "metadata", "type": "dict", "description": "Processing metadata"}
    ]
)
def process_with_metadata(data):
    pass
```

### Union Return Types

```python
@returns(
    type="DataFrame | Series",
    description="DataFrame if multiple columns, Series if single column",
    depends_on="input columns"
)
def get_column(data, col):
    pass

@returns(
    type="str | None",
    description="String value if found, None if not found"
)
def find_value(key):
    pass
```

### Optional Returns

```python
@returns(
    type="int | None",
    description="Count if successful, None if failed",
    nullable=True
)
def try_count(items):
    pass
```

### Return with Constraints

```python
@returns(
    type="int",
    description="Number of processed items",
    min=0,
    max=None,
    example=42
)
def process(items):
    pass

@returns(
    type="float",
    description="Success rate between 0 and 1",
    min=0.0,
    max=1.0
)
def calculate_success_rate(results):
    pass
```

### Return with Examples

```python
@returns(
    type="dict",
    description="Configuration dictionary",
    examples=[
        "{'batch_size': 32, 'learning_rate': 0.001}",
        "{'batch_size': 64, 'learning_rate': 0.0001, 'epochs': 100}"
    ]
)
def get_config(mode):
    pass
```

### Structured Return Types

```python
@returns(
    type="dict",
    structure={
        "status": "str (success|error)",
        "data": "list[dict] | None",
        "error": "str | None",
        "timestamp": "str (ISO format)"
    }
)
def api_response():
    pass
```

Output:
```json
{
  "returns": {
    "type": "dict",
    "structure": {
      "status": "str (success|error)",
      "data": "list[dict] | None",
      "error": "str | None",
      "timestamp": "str (ISO format)"
    }
  }
}
```

### Return Shape Information

```python
@returns(
    type="DataFrame",
    description="Filtered DataFrame",
    shape="Same as input, only rows filtered"
)
def filter_rows(df, condition):
    pass

@returns(
    type="ndarray",
    description="Flattened array",
    shape="(n,) where n is total elements of input"
)
def flatten(arr):
    pass
```

### Generator Returns

```python
@returns(
    type="Generator[int, None, None]",
    description="Yields integers one at a time",
    yields="int",
    infinite=False
)
def count_up_to(n):
    for i in range(n):
        yield i
```

### Async Returns

```python
@returns(
    type="Coroutine[None, None, str]",
    description="Async function that returns string",
    awaitable=True
)
async def fetch_data(url):
    return "data"
```

## Decorator Signature

```python
@returns(
    type,                      # Return type
    description=None,           # Description of return value
    nullable=False,             # Can return None
    min=None,                   # Minimum value (for numbers)
    max=None,                   # Maximum value (for numbers)
    examples=None,              # Example return values
    structure=None,             # Dict structure for complex types
    shape=None,                 # Shape information (for arrays)
    fields=None,                # Fields for tuple/namedtuple
    depends_on=None,            # What return depends on
    yields=None,                # What generator yields
    awaitable=False             # Is async/awaitable
)
```

## Query Returns

### Basic Query

```bash
doc mymodule.process --returns
```

### Compare Returns

```bash
doc mymodule.process_a mymodule.process_b --returns
```

Output:
```json
{
  "comparison": [
    {
      "function": "process_a",
      "returns": {"type": "DataFrame"}
    },
    {
      "function": "process_b",
      "returns": {"type": "Series"}
    }
  ]
}
```

### Find by Return Type

```bash
doc mypackage --returns-type DataFrame
```

Returns all functions that return DataFrame.

## Use Cases for Agents

### Return Value Validation

```python
# Agent: "Check if this return is valid"

function returns: int, min=0, max=100

actual = process(data)

1. Check actual return value
2. If actual = 150:
3. "Warning: process() returned 150 but max is 100"
```

### Code Completion

```python
# User types: result = process()

1. Agent checks return type
2. doc process --returns
3. Sees: type="DataFrame"
4. Can suggest DataFrame methods:
5. "result.", suggest: filter, sort, groupby, ...
```

### Type Inference

```python
# Agent: "What can I do with this result?"

result = fetch_data()

1. doc fetch_data --returns
2. type="dict[str, int]"
3. "result is a dict with string keys and int values"
4. Suggest appropriate operations
```

### Chaining Functions

```python
# Agent: "Can I chain these functions?"

process_a returns: DataFrame
process_b accepts: DataFrame

1. Check compatibility
2. "Yes, process_b can take output of process_a"
3. Suggest: process_b(process_a(data))
```

### Understanding Complex Returns

```python
# Agent: "What does this function return?"

api_response() returns:
{
  "status": "str (success|error)",
  "data": "list[dict] | None",
  "error": "str | None",
  "timestamp": "str (ISO format)"
}

1. Agent explains structure
2. "Returns a dict with 4 keys: status, data, error, timestamp"
3. "Check status to see if request succeeded"
4. "If status='success', data contains the results"
5. "If status='error', error contains the message"
```

### Test Generation

```python
# Agent: "Generate test for process()"

1. doc process --returns
2. type="int", min=0, max=100
3. Generates test:
   def test_process_return():
       result = process(test_data)
       assert isinstance(result, int)
       assert 0 <= result <= 100
```

## Combining with Type Hints

Works with standard type hints:

```python
def process(data: list[int]) -> dict[str, int]:
    pass

# Add extra info with decorator
@returns(
    description="Dict mapping values to their counts",
    examples=["{'a': 2, 'b': 1}"]
)
def process(data: list[int]) -> dict[str, int]:
    pass
```

Type hint provides type, decorator provides description and examples.

## Return Validation

### Runtime Validation

```python
@returns(
    type=int,
    min=0,
    max=100,
    validate=True  # Enable runtime validation
)
def process(items):
    return len(items)

# process([1, 2, 3]) → 3 ✓
# process([-1]) → Raises ReturnValidationError (value < min)
```

### Type Checking

```bash
doc mymodule --validate-returns
```

Checks actual return values against documented returns:
- Runs function with sample inputs
- Validates return type matches
- Validates constraints (min, max, etc.)
- Reports mismatches

## Storage

Return info stored on function:

```python
>>> process.__doc_returns__
{
  'type': 'DataFrame',
  'description': 'Processed data',
  'min': None,
  'max': None,
  'examples': [...]
}
```

## Integration with Examples

```python
@example("process(data)")
@returns(
    type="DataFrame",
    examples=["DataFrame with columns ['A', 'B', 'result']"]
)
def process(data):
    pass
```

Both examples are queryable.

## Nullable Returns

```python
@returns(
    type="int | None",
    nullable=True,
    description="Count if successful, None if failed",
    when_null="returns None when input is empty"
)
def count_or_none(items):
    return len(items) if items else None
```

Agent understands when None is returned and can explain conditions.
