# Documentation Templates / Scaffolding

Generate documentation templates to help developers document their code.

## Usage

```bash
doc-template generate function --name process_data
doc-template generate class --name DataProcessor
doc-template generate module --name mymodule
```

## Examples

### Function Template

```bash
doc-template generate function --name process_data
```

Generates:
```python
from docs_cli import category, example, returns, param, note

@category("data-processing")
@example("process_data(data)")
@example("process_data(data, validate=True)")
@returns(
    type="DataFrame",
    description="Processed data with transformations applied"
)
@param(
    data,
    description="Input data to process",
    required=True
)
@param(
    validate,
    default=True,
    description="Whether to validate input before processing"
)
@note("info", "This function modifies the DataFrame in place")
def process_data(data, validate=True):
    """
    Process input data.

    Parameters
    ----------
    data : DataFrame
        Input data to process
    validate : bool, default True
        Whether to validate input before processing

    Returns
    -------
    DataFrame
        Processed data with transformations applied

    Examples
    --------
    >>> process_data(df)
    DataFrame with processed values

    >>> process_data(df, validate=True)
    Validated and processed DataFrame
    """
    pass
```

### Class Template

```bash
doc-template generate class --name DataProcessor
```

Generates:
```python
from docs_cli import category, note

@category("data-processing")
@note("info", "This class is thread-safe")
class DataProcessor:
    """
    Process data with various transformations.

    Parameters
    ----------
    config : dict, optional
        Configuration options for processing

    Examples
    --------
    >>> processor = DataProcessor(config={'batch_size': 100})
    >>> processor.process(data)
    DataFrame with processed data
    """

    def __init__(self, config=None):
        """
        Initialize the processor.

        Parameters
        ----------
        config : dict, optional
            Configuration options
        """
        pass

    @example("processor.process(df)")
    @returns(DataFrame)
    def process(self, data):
        """
        Process the data.

        Parameters
        ----------
        data : DataFrame
            Input data

        Returns
        -------
        DataFrame
            Processed data
        """
        pass
```

### Module Template

```bash
doc-template generate module --name mymodule
```

Generates:
```python
"""
My module for data processing.

This module provides functions for processing and transforming data.
"""

from docs_cli import package_category

@package_category("data-processing")
__all__ = ["process_data", "transform_data", "validate_data"]


@category("data-processing")
def process_data(data):
    """
    Process input data.

    Parameters
    ----------
    data : DataFrame
        Input data

    Returns
    -------
    DataFrame
        Processed data
    """
    pass


@category("data-transformation")
def transform_data(data, method="standard"):
    """
    Transform data using specified method.

    Parameters
    ----------
    data : DataFrame
        Input data
    method : str, default 'standard'
        Transformation method

    Returns
    -------
    DataFrame
        Transformed data
    """
    pass
```

### Template with Existing Code

```bash
doc-template infer function mymodule.process_data
```

Analyzes existing function and generates template:
```python
# Original code
def process_data(data, validate=True):
    if validate:
        assert isinstance(data, list)
    return [x * 2 for x in data]

# Generated template
from docs_cli import param, returns, note

@param(data, description="Input data")
@param(validate, default=True, description="Validate input")
@returns(
    type="list",
    description="Doubled values"
)
@note("gotcha", "Asserts that data is a list if validate=True")
def process_data(data, validate=True):
    """
    Process input data.

    [Generated from analysis of function body]
    """
    if validate:
        assert isinstance(data, list)
    return [x * 2 for x in data]
```

## Template Types

### Basic Template

```bash
doc-template generate function --name func --style basic
```

Minimal template with just docstring.

### Full Template

```bash
doc-template generate function --name func --style full
```

Complete template with all decorators.

### SDK Template

```bash
doc-template generate function --name func --style sdk
```

Template with SDK decorators only.

### Custom Template

```bash
doc-template generate function --name func --template my-template
```

Uses custom template from `.docs-cli/templates/my-template.py`.

## Template Customization

### Define Custom Template

```python
# .docs-cli/templates/my-function.py
from docs_cli import template

@template.function
def my_function_template(name, params):
    return f'''
@category("custom")
@note("info", "Custom note")
def {name}({', '.join(params)}):
    """
    Custom function template.
    """
    pass
'''
```

Use:
```bash
doc-template generate function --name process --template my-function
```

### Template Variables

```bash
doc-template generate function \
  --name process \
  --var author="John Doe" \
  --var date="2024-01-15"
```

Template with variables:
```python
"""
@author: {author}
@date: {date}
"""
def process():
    pass
```

## Template Inheritance

```python
# Base template
@template.function(name="base")
def base_template(name):
    return f'''
@category("base")
def {name}():
    """Base function."""
    pass
'''

# Extended template
@template.function(name="extended", extends="base")
def extended_template(name):
    return f'''
@category("extended")
@note("info", "Extended function")
{base_template(name)}
'''
```

## Batch Template Generation

### Generate for All Functions in Module

```bash
doc-template generate-module mymodule --output templates/
```

Generates templates for all undocumented functions.

### Generate for Package

```bash
doc-template generate-package mypackage --recursive
```

Recursively generates templates for all modules.

## Template Fill-in

### Interactive Template Fill

```bash
doc-template fill function --name process_data --interactive
```

Prompts for each field:
```
Description: Process input data
Parameters: data (DataFrame), validate (bool, default=True)
Returns: DataFrame
Examples: process_data(df), process_data(df, validate=False)
Notes: Modifies in place
Category: data-processing

Generating template...
```

### From Configuration

```yaml
# .docs-cli/template-config.yaml
function:
  default_category: "data-processing"
  always_add:
    - note("info", "Check documentation for updates")
  prompts:
    - description
    - parameters
    - returns
    - examples
```

## Template Validation

### Validate Template

```bash
doc-template validate my-template.py
```

Checks template for:
- Valid syntax
- Required fields
- Decorator consistency

### Test Template

```bash
doc-template test my-template.py --with-example
```

Generates example code from template to verify it works.

## Use Cases for Agents

### Helping Users Document Code

```python
# User: "I need to document this function"

def process(data, opts=None):
    # complex logic
    pass

1. Agent analyzes function
2. doc-template infer function process
3. Generates template with inferred types, descriptions
4. Presents to user
5. "Fill in the descriptions and I'll add it"
```

### Improving Documentation Coverage

```python
# Agent: "Your project has 45% documentation coverage"

1. doc-template generate-module mymodule --undocumented-only
2. Generates templates for all undocumented functions
3. "Fill in these templates to improve coverage"
```

### Standardizing Documentation Style

```python
# Agent: "Inconsistent documentation style"

1. Define template standard
2. doc-template generate-module mymodule --apply-standard
3. Regenerates all documentation with consistent style
4. "Review and commit these changes"
```

### Code Review Assistance

```python
# Agent: "PR changes function signature"

1. Detect signature change
2. doc-template update function mymodule.process --from-signature
3. Updates documentation to match new signature
4. "Documentation updated to match new parameters"
```

## Template Management

### List Templates

```bash
doc-template list
```

Output:
```
Built-in templates:
  - basic
  - full
  - sdk

Custom templates:
  - my-function
  - data-class
```

### Show Template

```bash
doc-template show full
```

Displays template content.

### Copy Template

```bash
doc-template copy full my-full
```

Creates copy of template for customization.

### Delete Template

```bash
doc-template delete my-template
```

Removes custom template.

## Template Best Practices

### Naming Conventions

```bash
# Function names: verb_noun
doc-template generate function --name process_data

# Class names: Noun
doc-template generate class --name DataProcessor
```

### Category Selection

```bash
# Use standard categories
doc-template generate function --name process --category "data-processing"

# Custom categories
doc-template generate function --name process --category "etl/extract"
```

### Documentation Style

```bash
# Google style
doc-template generate function --name process --docstyle google

# NumPy style
doc-template generate function --name process --docstyle numpy

# reST style
doc-template generate function --name process --docstyle rest
```

## Template API

```python
from docs_cli.template import TemplateEngine

engine = TemplateEngine()

# Generate template
template = engine.generate_function(
    name="process_data",
    params=["data", "validate=True"],
    returns="DataFrame"
)

# Customize template
template.add_category("data-processing")
template.add_note("info", "This modifies in place")

# Get template code
code = template.render()

# Write to file
template.write_to_file("mymodule.py")
```

## Template Plugins

### Load External Template

```bash
doc-template install https://example.com/templates/company-standards.py
```

Installs template from URL.

### Template Marketplace

```bash
doc-template search pandas-style
```

Searches for templates matching "pandas-style".

## Template Diff

### Compare with Existing

```bash
doc-template diff mymodule.process --template full
```

Shows differences between existing documentation and template:
```diff
+ @category("data-processing")
+ @note("info", "This modifies in place")
  def process_data(data):
-     """Process data."""
+     """
+     Process input data.
+
+     Parameters
+     ----------
+     data : DataFrame
+         Input data
+     """
      pass
```

### Apply Template Changes

```bash
doc-template apply mymodule.process --template full
```

Updates function with template additions while preserving existing content.

## Template Statistics

```bash
doc-template stats mypackage
```

Output:
```json
{
  "total_elements": 45,
  "documented": 23,
  "need_template": 22,
  "coverage": "51%",
  "recommended_templates": {
    "functions": 18,
    "classes": 4
  }
}
```
