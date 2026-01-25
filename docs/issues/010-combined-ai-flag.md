# Issue FEAT-003: Combined `--for-ai` Flag

## Description

Add a convenience `--for-ai` flag that combines all AI-optimized output options into a single command. This provides a consistent interface for AI agents and reduces CLI complexity for agent developers.

## Problem Details

### Current State

AI agents need to remember multiple flags to get optimized output:

```bash
# What agents need today (verbose and error-prone)
pydocq pandas.DataFrame.merge \
  --format llm \
  --include-metadata \
  --include-source \
  --verbose
```

**Problems:**
| Problem | Impact | Severity |
|---------|--------|----------|
| **Verbose** | Agents must specify many flags | Medium |
| **Inconsistent** | Different agents use different flags | Medium |
| **Discovery** | Hard to find all AI-relevant options | Medium |
| **Maintenance** | Adding new AI features requires updating all agents | Low |

### Desired State

```bash
# What agents should use
pydocq pandas.DataFrame.merge --for-ai
```

Simple, consistent, and future-proof.

## Impact Assessment

| Impact Type | Severity | Description |
|-------------|----------|-------------|
| Developer Experience | 🟢 High | One flag instead of many |
| Consistency | 🟢 High | Standardized AI agent interface |
| Maintenance | 🟢 High | Add features to --for-ai, agents auto-benefit |
| Documentation | 🟢 High | Clear statement of AI-first design |
| Backward Compatibility | 🟢 Low | New flag, existing behavior unchanged |

## Recommended Implementation

### Option 1: Boolean Flag (Recommended)

```python
# pydocq/cli.py

@app.command()
def query(
    target: str,
    for_ai: bool = Option(
        False,
        "--for-ai",
        help="Optimize output for AI agent consumption (enables llm format, metadata, source, warnings)"
    ),
    format: str = Option("json", "--format", "-f", help="Output format"),
    verbose: bool = Option(False, "--verbose", "-V", help="Verbose output"),
    include_metadata: bool = Option(False, "--include-metadata", "-m", help="Include SDK metadata"),
    include_source: bool = Option(False, "--include-source", "-s", help="Include source location"),
    # ... other options
) -> None:
    """Query Python package documentation.

    TARGET is the package or element to query (e.g., pandas.DataFrame).

    Examples:
        doc pandas.DataFrame
        doc pandas.DataFrame.merge --for-ai
    """
    # Handle --for-ai flag
    if for_ai:
        # Enable all AI-optimized options
        from pydocq.analyzer.output_formats import format_llm

        # Use LLM format
        output_dict = format_llm(inspected)

        # Always include metadata for AI
        if inspected.sdk_metadata:
            output_dict["sdk_metadata"] = inspected.sdk_metadata

        # Always include source for context
        if inspected.source_location:
            output_dict["source_location"] = {
                "file": inspected.source_location.file_path,
                "line": inspected.source_location.lineno
            }

        # Include warnings/deprecations
        if inspected.sdk_metadata and "deprecated" in inspected.sdk_metadata:
            output_dict["warnings"] = {
                "deprecated": True,
                "reason": inspected.sdk_metadata["deprecated"].get("reason"),
                "use_instead": inspected.sdk_metadata["deprecated"].get("use_instead")
            }

        # Include examples if available
        if inspected.sdk_metadata and "example" in inspected.sdk_metadata:
            output_dict["examples"] = [inspected.sdk_metadata["example"]]

        sys.stdout.write(json.dumps(output_dict, indent=2))
        return

    # ... rest of existing logic
```

**Usage:**
```bash
# Simple usage for AI agents
pydocq json.dump --for-ai

# Output includes:
# - LLM-optimized format
# - SDK metadata
# - Source location
# - Warnings/deprecations
# - Examples
```

### Option 2: Preset-Based

Allow multiple presets with different optimizations:

```python
# pydocq/cli.py

@app.command()
def query(
    target: str,
    preset: str = Option(
        None,
        "--preset",
        help="Output preset (default, for-ai, minimal, verbose)"
    ),
    # ... existing options
) -> None:
    """Query Python package documentation."""
    # Handle presets
    if preset == "for-ai":
        # Enable AI optimizations
        # ...
    elif preset == "minimal":
        # Enable minimal output
        # ...
    elif preset == "verbose":
        # Enable verbose output
        # ...
```

**Usage:**
```bash
pydocq json.dump --preset for-ai
```

### Option 3: Config File

```python
# pyproject.toml
[tool.pydocq]
default_preset = "for-ai"

[tool.pydocq.presets.for-ai]
format = "llm"
include_metadata = true
include_source = true
include_warnings = true
```

## Output Examples

### Standard Query vs For-AI

**Standard output:**
```bash
$ pydocq json.dump
```
```json
{
  "path": "json.dump",
  "type": "function",
  "signature": {...},
  "docstring": {...}
}
```

**--for-ai output:**
```bash
$ pydocq json.dump --for-ai
```
```json
{
  "path": "json.dump",
  "type": "function",
  "summary": "Serialize Python object to JSON file",
  "key_params": [
    {"name": "obj", "type": "Any", "required": true},
    {"name": "fp", "type": "SupportsWrite[str]", "required": true}
  ],
  "common_usage": "Save data to JSON file",
  "example_concise": "json.dump(data, open('file.json', 'w'))",
  "common_pitfalls": [
    "fp must have a .write() method",
    "obj must be JSON-serializable"
  ],
  "alternatives": [
    {"path": "json.dumps", "reason": "Returns string instead of writing to file"}
  ],
  "source_location": {
    "file": "/usr/lib/python3.11/json/__init__.py",
    "line": 180
  },
  "token_count": 52
}
```

### With SDK Metadata

**With @example decorator in source:**
```python
@metadata(category="serialization", version="1.0")
@example("json.dump(data, open('out.json', 'w'))", "Basic usage")
def dump(obj, fp, **kwargs):
    """Serialize obj to JSON file."""
    ...
```

**Output:**
```bash
$ pydocq json.dump --for-ai
```
```json
{
  "path": "json.dump",
  "summary": "Serialize Python object to JSON file",
  "key_params": [...],
  "sdk_metadata": {
    "category": "serialization",
    "version": "1.0"
  },
  "examples": [
    {
      "code": "json.dump(data, open('out.json', 'w'))",
      "description": "Basic usage"
    }
  ],
  "source_location": {...},
  "token_count": 68
}
```

### With Deprecation Warning

```python
@deprecated("Use new_func instead", since="1.0", version="2.0")
def old_func():
    """Old function."""
    pass
```

**Output:**
```bash
$ pydocq old_func --for-ai
```
```json
{
  "path": "old_func",
  "summary": "Old function",
  "warnings": {
    "deprecated": true,
    "reason": "Use new_func instead",
    "since": "1.0",
    "removed_in": "2.0",
    "alternatives": ["new_func"]
  },
  "alternatives": [
    {"path": "new_func", "reason": "Replacement for deprecated old_func"}
  ],
  "token_count": 45
}
```

## Testing

### Unit Tests

```python
# tests/test_for_ai_flag.py
import pytest
from typer.testing import CliRunner
from pydocq.cli import app

runner = CliRunner()

class TestForAIFlag:
    """Test suite for --for-ai flag."""

    def test_enables_llm_format(self):
        """Test that --for-ai enables LLM format."""
        result = runner.invoke(app, ["json.dump", "--for-ai"])
        output = json.loads(result.stdout)

        # Should have LLM format fields
        assert "summary" in output
        assert "key_params" in output
        assert "example_concise" in output
        assert "token_count" in output

    def test_includes_metadata(self):
        """Test that --for-ai includes SDK metadata."""
        result = runner.invoke(app, ["my_module.my_func", "--for-ai"])
        output = json.loads(result.stdout)

        # Should include metadata if available
        # (assuming my_module.my_func has SDK metadata)
        assert "sdk_metadata" in output or output.get("sdk_metadata") is None

    def test_includes_source_location(self):
        """Test that --for-ai includes source location."""
        result = runner.invoke(app, ["json.dump", "--for-ai"])
        output = json.loads(result.stdout)

        # Should include source location
        assert "source_location" in output
        assert "file" in output["source_location"]
        assert "line" in output["source_location"]

    def test_includes_deprecation_warnings(self):
        """Test that --for-ai includes deprecation warnings."""
        result = runner.invoke(app, ["deprecated_func", "--for-ai"])
        output = json.loads(result.stdout)

        # Should include warnings if deprecated
        if "warnings" in output:
            assert output["warnings"].get("deprecated") == True

    def test_flag_overrides_format(self):
        """Test that --for-ai overrides --format."""
        result = runner.invoke(app, ["json.dump", "--format", "raw", "--for-ai"])
        output = json.loads(result.stdout)

        # Should use LLM format despite --format raw
        assert "summary" in output  # LLM format field

    def test_combines_with_other_flags(self):
        """Test that --for-ai can combine with other flags."""
        result = runner.invoke(app, ["json.dump", "--for-ai", "--include-private"])
        # Should work without error
        assert result.exit_code == 0
```

## Implementation Priority

1. **Immediate (P0):** Implement `--for-ai` boolean flag
2. **Immediate (P0):** Add LLM format integration
3. **Short-term (P1):** Add SDK metadata inclusion
4. **Short-term (P1):** Add source location inclusion
5. **Testing (P1):** Add comprehensive test suite
6. **Documentation (P1):** Update README

## Migration Plan

### Phase 1: Core Implementation (Week 1)
- [ ] Add `--for-ai` flag to CLI
- [ ] Integrate with `format_llm()`
- [ ] Add SDK metadata inclusion
- [ ] Add source location inclusion

### Phase 2: Enhancement (Week 1-2)
- [ ] Add deprecation warning extraction
- [ ] Add examples inclusion
- [ ] Add alternatives suggestion
- [ ] Test on real packages

### Phase 3: Testing (Week 2)
- [ ] Add unit tests for flag behavior
- [ ] Add integration tests
- [ ] Test flag combinations
- [ ] Benchmark output quality

### Phase 4: Documentation (Week 2)
- [ ] Update README with --for-ai examples
- [ ] Document for AI agent developers
- [ ] Add migration guide for existing agents
- [ ] Create tutorial video

## Benefits

| Benefit | Impact |
|---------|--------|
| **Simplicity** | One flag instead of many |
| **Consistency** | Standardized agent interface |
| **Future-Proof** | New features auto-included |
| **Documentation** | Clear AI-first message |
| **Adoption** | Lower barrier for agent developers |

## Related Issues

- [FEAT-002: LLM-Optimized Output Format](./009-llm-output-format.md)
- [FEAT-001: Expose AST Analysis to CLI](./008-expose-ast-analysis-to-cli.md)

## References

- [CLI Interface](../pydocq/cli.py)
- [Output Formats Module](../pydocq/analyzer/output_formats.py)

## Checklist

- [ ] Add `--for-ai` flag to CLI
- [ ] Implement LLM format integration
- [ ] Add SDK metadata inclusion logic
- [ ] Add source location inclusion logic
- [ ] Add deprecation warning extraction
- [ ] Add examples inclusion
- [ ] Add unit tests for flag behavior
- [ ] Add integration tests
- [ ] Test on real packages
- [ ] Update README with examples
- [ ] Document for AI agent developers
- [ ] Create migration guide
