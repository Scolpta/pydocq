# Agent Hooks / Callbacks System

Allow agents to register callbacks for documentation-related events.

## Usage

```python
from docs_cli import hook

@hook.on_query("pandas.DataFrame")
def log_dataframe_query(agent, query):
    """Called when DataFrame is queried"""
    logger.info(f"{agent} queried DataFrame at {query.time}")

@hook.on_deprecated_use
def warn_user(agent, element, context):
    """Called when user tries to use deprecated code"""
    return f"{element.name} is deprecated, use {element.metadata['use_instead']}"
```

## Examples

### Query Hooks

#### Before Query

```python
@hook.before_query
def track_query(agent, query):
    """Track all documentation queries"""
    analytics.track("doc_query", {
        "agent": agent.name,
        "target": query.target,
        "timestamp": query.time
    })
```

#### After Query

```python
@hook.after_query
def log_results(agent, query, result):
    """Log query results"""
    logger.info(f"Query {query.target} returned {len(result)} elements")
```

#### On Specific Element

```python
@hook.on_query("pandas.DataFrame")
def dataframe_accessed(agent, query):
    """DataFrame was queried"""
    notify_data_team(f"DataFrame accessed by {agent.name}")

@hook.on_query("pandas.*.merge")
def merge_accessed(agent, query):
    """Any merge function was queried"""
    record_merge_usage(agent, query)
```

### Deprecation Hooks

#### Before Using Deprecated

```python
@hook.before_deprecated_use
def warn_deprecated(agent, element, context):
    """Warn before using deprecated code"""
    return {
        "warning": f"{element.name} is deprecated since {element.metadata['since']}",
        "alternative": element.metadata.get('use_instead'),
        "severity": "high"
    }
```

#### After Using Deprecated

```python
@hook.after_deprecated_use
def report_deprecated_usage(agent, element, context):
    """Report that deprecated code was used"""
    metrics.increment("deprecated.usage", {
        "element": element.name,
        "agent": agent.name
    })
```

### Missing Parameter Hooks

#### Suggest Values

```python
@hook.on_missing_parameter
def suggest_parameter_value(agent, func, param, context):
    """Suggest parameter value based on context"""
    if param.name == "mode":
        # Analyze context to suggest mode
        if "speed" in context.requirements:
            return "fast"
        elif "accuracy" in context.requirements:
            return "accurate"
        return "auto"
```

#### Validate Parameters

```python
@hook.before_call
def validate_parameters(agent, func, params, context):
    """Validate parameters before function call"""
    if "data" in params:
        data = params["data"]
        if len(data) > 1000000:
            return {
                "warning": "Large dataset detected",
                "suggestion": "Consider using chunked version"
            }
```

### Error Hooks

#### On Error

```python
@hook.on_error
def handle_error(agent, element, error, context):
    """Handle documentation query errors"""
    if isinstance(error, NotFoundError):
        return suggest_alternative(agent, element.name)
    elif isinstance(error, ImportError):
        return install_instructions(element.name)
```

#### On Validation Error

```python
@hook.on_validation_error
def fix_validation_error(agent, func, param, value, error):
    """Suggest fix for validation error"""
    if param.constraints and "choices" in param.constraints:
        return {
            "error": f"Invalid value '{value}'",
            "valid_choices": param.constraints["choices"],
            "suggestion": f"Use one of: {', '.join(param.constraints['choices'])}"
        }
```

### Performance Hooks

#### Before Execution

```python
@hook.before_execution
def check_performance(agent, element, context):
    """Check performance characteristics"""
    perf = element.metadata.get("performance")
    if perf == "slow":
        return {
            "warning": "This function is slow",
            "estimated_time": element.metadata.get("expected_time"),
            "alternative": element.metadata.get("fast_alternative")
        }
```

#### After Execution

```python
@hook.after_execution
def track_performance(agent, element, result, duration_ms):
    """Track actual performance"""
    expected = element.metadata.get("expected_duration_ms")
    if expected and duration_ms > expected * 2:
        logger.warning(f"{element.name} took {duration_ms}ms, expected {expected}ms")
```

### Security Hooks

#### Before Sensitive Operation

```python
@hook.before_sensitive_operation
def check_permissions(agent, element, context):
    """Check permissions for sensitive operations"""
    if "security" in element.tags:
        if not agent.has_permission("sensitive_ops"):
            return {
                "error": "Permission denied",
                "required_permission": "sensitive_ops"
            }
```

#### Log Sensitive Data Access

```python
@hook.on_sensitive_data
def log_sensitive_access(agent, element, data):
    """Log access to sensitive data"""
    security.log("sensitive_data_access", {
        "agent": agent.name,
        "element": element.name,
        "data_type": type(data).__name__
    })
```

### Custom Hooks

#### Define Custom Hook Point

```python
# In your code
from docs_cli import hook_point

@hook_point("before_data_processing")
def process_data(data):
    """Process data with hook point"""
    # Hook will be called here
    result = transform(data)
    return result
```

#### Register Custom Hook

```python
@hook.on("before_data_processing")
def custom_processing(agent, data):
    """Custom hook for data processing"""
    # Modify or validate data
    return validate(data)
```

## Hook Types

### Query Hooks

| Hook | Parameters | When |
|------|------------|------|
| `before_query` | agent, query | Before any query |
| `after_query` | agent, query, result | After query completes |
| `on_query` | agent, query, element | When specific element queried |
| `on_query_failed` | agent, query, error | When query fails |

### Documentation Hooks

| Hook | Parameters | When |
|------|------------|------|
| `on_doc_loaded` | agent, element, doc | When documentation loaded |
| `on_doc_parsed` | agent, element, parsed | After parsing docstring |
| `on_examples_extracted` | agent, element, examples | After examples extracted |

### Function Hooks

| Hook | Parameters | When |
|------|------------|------|
| `before_call` | agent, func, params, context | Before function call |
| `after_call` | agent, func, result, context | After function returns |
| `on_call_failed` | agent, func, error, context | When function raises |

### Lifecycle Hooks

| Hook | Parameters | When |
|------|------------|------|
| `on_agent_start` | agent | When agent starts |
| `on_agent_stop` | agent | When agent stops |
| `on_session_start` | agent, session | When session starts |
| `on_session_end` | agent, session | When session ends |

### Metadata Hooks

| Hook | Parameters | When |
|------|------------|------|
| `on_metadata_access` | agent, element, key | When metadata accessed |
| `on_metadata_update` | agent, element, key, value | When metadata updated |

## Hook Priority

```python
@hook.on_query("pandas.DataFrame", priority=100)
def high_priority_hook(agent, query):
    """Called first"""
    pass

@hook.on_query("pandas.DataFrame", priority=1)
def low_priority_hook(agent, query):
    """Called last"""
    pass
```

Higher priority hooks execute first.

## Hook Chaining

```python
@hook.on_query("pandas.DataFrame", chain=True)
def log_access(agent, query):
    """Log and continue to next hook"""
    logger.info(f"DataFrame accessed by {agent.name}")
    return hook.CONTINUE  # Continue to next hook

@hook.on_query("pandas.DataFrame", chain=True)
def check_permissions(agent, query):
    """Check permissions"""
    if not agent.can_access("DataFrame"):
        return hook.STOP  # Stop chain, don't call other hooks
    return hook.CONTINUE
```

Return values:
- `hook.CONTINUE` - Continue to next hook
- `hook.STOP` - Stop chain
- Return value - Use as result

## Conditional Hooks

```python
@hook.on_query("pandas.DataFrame", condition=lambda agent, q: agent.type == "user")
def user_only_hook(agent, query):
    """Only for user agents"""
    return user_friendly_response()

@hook.on_query("pandas.DataFrame", condition=lambda agent, q: agent.type == "system")
def system_only_hook(agent, query):
    """Only for system agents"""
    return system_response()
```

## Hook Context

```python
@hook.on_query("pandas.DataFrame")
def contextual_hook(agent, query):
    """Hook with access to context"""
    # Access query context
    user_intent = query.context.get("intent")
    previous_queries = query.context.get("history")

    # Modify context
    query.context["hook_called"] = True

    # Return custom response based on context
    if user_intent == "learning":
        return educational_response()
```

## Hook Groups

```python
# Define hook group
@hook.group("data_validation")
class DataValidationHooks:
    @hook.before_call
    def validate_input(self, agent, func, params, context):
        """Validate input data"""
        pass

    @hook.after_call
    def validate_output(self, agent, func, result, context):
        """Validate output data"""
        pass

# Enable/disable entire group
hook.enable_group("data_validation")
hook.disable_group("data_validation")
```

## Hook Storage

### Persistent Hooks

```python
# Save hooks to file
hook.save_hooks("my_hooks.json")

# Load hooks from file
hook.load_hooks("my_hooks.json")
```

### Hook Registry

```python
# List all registered hooks
hooks = hook.list_hooks()

# Get hooks for specific event
df_hooks = hook.get_hooks("on_query", "pandas.DataFrame")

# Remove specific hook
hook.remove_hook(hook_id)
```

## Use Cases for Agents

### Custom Error Handling

```python
@hook.on_error
def custom_error_handler(agent, element, error, context):
    """Custom error handling for agent"""
    if agent.name == "code-assistant":
        return friendly_error_message(error)
    elif agent.name == "debugger":
        return detailed_error_info(error)
```

### Query Analytics

```python
@hook.after_query
def analytics(agent, query, result):
    """Track query patterns"""
    analytics.track("query", {
        "agent": agent.name,
        "target": query.target,
        "results_count": len(result),
        "duration_ms": query.duration
    })
```

### Contextual Help

```python
@hook.on_query("pandas.DataFrame")
def provide_contextual_help(agent, query):
    """Provide contextual help based on user's level"""
    if agent.user_level == "beginner":
        return beginner_guide(query)
    elif agent.user_level == "advanced":
        return advanced_guide(query)
```

### Automated Suggestions

```python
@hook.after_query
def suggest_related(agent, query, result):
    """Suggest related functions"""
    suggestions = find_similar(query.target)
    if suggestions:
        return {
            "results": result,
            "related": suggestions
        }
```

### Performance Monitoring

```python
@hook.after_execution
def monitor_performance(agent, element, result, duration_ms):
    """Monitor function performance"""
    if duration_ms > element.metadata.get("slow_threshold", 1000):
        alert_slow_performance(element, duration_ms)
```

### Security Auditing

```python
@hook.before_sensitive_operation
def audit_access(agent, element, context):
    """Audit access to sensitive operations"""
    security.audit_log({
        "agent": agent.name,
        "operation": element.name,
        "timestamp": datetime.now(),
        "context": context
    })
```

## Hook API

### Register Hook

```python
from docs_cli import hook

hook.register(
    event="on_query",
    handler=my_handler,
    filter="pandas.DataFrame",  # Optional filter
    priority=10
)
```

### Unregister Hook

```python
hook.unregister(handler_id)
```

### Trigger Hook

```python
result = hook.trigger("on_query", agent=agent, query=query)
```

### Check Hook Results

```python
results = hook.get_results("on_query")
```

## Hook Debugging

### Trace Hooks

```bash
doc --trace-hooks
```

Logs all hook executions:
```
[TRACE] Hook log_dataframe_query called for pandas.DataFrame
[TRACE] Hook check_permissions called for pandas.DataFrame
[TRACE] Hook provide_contextual_help called for pandas.DataFrame
```

### Hook Statistics

```bash
doc --hook-stats
```

Output:
```json
{
  "hooks": {
    "on_query": {
      "total_calls": 1234,
      "total_duration_ms": 456,
      "handlers": [
        {"name": "log_dataframe_query", "calls": 123, "avg_duration_ms": 0.5},
        {"name": "check_permissions", "calls": 123, "avg_duration_ms": 0.2}
      ]
    }
  }
}
```

### Hook Profiling

```bash
doc --profile-hooks
```

Shows performance of each hook handler.
