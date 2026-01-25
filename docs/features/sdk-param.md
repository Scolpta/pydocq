# Param Decorator

Document individual parameters with constraints and metadata.

## Usage

```python
from docs_cli import param

def process(
    data: list,
    limit: int = param(default=10, min=1, max=100, description="Max items to process"),
    validate: bool = param(default=True, description="Validate input before processing")
):
    pass
```

## Examples

### Basic Parameter Documentation

```python
def read_csv(
    filepath: str = param(description="Path to CSV file"),
    sep: str = param(default=",", description="Column separator"),
    encoding: str = param(default="utf-8", description="File encoding"),
    nrows: int = param(default=None, min=0, description="Number of rows to read")
):
    pass
```

Query:
```bash
doc mymodule.read_csv --params
```

Output:
```json
{
  "path": "mymodule.read_csv",
  "parameters": [
    {
      "name": "filepath",
      "type": "str",
      "required": true,
      "description": "Path to CSV file"
    },
    {
      "name": "sep",
      "type": "str",
      "default": ",",
      "description": "Column separator"
    },
    {
      "name": "encoding",
      "type": "str",
      "default": "utf-8",
      "description": "File encoding"
    },
    {
      "name": "nrows",
      "type": "int",
      "default": null,
      "min": 0,
      "description": "Number of rows to read"
    }
  ]
}
```

### Parameter with Constraints

```python
def process(
    count: int = param(
        default=10,
        min=1,
        max=100,
        description="Number of items"
    ),
    rate: float = param(
        default=0.5,
        min=0.0,
        max=1.0,
        description="Processing rate"
    ),
    mode: str = param(
        default="auto",
        choices=["auto", "fast", "accurate"],
        description="Processing mode"
    )
):
    pass
```

Output:
```json
{
  "parameters": [
    {
      "name": "count",
      "type": "int",
      "default": 10,
      "constraints": {
        "min": 1,
        "max": 100
      },
      "description": "Number of items"
    },
    {
      "name": "rate",
      "type": "float",
      "default": 0.5,
      "constraints": {
        "min": 0.0,
        "max": 1.0
      },
      "description": "Processing rate"
    },
    {
      "name": "mode",
      "type": "str",
      "default": "auto",
      "constraints": {
        "choices": ["auto", "fast", "accurate"]
      },
      "description": "Processing mode"
    }
  ]
}
```

### Parameter with Validation

```python
def connect(
    host: str = param(
        description="Server hostname or IP",
        pattern=r"^[\w\-\.]+$",  # Regex pattern
        example="localhost"
    ),
    port: int = param(
        default=8080,
        min=1,
        max=65535,
        description="Server port"
    ),
    timeout: int = param(
        default=30,
        min=1,
        max=300,
        unit="seconds",
        description="Connection timeout"
    )
):
    pass
```

### Parameter with Examples

```python
def query(
    sql: str = param(
        description="SQL query string",
        examples=[
            "SELECT * FROM users",
            "SELECT id, name FROM users WHERE active = true"
        ]
    ),
    params: dict = param(
        default=None,
        examples=[
            "{'user_id': 123}",
            "{'start_date': '2024-01-01', 'end_date': '2024-12-31'}"
        ]
    )
):
    pass
```

Query:
```bash
doc mymodule.query --params --examples
```

Output:
```json
{
  "parameters": [
    {
      "name": "sql",
      "examples": [
        "SELECT * FROM users",
        "SELECT id, name FROM users WHERE active = true"
      ]
    }
  ]
}
```

### Nullable/Optional Parameters

```python
def process(
    data: list = param(required=True, description="Input data"),
    config: dict = param(default=None, nullable=True, description="Optional config"),
    validator: Callable = param(default=None, nullable=True, description="Custom validator")
):
    pass
```

Output:
```json
{
  "parameters": [
    {
      "name": "data",
      "required": true,
      "nullable": false,
      "description": "Input data"
    },
    {
      "name": "config",
      "required": false,
      "default": null,
      "nullable": true,
      "description": "Optional config"
    }
  ]
}
```

## Decorator Signature

```python
param(
    default=...,           # Default value
    required=None,         # Override type inference
    nullable=False,        # Can be None
    description=None,      # Parameter description
    min=None,              # Minimum value (for numbers)
    max=None,              # Maximum value (for numbers)
    pattern=None,          # Regex pattern (for strings)
    choices=None,          # List of valid choices
    unit=None,             # Unit (e.g., "seconds", "MB")
    examples=None,         # List of example values
    deprecated=None,       # Deprecation info
    depends_on=None        # Parameter dependencies
)
```

## Advanced Features

### Parameter Dependencies

```python
def download(
    url: str = param(description="URL to download"),
    filename: str = param(
        description="Save as filename",
        depends_on="url",  # Only relevant if url is provided
        example="data.json"
    ),
    format: str = param(
        default="json",
        choices=["json", "csv", "xml"],
        description="Output format"
    )
):
    pass
```

Output:
```json
{
  "parameters": [
    {
      "name": "filename",
      "depends_on": "url",
      "note": "Only relevant when url is provided"
    }
  ]
}
```

### Deprecated Parameters

```python
def process(
    data: list,
    legacy_mode: bool = param(
        default=False,
        deprecated="2.0",
        use_instead="mode parameter",
        description="Legacy processing mode"
    ),
    mode: str = param(default="auto", description="Processing mode")
):
    pass
```

Query shows deprecation:
```json
{
  "parameters": [
    {
      "name": "legacy_mode",
      "deprecated": {
        "since": "2.0",
        "use_instead": "mode parameter"
      }
    }
  ]
}
```

### Parameter Groups

```python
from docs_cli import param_group

def connect(
    # Connection parameters
    host: str = param(group="connection", description="Server host"),
    port: int = param(group="connection", default=8080, description="Server port"),

    # Authentication parameters
    username: str = param(group="auth", description="Username"),
    password: str = param(group="auth", description="Password"),

    # Timeout parameters
    timeout: int = param(group="timeout", default=30, unit="seconds")
):
    pass
```

Query:
```bash
doc mymodule.connect --params --group-by
```

Output:
```json
{
  "parameter_groups": {
    "connection": [
      {"name": "host", "type": "str"},
      {"name": "port", "type": "int", "default": 8080}
    ],
    "auth": [
      {"name": "username", "type": "str"},
      {"name": "password", "type": "str"}
    ],
    "timeout": [
      {"name": "timeout", "type": "int", "default": 30, "unit": "seconds"}
    ]
  }
}
```

## Use Cases for Agents

### Parameter Validation

```python
# Agent: "Check if these arguments are valid"

User: process(count=150, rate=1.5, mode="invalid")

1. doc mymodule.process --params
2. Checks constraints
3. "count=150 exceeds max (100)"
4. "rate=1.5 exceeds max (1.0)"
5. "mode='invalid' not in choices ['auto', 'fast', 'accurate']"
```

### Argument Suggestions

```python
# Agent: "What parameters should I use?"

1. doc mymodule.process --params
2. Analyzes user's goal
3. "For large datasets, use: mode='accurate', count=100"
4. "For speed, use: mode='fast', timeout=10"
```

### Code Completion

```python
# Agent: "Complete this function call"

User types: read_csv(

1. Gets parameter list with descriptions
2. Suggests parameters in order
3. Shows constraints as user types
4. "filepath (required): Path to CSV file"
5. "sep (default ','): Column separator"
```

### Function Documentation

```python
# Agent: "Explain process() parameters"

1. doc mymodule.process --params
2. Generates formatted explanation
3. "data (list, required): Input data"
4. "limit (int, default 10, range 1-100): Max items"
5. "validate (bool, default True): Validate before processing"
```

### Test Case Generation

```python
# Agent: "Generate tests for parameter validation"

1. doc mymodule.process --params
2. For each constraint, generate test
3. count < 1 → test_value_error()
4. count > 100 → test_value_error()
5. mode not in choices → test_value_error()
```

## Storage

Parameter metadata stored on function:

```python
>>> process.__doc_params__
{
  'data': {'required': True, 'description': 'Input data'},
  'limit': {'default': 10, 'min': 1, 'max': 100, 'description': '...'},
  'validate': {'default': True, 'description': '...'}
}
```

Accessible via CLI.

## Integration with Type Hints

Works with standard type hints:

```python
def process(
    data: list[int],
    config: dict[str, Any] | None = param(default=None, description="Config dict"),
    callback: Callable[[int], bool] = param(description="Filter callback")
):
    pass
```

Type hints combined with param decorator:
- `list[int]` → type information
- `param()` → constraints, description, examples

## Parameter Inference

Without `param()` decorator, CLI infers from:
- Type hints
- Default values
- Docstring

With `param()`:
- Explicit constraints
- Additional metadata
- Examples
- Validation rules
