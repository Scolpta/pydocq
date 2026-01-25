# Issue QUAL-001: Code Duplication - Type Detection Logic

## Description

The element type detection logic is duplicated across multiple modules with minor variations. This creates maintenance burden, potential for inconsistencies, and violates the DRY (Don't Repeat Yourself) principle.

## Problem Details

### Duplicated Code Locations

#### Location 1: `docs_cli/analyzer/resolver.py:129-150`
```python
def _determine_element_type(obj: Any) -> ElementType:
    """Determine the type of a Python object.

    Args:
        obj: Python object to classify

    Returns:
        ElementType enum value
    """
    import inspect

    if inspect.ismodule(obj):
        return ElementType.MODULE
    if inspect.isclass(obj):
        return ElementType.CLASS
    if inspect.isfunction(obj):
        return ElementType.FUNCTION
    if inspect.ismethod(obj):
        return ElementType.METHOD
    if isinstance(obj, property):
        return ElementType.PROPERTY
    return ElementType.UNKNOWN
```

#### Location 2: `docs_cli/analyzer/discovery.py:158-177`
```python
# Similar logic with minor variations
def _classify_element(obj):
    """Classify element by type."""
    import inspect
    if inspect.ismodule(obj):
        return "module"
    # ... similar logic
```

#### Location 3: `docs_cli/analyzer/search.py:275-296`
```python
def _get_element_type(obj: Any) -> ElementType:
    """Get the element type of an object.

    Args:
        obj: Python object

    Returns:
        ElementType enum value
    """
    import inspect as insp

    if insp.ismodule(obj):
        return ElementType.MODULE
    if insp.isclass(obj):
        return ElementType.CLASS
    if insp.isfunction(obj):
        return ElementType.FUNCTION
    if insp.ismethod(obj):
        return ElementType.METHOD
    if isinstance(obj, property):
        return ElementType.PROPERTY
    return ElementType.UNKNOWN
```

### Issues Identified

| Issue | Impact | Severity |
|-------|--------|----------|
| **Maintenance Burden** | Changes must be made in 3+ places | Medium |
| **Potential Inconsistency** | Different return types (enum vs string) | Medium |
| **Code Bloat** | ~60 lines of duplicated code | Low |
| **Import Inconsistency** | `import inspect` vs `import inspect as insp` | Low |

### Example of Inconsistency

```python
# resolver.py returns ElementType enum
return ElementType.MODULE

# discovery.py might return string
return "module"

# This creates type checking issues:
if element_type == ElementType.MODULE:  # Works
if element_type == "module":  # Inconsistent!
```

## Impact Assessment

| Impact Type | Severity | Description |
|-------------|----------|-------------|
| Maintainability | 🟡 Medium | Changes require updates in multiple files |
| Bug Risk | 🟡 Medium | Easy to miss updating one location |
| Type Safety | 🟢 Low | Type hints may be inconsistent |
| Code Clarity | 🟢 Low | Harder to understand which function to use |

## Recommended Fix

### Option 1: Create Centralized Utility Module (Recommended)

```python
# docs_cli/utils/type_detection.py
"""Centralized element type detection utilities."""

import inspect
from docs_cli.analyzer.resolver import ElementType

# Type detection function order matters (more specific types first)
_TYPE_CHECKS = [
    # Modules first (most general)
    (inspect.ismodule, ElementType.MODULE),
    # Then classes
    (inspect.isclass, ElementType.CLASS),
    # Then functions (before methods)
    (inspect.isfunction, ElementType.FUNCTION),
    # Then methods (bound functions)
    (inspect.ismethod, ElementType.METHOD),
    # Then properties
    (lambda obj: isinstance(obj, property), ElementType.PROPERTY),
]


def get_element_type(obj: Any) -> ElementType:
    """Determine the type of a Python object.

    This is the SINGLE source of truth for element type detection
    across the entire pydocq project.

    Args:
        obj: Python object to classify

    Returns:
        ElementType enum value

    Examples:
        >>> get_element_type(os.path)
        <ElementType.MODULE: 'module'>
        >>> get_element_type(str)
        <ElementType.CLASS: 'class'>
        >>> get_element_type(len)
        <ElementType.FUNCTION: 'function'>
    """
    for check_func, element_type in _TYPE_CHECKS:
        if check_func(obj):
            return element_type

    return ElementType.UNKNOWN


def is_public_element(obj: Any, name: str = None) -> bool:
    """Check if an element is public (not private).

    Args:
        obj: Python object to check
        name: Optional name string (if available, avoids name lookup)

    Returns:
        True if element is public, False if private
    """
    if name is None:
        name = getattr(obj, '__name__', '')

    # Private if starts with underscore (but not __dunder__)
    if name.startswith('_'):
        # Dunder methods are considered public
        return name.startswith('__') and name.endswith('__')
    return True


def get_element_name(obj: Any) -> str:
    """Get the name of an element safely.

    Args:
        obj: Python object

    Returns:
        Element name or empty string if not available
    """
    return getattr(obj, '__name__', '')


def get_element_qualname(obj: Any) -> str:
    """Get the qualified name of an element safely.

    Args:
        obj: Python object

    Returns:
        Qualified name or empty string if not available
    """
    return getattr(obj, '__qualname__', '')


def is_callable(obj: Any) -> bool:
    """Check if an object is callable (excluding classes).

    Args:
        obj: Python object to check

    Returns:
        True if callable and not a class
    """
    if inspect.isclass(obj):
        return False
    return callable(obj)
```

### Update All Modules

```python
# docs_cli/analyzer/resolver.py
from docs_cli.utils.type_detection import get_element_type

def resolve_path(path_string: str) -> ResolvedElement:
    # ... existing code ...

    # Use centralized function
    element_type = get_element_type(current)

    return ResolvedElement(
        path=path_string,
        element_type=element_type,
        obj=current,
        module_path=_get_module_path(current),
    )

# Remove the old _determine_element_type function
```

```python
# docs_cli/analyzer/discovery.py
from docs_cli.utils.type_detection import get_element_type, is_public_element

class MemberInfo:
    # ... existing code ...

def _classify_member(obj: Any, name: str) -> MemberInfo:
    """Classify a member object."""
    element_type = get_element_type(obj)
    is_public = is_public_element(obj, name)

    # ... rest of logic
```

```python
# docs_cli/analyzer/search.py
from docs_cli.utils.type_detection import get_element_type

def search_by_name(module_path: str, pattern: str, include_private: bool = False):
    # ... existing code ...

    # Use centralized function
    element_type = get_element_type(member)

    results.append(SearchResult(
        path=f"{current_path}.{name}",
        element_type=element_type,
        # ...
    ))

# Remove the old _get_element_type function
```

### Option 2: Mixin Approach (For Object-Oriented Design)

```python
# docs_cli/utils/type_detection.py
import inspect
from docs_cli.analyzer.resolver import ElementType

class ElementTypeClassifier:
    """Centralized element type classification."""

    @staticmethod
    def classify(obj: Any) -> ElementType:
        """Classify an object's type."""
        if inspect.ismodule(obj):
            return ElementType.MODULE
        if inspect.isclass(obj):
            return ElementType.CLASS
        if inspect.isfunction(obj):
            return ElementType.FUNCTION
        if inspect.ismethod(obj):
            return ElementType.METHOD
        if isinstance(obj, property):
            return ElementType.PROPERTY
        return ElementType.UNKNOWN

# Singleton instance for easy access
_classifier = ElementTypeClassifier()

def get_element_type(obj: Any) -> ElementType:
    """Convenience function using singleton classifier."""
    return _classifier.classify(obj)
```

### Option 3: Caching for Performance (Bonus)

```python
# docs_cli/utils/type_detection.py
from functools import lru_cache
import inspect
from docs_cli.analyzer.resolver import ElementType

@lru_cache(maxsize=1024)
def get_element_type_cached(obj_id: int, obj_type: str) -> ElementType:
    """Cached version of element type detection.

    Note: We cache by id and type name to avoid holding object references.

    Args:
        obj_id: Object ID (from id() function)
        obj_type: Object type name (from type().__name__)

    Returns:
        ElementType enum value
    """
    # This is a simplified version - actual implementation would need the real object
    # For performance-critical code, consider this approach
    pass


def get_element_type(obj: Any, use_cache: bool = False) -> ElementType:
    """Get element type with optional caching.

    Args:
        obj: Python object to classify
        use_cache: Whether to use cached results (for repeated checks)

    Returns:
        ElementType enum value
    """
    if use_cache:
        obj_type = type(obj).__name__
        return get_element_type_cached(id(obj), obj_type)

    # Regular non-cached implementation
    if inspect.ismodule(obj):
        return ElementType.MODULE
    if inspect.isclass(obj):
        return ElementType.CLASS
    if inspect.isfunction(obj):
        return ElementType.FUNCTION
    if inspect.ismethod(obj):
        return ElementType.METHOD
    if isinstance(obj, property):
        return ElementType.PROPERTY
    return ElementType.UNKNOWN
```

## Migration Plan

### Phase 1: Create Utility Module
- [ ] Create `docs_cli/utils/__init__.py`
- [ ] Create `docs_cli/utils/type_detection.py`
- [ ] Implement `get_element_type()` function
- [ ] Add comprehensive unit tests

### Phase 2: Update Modules One by One
- [ ] Update `resolver.py` to use new function
- [ ] Update `discovery.py` to use new function
- [ ] Update `search.py` to use new function
- [ ] Run tests to ensure no regressions

### Phase 3: Remove Old Code
- [ ] Remove `_determine_element_type()` from `resolver.py`
- [ ] Remove `_get_element_type()` from `search.py`
- [ ] Remove similar functions from `discovery.py`
- [ ] Run full test suite

### Phase 4: Additional Utilities
- [ ] Add `is_public_element()` helper
- [ ] Add `get_element_name()` helper
- [ ] Add documentation

## Testing

### Unit Tests for Centralized Function

```python
# tests/test_type_detection.py
import pytest
from docs_cli.utils.type_detection import get_element_type
from docs_cli.analyzer.resolver import ElementType
import os
from pathlib import Path

class TestElementTypeDetection:
    """Test suite for centralized type detection."""

    def test_detects_modules(self):
        """Test module detection."""
        assert get_element_type(os) == ElementType.MODULE
        assert get_element_type(os.path) == ElementType.MODULE

    def test_detects_classes(self):
        """Test class detection."""
        assert get_element_type(str) == ElementType.CLASS
        assert get_element_type(dict) == ElementType.CLASS
        assert get_element_type(Path) == ElementType.CLASS

    def test_detects_functions(self):
        """Test function detection."""
        assert get_element_type(len) == ElementType.FUNCTION
        assert get_element_type(print) == ElementType.FUNCTION

    def test_detects_methods(self):
        """Test method detection."""
        assert get_element_type(str.upper) == ElementType.METHOD
        assert get_element_type([].append) == ElementType.METHOD

    def test_detects_properties(self):
        """Test property detection."""
        class Sample:
            @property
            def prop(self):
                return 42

        assert get_element_type(Sample.prop) == ElementType.PROPERTY

    def test_returns_unknown_for_unrecognized(self):
        """Test unknown type detection."""
        assert get_element_type(42) == ElementType.UNKNOWN
        assert get_element_type("string") == ElementType.UNKNOWN
        assert get_element_type([1, 2, 3]) == ElementType.UNKNOWN

    def test_handles_edge_cases(self):
        """Test edge cases."""
        # None
        assert get_element_type(None) == ElementType.UNKNOWN

        # Lambda
        assert get_element_type(lambda x: x) == ElementType.FUNCTION

        # Static method
        class Sample:
            @staticmethod
            def static_method():
                pass

        assert get_element_type(Sample.static_method) == ElementType.FUNCTION

        # Class method
        class Sample:
            @classmethod
            def class_method(cls):
                pass

        assert get_element_type(Sample.class_method) == ElementType.METHOD
```

### Integration Tests

```python
# tests/test_type_detection_integration.py
def test_resolver_uses_centralized_detection():
    """Test that resolver uses centralized type detection."""
    from docs_cli.analyzer.resolver import resolve_path

    result = resolve_path("json.dumps")
    assert result.element_type.name == "FUNCTION"

    result = resolve_path("json.JSONDecoder")
    assert result.element_type.name == "CLASS"


def test_search_uses_centralized_detection():
    """Test that search uses centralized type detection."""
    from docs_cli.analyzer.search import search_by_type
    from docs_cli.analyzer.resolver import ElementType

    results = search_by_type("json", ElementType.FUNCTION)
    assert len(results) > 0
    assert all(r.element_type == ElementType.FUNCTION for r in results)
```

## Benefits of Fix

| Benefit | Impact |
|---------|--------|
| **Single Source of Truth** | All type detection logic in one place |
| **Easier Maintenance** | Changes only need to be made once |
| **Better Testing** | One test suite for all type detection |
| **Type Safety** | Consistent return types (always ElementType enum) |
| **Extensibility** | Easy to add new element types |
| **Performance** | Can add caching in one place |
| **Code Reusability** | Other modules can easily use the utility |

## Related Issues

- [QUAL-002: Exception Handling Inconsistencies](./005-exception-handling-inconsistencies.md)
- [QUAL-003: Orphaned main.py File](./006-orphaned-main-py-file.md)
- [QUAL-004: Search Depth Not Limited](./007-search-depth-not-limited.md)

## References

- [DRY Principle](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself)
- [Python inspect module](https://docs.python.org/3/library/inspect.html)
- [Code refactoring best practices](https://refactoring.guru/)

## Checklist

- [ ] Create `docs_cli/utils/type_detection.py` module
- [ ] Implement centralized `get_element_type()` function
- [ ] Add comprehensive unit tests
- [ ] Update `resolver.py` to use new function
- [ ] Update `discovery.py` to use new function
- [ ] Update `search.py` to use new function
- [ ] Remove old `_determine_element_type()` from `resolver.py`
- [ ] Remove old `_get_element_type()` from `search.py`
- [ ] Run full test suite to ensure no regressions
- [ ] Update any other modules with similar logic
- [ ] Add documentation
- [ ] Consider adding caching for performance
