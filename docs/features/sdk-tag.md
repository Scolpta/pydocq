# Tag Decorator

Add freeform tags to elements for flexible filtering and organization.

## Usage

```python
from docs_cli import tag

@tag("experimental")
@tag("unstable")
def new_feature():
    pass

@tag("performance-critical")
@tag("optimized")
def fast_process():
    pass
```

## Examples

### Single Tag

```python
@tag("experimental")
def new_api():
    pass
```

Query:
```bash
doc mymodule.new_api --tags
```

Output:
```json
{
  "path": "mymodule.new_api",
  "tags": ["experimental"]
}
```

### Multiple Tags

```python
@tag("experimental")
@tag("unstable")
@tag("may-change")
def beta_feature():
    pass
```

Or with list:
```python
@tag(["experimental", "unstable", "may-change"])
def beta_feature():
    pass
```

### Tag with Values

```python
@tag("deprecated:v2.0")
@tag("remove:v3.0")
def old_func():
    pass

@tag("performance:O(n)")
@tag("memory:low")
def efficient_func():
    pass
```

Query by tag value:
```bash
doc mypackage --tag "deprecated:*"
```

Returns all elements with `deprecated:` prefix.

### Performance Tags

```python
@tag("perf:fast")
@tag("perf:O(n)")
def quick_function():
    pass

@tag("perf:slow")
@tag("perf:O(n²)")
def slow_function():
    pass
```

### Stability Tags

```python
@tag("stable")
def mature_api():
    pass

@tag("experimental")
@tag("unstable")
def new_api():
    pass

@tag("deprecated")
def old_api():
    pass
```

### Domain Tags

```python
@tag("domain:ml")
@tag("domain:classification")
def classify():
    pass

@tag("domain:cv")
@tag("domain:detection")
def detect():
    pass
```

### Team Ownership Tags

```python
@tag("team:data")
@tag("team:data-platform")
def etl_process():
    pass

@tag("team:ml")
def train_model():
    pass
```

### Usage Context Tags

```python
@tag("use-case:batch")
def batch_process():
    pass

@tag("use-case:realtime")
@tag("use-case:streaming")
def stream_process():
    pass
```

### Internal vs Public

```python
@tag("public")
def user_api():
    pass

@tag("internal")
@tag("private")
def _internal_helper():
    pass
```

### Complexity Tags

```python
@tag("complexity:simple")
def simple_func():
    pass

@tag("complexity:medium")
def medium_func():
    pass

@tag("complexity:complex")
@tag("complexity:needs-docs")
def complex_func():
    pass
```

## Query by Tags

### Find by Tag

```bash
doc mypackage --tag experimental
```

Output:
```json
{
  "tag": "experimental",
  "matches": [
    {"path": "mypackage.beta_feature", "tags": ["experimental", "unstable"]},
    {"path": "mypackage.new_api", "tags": ["experimental"]}
  ]
}
```

### Find by Multiple Tags

```bash
doc mypackage --tag experimental --tag unstable
```

Returns elements with BOTH tags (AND logic).

### Find Any Tag

```bash
doc mypackage --tag-any experimental unstable
```

Returns elements with EITHER tag (OR logic).

### Tag Negation

```bash
doc mypackage --tag-any --not-tag deprecated
```

Returns elements with any tag EXCEPT deprecated.

### Tag Wildcards

```bash
doc mypackage --tag "perf:*"
```

Returns all performance-related tags:
- perf:fast
- perf:slow
- perf:O(n)
- etc.

```bash
doc mypackage --tag "domain:*"
```

Returns all domain-specific functions.

### Tag Search

```bash
doc mypackage --tag-contains "exp"
```

Returns elements with tags containing "exp":
- experimental
- experience
- expert

## Tag Prefixes (Conventions)

### Stability
- `stable` - Stable API
- `experimental` - Experimental, may change
- `unstable` - Known to be unstable
- `deprecated` - Deprecated
- `removed` - Removed but not deleted

### Performance
- `perf:fast` - Fast execution
- `perf:slow` - Slow execution
- `perf:O(n)` - Linear complexity
- `perf:O(n²)` - Quadratic complexity
- `perf:memory-low` - Low memory usage
- `perf:memory-high` - High memory usage

### Lifecycle
- `lifecycle:alpha` - Alpha stage
- `lifecycle:beta` - Beta stage
- `lifecycle:stable` - Stable
- `lifecycle:legacy` - Legacy

### Domain
- `domain:ml` - Machine learning
- `domain:cv` - Computer vision
- `domain:nlp` - Natural language processing
- `domain:data` - Data processing
- `domain:api` - API/HTTP

### Visibility
- `public` - Public API
- `internal` - Internal use only
- `private` - Private, should not be used externally

### Use Case
- `use-case:batch` - Batch processing
- `use-case:realtime` - Real-time processing
- `use-case:streaming` - Streaming data
- `use-case:interactive` - Interactive use

## Tag Statistics

```bash
doc mypackage --tag-stats
```

Output:
```json
{
  "total_tagged": 45,
  "total_untagged": 12,
  "tags": {
    "experimental": 8,
    "stable": 25,
    "deprecated": 5,
    "perf:fast": 12,
    "perf:slow": 3,
    "domain:ml": 10,
    "domain:data": 15
  }
}
```

## Tag Cloud

```bash
doc mypackage --tag-cloud
```

Output:
```json
{
  "tags": [
    {"tag": "stable", "count": 25, "size": "large"},
    {"tag": "experimental", "count": 8, "size": "medium"},
    {"tag": "perf:fast", "count": 12, "size": "medium"},
    {"tag": "deprecated", "count": 5, "size": "small"}
  ]
}
```

## Use Cases for Agents

### Feature Discovery

```python
# Agent: "What experimental features are available?"

1. doc mypackage --tag experimental
2. Gets list of experimental functions
3. Warns user: "These are experimental and may change"
4. "new_api, beta_feature, alpha_transform are experimental"
```

### Avoiding Deprecated Code

```python
# Agent: "Show me stable functions only"

1. doc mypackage --tag stable --not-tag deprecated
2. Filters out experimental and deprecated
3. Only shows stable APIs
4. Can recommend confidently
```

### Performance Guidance

```python
# Agent: "I need fast functions"

1. doc mypackage --tag "perf:fast"
2. Gets list of fast functions
3. "quick_function, fast_process are optimized for speed"
```

### Domain-Specific Help

```python
# Agent: "What ML functions are available?"

1. doc mypackage --tag "domain:ml"
2. Gets ML-specific functions
3. "train_model, predict, evaluate are ML functions"
```

### Understanding Maturity

```python
# Agent: "Is this API safe to use?"

1. doc mymodule.new_api --tags
2. Sees: ["experimental", "unstable"]
3. Warns: "This API is experimental and unstable, may change"
```

### Team Routing

```python
# Agent: "Who maintains this?"

1. doc mymodule.etl_process --tags
2. Sees: ["team:data", "team:data-platform"]
3. "This is maintained by the data-platform team"
```

## Tag Validation

### Require Tags

```python
from docs_cli import require_tags

@require_tags(["public", "stable"])
def public_api():
    pass

# If function doesn't have these tags, linting fails
```

### Tag Whitelist

```python
# .docs-cli/config.yaml
tags:
  allowed:
    - stable
    - experimental
    - deprecated
    - "perf:*"
    - "domain:*"
  forbidden:
    - "FIXME"
    - "TODO"
```

CLI warns if forbidden tags are used.

## Tag Management

### Add Tag

```bash
doc mymodule.func --add-tag "needs-review"
```

### Remove Tag

```bash
doc mymodule.func --remove-tag "experimental"
```

### Rename Tag

```bash
doc mypackage --rename-tag "unstable" -> "beta"
```

Renames tag across all elements.

## Combining with Other Decorators

```python
@tag("experimental")
@category("data-processing")
@deprecated("Use new_func instead")
@author("data-team")
def process():
    pass
```

All metadata is queryable together.

## Tag Suggestions

```bash
doc mypackage --suggest-tags
```

Analyzes code and suggests tags:
```json
{
  "suggestions": [
    {
      "path": "mymodule.process",
      "suggested_tags": ["perf:slow", "complexity:complex"],
      "reason": "High cyclomatic complexity (15)"
    },
    {
      "path": "mymodule._helper",
      "suggested_tags": ["internal"],
      "reason": "Name starts with underscore"
    }
  ]
}
```

## Storage

Tags stored on function:

```python
>>> func.__doc_tags__
['experimental', 'unstable']
```

Accessible via CLI.

## Tag Hierarchies

```python
@tag("ml")
@tag("ml:classification")
@tag("ml:classification:binary")
def binary_classifier():
    pass
```

Query:
```bash
doc mypackage --tag "ml:*"
```

Returns all ML-related functions.

## Tag Expiration

```python
@tag("experimental", expires="2024-06-01")
def new_feature():
    pass
```

CLI can warn if tag is expired:
```bash
doc mymodule.new_feature
# Warning: Tag 'experimental' expired on 2024-06-01
```

## Bulk Tagging

```bash
doc mypackage --tag "experimental" --apply-to "mymodule.new_*"
```

Adds tag to all functions matching pattern `new_*`.
