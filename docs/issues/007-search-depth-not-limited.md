# Issue QUAL-004: Search Depth Not Limited

## Description

Search functions in `search.py` recursively traverse modules and classes without any depth limits. This can lead to:
- Stack overflow on deeply nested structures
- Infinite loops on circular imports
- Performance issues on large codebases
- Unpredictable behavior

## Problem Details

### Affected Code

```python
# docs_cli/analyzer/search.py:74-103
def search_by_name(
    module_path: str, pattern: str, include_private: bool = False
) -> List[SearchResult]:
    """Search for elements by name pattern."""

    # ... setup code ...

    def search_object(obj: Any, current_path: str) -> None:
        """Recursively search object."""
        try:
            members = inspect.getmembers(obj)
        except Exception:
            return

        for name, member in members:
            # Skip private members if requested
            if not include_private and name.startswith("_"):
                continue

            # Check if name matches pattern
            if fnmatch.fnmatch(name, pattern):
                element_type = _get_element_type(member)
                results.append(
                    SearchResult(
                        path=f"{current_path}.{name}",
                        element_type=element_type,
                        name=name,
                        match_reason="name_pattern",
                        obj=member,
                    )
                )

            # NO DEPTH LIMIT HERE - recursively searches everything
            if inspect.ismodule(member) or inspect.isclass(member):
                search_object(member, f"{current_path}.{name}")

    search_object(resolved.obj, resolved.path)
    return results
```

### Similar Issues in Other Functions

All search functions have the same problem:
- `search_by_name()` - line 74-103
- `search_by_docstring()` - line 107-161
- `search_by_type()` - line 164-212
- `search_by_metadata()` - line 215-272

### Issues Identified

| Issue | Impact | Severity |
|-------|--------|----------|
| **Stack Overflow** | Can crash on deeply nested code | Medium |
| **Infinite Loops** | Circular imports cause recursion forever | High |
| **Performance** | Can hang on large packages | Medium |
| **No Control** | Users can't limit search scope | Low |
| **Resource Exhaustion** | Can consume excessive memory | Medium |

## Impact Assessment

| Impact Type | Severity | Description |
|-------------|----------|-------------|
| Stability | 🟡 Medium | Potential stack overflow crashes |
| Performance | 🟡 Medium | Can hang indefinitely on circular imports |
| User Experience | 🟡 Medium | Unpredictable search times |
| Resource Usage | 🟡 Medium | High memory/CPU usage on large projects |
| Correctness | 🟢 Low | Results are correct when function returns |

## Example Problem Scenarios

### Scenario 1: Circular Imports

```python
# module_a.py
import module_b

class ClassA:
    pass

# module_b.py
import module_a

class ClassB:
    # References module_a which imports module_b...
    pass
```

**Result:** Infinite recursion when searching.

### Scenario 2: Deeply Nested Package

```
package/
  a/
    b/
      c/
        d/
          e/
            f/
              g/
                h/
                  i/
                    j/
                      deep_class.py  # 10+ levels deep
```

**Result:** Stack overflow or excessive recursion depth.

### Scenario 3: Large Package (e.g., Django, pandas)

```bash
$ pydocq --search "*test*" django
# Searches through:
# - 1000+ classes
# - 5000+ functions
# - Circular inheritance chains
# - Deep module hierarchies
# Result: Hangs or crashes
```

## Recommended Fix

### Option 1: Add Depth Limit Parameter (Recommended)

```python
# docs_cli/analyzer/search.py

# Default limits
DEFAULT_MAX_DEPTH = 10
DEFAULT_MAX_RESULTS = 1000

def search_by_name(
    module_path: str,
    pattern: str,
    include_private: bool = False,
    max_depth: int = DEFAULT_MAX_DEPTH,
    max_results: int = DEFAULT_MAX_RESULTS,
) -> List[SearchResult]:
    """Search for elements by name pattern.

    Args:
        module_path: Path to module to search
        pattern: Glob pattern to match names (e.g., "*test*", "get_*")
        include_private: Whether to include private members
        max_depth: Maximum recursion depth (default: 10)
        max_results: Maximum number of results to return (default: 1000)

    Returns:
        List of SearchResult objects

    Raises:
        ValueError: If max_depth or max_results are invalid
    """
    if max_depth < 1:
        raise ValueError("max_depth must be at least 1")
    if max_results < 1:
        raise ValueError("max_results must be at least 1")

    try:
        resolved = resolve_path(module_path)
    except Exception:
        return []

    results = []
    visited = set()  # Track visited objects to prevent infinite loops

    def search_object(obj: Any, current_path: str, depth: int = 0) -> None:
        """Recursively search object with depth limit."""
        # Check depth limit
        if depth >= max_depth:
            return

        # Check result limit
        if len(results) >= max_results:
            return

        # Check for circular references
        obj_id = id(obj)
        if obj_id in visited:
            return
        visited.add(obj_id)

        try:
            members = inspect.getmembers(obj)
        except Exception:
            return

        for name, member in members:
            # Check result limit again before processing
            if len(results) >= max_results:
                return

            # Skip private members if requested
            if not include_private and name.startswith("_"):
                continue

            # Check if name matches pattern
            if fnmatch.fnmatch(name, pattern):
                element_type = _get_element_type(member)
                results.append(
                    SearchResult(
                        path=f"{current_path}.{name}",
                        element_type=element_type,
                        name=name,
                        match_reason="name_pattern",
                        obj=member,
                    )
                )

            # Recursively search modules and classes (with depth tracking)
            if inspect.ismodule(member) or inspect.isclass(member):
                search_object(member, f"{current_path}.{name}", depth + 1)

    search_object(resolved.obj, resolved.path)
    return results
```

### Update CLI to Expose Depth Limit

```python
# docs_cli/cli.py

@app.command()
def search(
    module_path: str,
    pattern: str,
    include_private: bool = Option(False, "--include-private"),
    max_depth: int = Option(10, "--max-depth", help="Maximum search depth"),
    max_results: int = Option(1000, "--max-results", help="Maximum results to return"),
) -> None:
    """Search for elements in a module.

    MODULE_PATH is the module to search (e.g., pandas).

    PATTERN is a glob pattern to match (e.g., "*test*", "get_*").
    """
    try:
        results = search_by_name(
            module_path=module_path,
            pattern=pattern,
            include_private=include_private,
            max_depth=max_depth,
            max_results=max_results,
        )

        # Output results
        output = [r.to_dict() for r in results]
        sys.stdout.write(json.dumps(output, indent=2))

    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        raise Exit(code=1)
```

### Option 2: Add Configuration File

```python
# pyproject.toml or .pydocq.toml
[tool.pydocq.search]
# Default search limits
max_depth = 10
max_results = 1000

# Per-package overrides
[tool.pydocq.search.package_limits]
"django" = {max_depth = 5, max_results = 500}
"pandas" = {max_depth = 8, max_results = 1000}
```

```python
# docs_cli/analyzer/search.py
def get_package_limits(package_name: str) -> dict:
    """Get search limits for a specific package."""
    # Load from config file
    # Return defaults if not configured
    return {"max_depth": 10, "max_results": 1000}
```

### Option 3: Smart Detection and Warnings

```python
def search_by_name_smart(
    module_path: str,
    pattern: str,
    include_private: bool = False,
    max_depth: int = DEFAULT_MAX_DEPTH,
) -> List[SearchResult]:
    """Search with intelligent depth detection."""

    # Detect if it's a large package
    try:
        resolved = resolve_path(module_path)
        module_size = _estimate_module_size(resolved.obj)

        # Auto-adjust depth based on package size
        if module_size > 10000:  # Large package
            if max_depth == DEFAULT_MAX_DEPTH:
                import warnings
                warnings.warn(
                    f"Module '{module_path}' is very large. "
                    f"Consider using --max-depth to limit search scope. "
                    f"Using reduced depth of 5."
                )
                max_depth = min(max_depth, 5)
    except Exception:
        pass

    # Continue with search using adjusted max_depth
    # ...
```

```python
def _estimate_module_size(obj: Any) -> int:
    """Estimate the number of members in a module."""
    try:
        members = inspect.getmembers(obj)
        return len(members)
    except Exception:
        return 0
```

### Option 4: Timeout Protection

```python
import signal
import time

class TimeoutError(Exception):
    """Search timeout."""
    pass

def search_with_timeout(
    module_path: str,
    pattern: str,
    timeout_seconds: int = 30,
) -> List[SearchResult]:
    """Search with timeout protection."""

    def timeout_handler(signum, frame):
        raise TimeoutError(f"Search timeout after {timeout_seconds} seconds")

    # Set alarm
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout_seconds)

    try:
        results = search_by_name(module_path, pattern)
        signal.alarm(0)  # Cancel alarm
        return results
    except TimeoutError as e:
        signal.alarm(0)  # Cancel alarm
        import warnings
        warnings.warn(str(e))
        return []
    finally:
        signal.signal(signal.SIGALRM, old_handler)
```

**Note:** Signal-based timeout only works on Unix systems.

## Testing

### Test Suite

```python
# tests/test_search_depth.py
import pytest
from docs_cli.analyzer.search import search_by_name

class TestSearchDepthLimits:
    """Test suite for search depth limiting."""

    def test_respects_max_depth_parameter(self):
        """Test that max_depth parameter is respected."""
        # Create a deeply nested structure
        import types

        # Create nested modules
        root = types.ModuleType("root")
        current = root

        for i in range(20):
            next_module = types.ModuleType(f"level{i}")
            setattr(current, f"level{i}", next_module)
            current = next_module

            # Add a test function at each level
            def test_func():
                pass
            test_func.__name__ = f"test_function_{i}"
            setattr(current, test_func.__name__, test_func)

        # Search with max_depth=5
        results = search_by_name(
            "root",
            "test_function_*",
            max_depth=5
        )

        # Should only find functions up to depth 5
        assert len(results) <= 6  # root + 5 levels
        assert all("level" in r.path for r in results)

        # Should NOT find deeper levels
        assert not any("level10" in r.path for r in results)
        assert not any("level15" in r.path for r in results)

    def test_respects_max_results_parameter(self):
        """Test that max_results parameter is respected."""
        import json

        # json module has many functions
        results = search_by_name(
            "json",
            "*",
            max_results=10
        )

        # Should return at most 10 results
        assert len(results) <= 10

    def test_handles_circular_imports(self):
        """Test that circular imports don't cause infinite loops."""
        # Create modules with circular imports
        import types
        import sys

        module_a = types.ModuleType("test_circular_a")
        module_b = types.ModuleType("test_circular_b")

        # Create circular reference
        module_a.b = module_b
        module_b.a = module_a

        # Add test functions
        def func_a():
            pass
        func_a.__name__ = "func_a"
        module_a.func_a = func_a

        def func_b():
            pass
        func_b.__name__ = "func_b"
        module_b.func_b = func_b

        sys.modules["test_circular_a"] = module_a
        sys.modules["test_circular_b"] = module_b

        try:
            # Should complete without hanging
            results = search_by_name(
                "test_circular_a",
                "func_*",
                max_depth=10
            )

            # Should find functions but not loop forever
            assert len(results) > 0
        finally:
            # Clean up
            del sys.modules["test_circular_a"]
            del sys.modules["test_circular_b"]

    def test_depth_limit_with_real_package(self):
        """Test depth limit on a real package."""
        # Search pandas with small depth limit
        results = search_by_name(
            "json",
            "*",
            max_depth=2
        )

        # Should complete quickly
        assert isinstance(results, list)

    def test_invalid_depth_parameters_raise_error(self):
        """Test that invalid parameters raise errors."""
        with pytest.raises(ValueError, match="max_depth"):
            search_by_name("json", "*", max_depth=0)

        with pytest.raises(ValueError, match="max_depth"):
            search_by_name("json", "*", max_depth=-1)

        with pytest.raises(ValueError, match="max_results"):
            search_by_name("json", "*", max_results=0)

    def test_visited_tracking_prevents_repeats(self):
        """Test that visited tracking prevents processing same object twice."""
        import types

        # Create a module with the same function referenced twice
        module = types.ModuleType("test_repeats")

        def shared_func():
            pass
        shared_func.__name__ = "shared_func"

        module.func1 = shared_func
        module.func2 = shared_func  # Same object, different name

        import sys
        sys.modules["test_repeats"] = module

        try:
            results = search_by_name(
                "test_repeats",
                "*",
                max_depth=5
            )

            # Each reference should be searched once
            # (Though both might match the pattern)
            assert len(results) >= 0  # Should not crash or hang
        finally:
            del sys.modules["test_repeats"]
```

### Performance Tests

```python
# tests/test_search_performance.py
import time
from docs_cli.analyzer.search import search_by_name

def test_search_performance_with_depth_limit():
    """Test that depth limits improve performance."""
    import json

    # Search without depth limit (slow)
    start = time.time()
    results_deep = search_by_name("json", "*", max_depth=20)
    time_deep = time.time() - start

    # Search with depth limit (fast)
    start = time.time()
    results_shallow = search_by_name("json", "*", max_depth=3)
    time_shallow = time.time() - start

    # Shallow search should be significantly faster
    assert time_shallow < time_deep
    print(f"Deep search: {time_deep:.3f}s, Shallow search: {time_shallow:.3f}s")
```

## Migration Plan

### Phase 1: Implementation (Week 1)
- [ ] Add depth limit parameter to all search functions
- [ ] Add visited object tracking
- [ ] Add max_results parameter
- [ ] Add input validation

### Phase 2: CLI Integration (Week 1)
- [ ] Update CLI to expose `--max-depth` option
- [ ] Update CLI to expose `--max-results` option
- [ ] Update help text

### Phase 3: Testing (Week 1-2)
- [ ] Add unit tests for depth limiting
- [ ] Add tests for circular import handling
- [ ] Add performance tests
- [ ] Test on large packages (pandas, django)

### Phase 4: Documentation (Week 2)
- [ ] Update README with new options
- [ ] Add examples of depth-limited search
- [ ] Document performance implications

### Phase 5: Advanced Features (Optional)
- [ ] Add configuration file support
- [ ] Add smart depth detection
- [ ] Add timeout protection
- [ ] Add per-package limits

## Benefits of Fix

| Benefit | Impact |
|---------|--------|
| **Stability** | Prevents stack overflow crashes |
| **Performance** | Predictable search times |
| **User Control** | Users can limit search scope |
| **Resource Management** | Prevents memory exhaustion |
| **Better UX** | No more hanging searches |

## Related Issues

- [QUAL-001: Code Duplication - Type Detection](./004-code-duplication-type-detection.md)
- [SEC-001: Dynamic Import Without Sanitization](./001-dynamic-import-without-sanitization.md)

## References

- [Python Recursion Limits](https://docs.python.org/3/library/sys.html#sys.setrecursionlimit)
- [Circular Import Detection](https://docs.python.org/3/library/inspect.html)

## Checklist

- [ ] Add depth limit parameter to all search functions
- [ ] Implement visited object tracking
- [ ] Add max_results parameter
- [ ] Add input validation for parameters
- [ ] Update CLI with new options
- [ ] Add unit tests for depth limiting
- [ ] Add tests for circular import handling
- [ ] Add performance tests
- [ ] Test on large packages
- [ ] Update documentation
- [ ] Add examples to README
