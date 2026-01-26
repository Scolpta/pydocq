"""Search functionality for discovering code elements.

This module provides functions to search for elements within modules
based on various criteria like name patterns, docstrings, metadata, etc.
"""

import fnmatch
import inspect
import re
from dataclasses import dataclass
from typing import Any, Callable, List, Optional

from pydocq.analyzer.resolver import ResolvedElement, resolve_path
from pydocq.utils.type_detection import ElementType, get_element_type


class SearchResult:
    """Result of a search operation."""

    def __init__(
        self,
        path: str,
        element_type: ElementType,
        name: str,
        match_reason: str,
        obj: Any = None,
    ) -> None:
        """Initialize search result.

        Args:
            path: Full path to element
            element_type: Type of element
            name: Name of the element
            match_reason: Why this element matched
            obj: The actual Python object
        """
        self.path = path
        self.element_type = element_type
        self.name = name
        self.match_reason = match_reason
        self.obj = obj

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON output.

        Returns:
            Dictionary representation
        """
        return {
            "path": self.path,
            "type": self.element_type.value,
            "name": self.name,
            "match_reason": self.match_reason,
        }


def search_by_name(
    module_path: str,
    pattern: str,
    include_private: bool = False,
    max_depth: int = 10,
) -> List[SearchResult]:
    """Search for elements by name pattern.

    Args:
        module_path: Path to module to search
        pattern: Glob pattern to match names (e.g., "*test*", "get_*")
        include_private: Whether to include private members
        max_depth: Maximum recursion depth (default: 10)

    Returns:
        List of SearchResult objects
    """
    try:
        resolved = resolve_path(module_path)
    except Exception:
        return []

    results = []
    visited = set()  # Track visited objects to prevent cycles

    def search_object(obj: Any, current_path: str, depth: int) -> None:
        """Recursively search object with depth limit."""
        # Check depth limit
        if depth > max_depth:
            return

        # Check for cycles
        obj_id = id(obj)
        if obj_id in visited:
            return
        visited.add(obj_id)

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
                element_type = get_element_type(member)
                results.append(
                    SearchResult(
                        path=f"{current_path}.{name}",
                        element_type=element_type,
                        name=name,
                        match_reason="name_pattern",
                        obj=member,
                    )
                )

            # Recursively search modules and classes
            if inspect.ismodule(member) or inspect.isclass(member):
                search_object(member, f"{current_path}.{name}", depth + 1)

    search_object(resolved.obj, resolved.path, depth=0)
    return results


def search_by_docstring(
    module_path: str,
    keyword: str,
    case_sensitive: bool = False,
    max_depth: int = 10,
) -> List[SearchResult]:
    """Search for elements by docstring content.

    Args:
        module_path: Path to module to search
        keyword: Keyword to search for in docstrings
        case_sensitive: Whether search is case sensitive
        max_depth: Maximum recursion depth (default: 10)

    Returns:
        List of SearchResult objects
    """
    try:
        resolved = resolve_path(module_path)
    except Exception:
        return []

    results = []
    search_keyword = keyword if case_sensitive else keyword.lower()
    visited = set()

    def search_object(obj: Any, current_path: str, depth: int) -> None:
        """Recursively search object with depth limit."""
        if depth > max_depth:
            return

        obj_id = id(obj)
        if obj_id in visited:
            return
        visited.add(obj_id)

        try:
            members = inspect.getmembers(obj)
        except Exception:
            return

        for name, member in members:
            if name.startswith("_"):
                continue

            doc = inspect.getdoc(member)
            if doc:
                doc_search = doc if case_sensitive else doc.lower()
                if search_keyword in doc_search:
                    element_type = get_element_type(member)
                    results.append(
                        SearchResult(
                            path=f"{current_path}.{name}",
                            element_type=element_type,
                            name=name,
                            match_reason="docstring_contains",
                            obj=member,
                        )
                    )

            if inspect.ismodule(member) or inspect.isclass(member):
                search_object(member, f"{current_path}.{name}", depth + 1)

    search_object(resolved.obj, resolved.path, depth=0)
    return results


def search_by_type(
    module_path: str,
    element_type: ElementType,
    max_depth: int = 10,
) -> List[SearchResult]:
    """Search for elements by type.

    Args:
        module_path: Path to module to search
        element_type: Type of elements to find
        max_depth: Maximum recursion depth (default: 10)

    Returns:
        List of SearchResult objects
    """
    try:
        resolved = resolve_path(module_path)
    except Exception:
        return []

    results = []
    visited = set()

    def search_object(obj: Any, current_path: str, depth: int) -> None:
        """Recursively search object with depth limit."""
        if depth > max_depth:
            return

        obj_id = id(obj)
        if obj_id in visited:
            return
        visited.add(obj_id)

        try:
            members = inspect.getmembers(obj)
        except Exception:
            return

        for name, member in members:
            if name.startswith("_"):
                continue

            if get_element_type(member) == element_type:
                results.append(
                    SearchResult(
                        path=f"{current_path}.{name}",
                        element_type=element_type,
                        name=name,
                        match_reason="type_match",
                        obj=member,
                    )
                )

            if inspect.ismodule(member) or inspect.isclass(member):
                search_object(member, f"{current_path}.{name}", depth + 1)

    search_object(resolved.obj, resolved.path, depth=0)
    return results


def search_by_metadata(
    module_path: str,
    metadata_key: str,
    metadata_value: Any = None,
    max_depth: int = 10,
) -> List[SearchResult]:
    """Search for elements by SDK metadata.

    Args:
        module_path: Path to module to search
        metadata_key: Metadata key to search for
        metadata_value: Optional value to match (None = any value)
        max_depth: Maximum recursion depth (default: 10)

    Returns:
        List of SearchResult objects
    """
    try:
        from pydocq.sdk import get_metadata_dict
    except ImportError:
        return []

    try:
        resolved = resolve_path(module_path)
    except Exception:
        return []

    results = []
    visited = set()

    def search_object(obj: Any, current_path: str, depth: int) -> None:
        """Recursively search object with depth limit."""
        if depth > max_depth:
            return

        obj_id = id(obj)
        if obj_id in visited:
            return
        visited.add(obj_id)

        try:
            members = inspect.getmembers(obj)
        except Exception:
            return

        for name, member in members:
            if name.startswith("_"):
                continue

            meta = get_metadata_dict(member)
            if metadata_key in meta:
                if metadata_value is None or meta[metadata_key] == metadata_value:
                    element_type = get_element_type(member)
                    results.append(
                        SearchResult(
                            path=f"{current_path}.{name}",
                            element_type=element_type,
                            name=name,
                            match_reason="metadata_match",
                            obj=member,
                        )
                    )

            if inspect.ismodule(member) or inspect.isclass(member):
                search_object(member, f"{current_path}.{name}", depth + 1)

    search_object(resolved.obj, resolved.path, depth=0)
    return results


@dataclass
class MatchResult:
    """Result of a search operation with additional metadata."""

    path: str
    name: str
    element_type: str
    module: str
    is_public: bool

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON output."""
        return {
            "path": self.path,
            "name": self.name,
            "type": self.element_type,
            "module": self.module,
            "is_public": self.is_public,
        }


def search_members(
    module_path: str,
    pattern: str,
    *,
    use_regex: bool = False,
    case_sensitive: bool = False,
    element_type_filter: Optional[str] = None,
    max_results: Optional[int] = None,
    include_private: bool = False,
    max_depth: int = 10,
) -> List[MatchResult]:
    """Search for members matching a pattern in a module.

    This is an enhanced search function that supports both glob patterns
    and regex patterns, with additional filtering options.

    Args:
        module_path: Module path to search in (e.g., "json" or "pandas")
        pattern: Search pattern (glob or regex)
        use_regex: If True, treat pattern as regex instead of glob
        case_sensitive: If True, case-sensitive search
        element_type_filter: Filter by element type (class, function, method, etc.)
        max_results: Maximum number of results to return
        include_private: Include private members (starting with _)
        max_depth: Maximum recursion depth

    Returns:
        List of MatchResult objects
    """
    try:
        resolved = resolve_path(module_path)
    except Exception:
        return []

    results = []
    visited = set()

    def _matches(name: str) -> bool:
        """Check if name matches the pattern."""
        # Empty pattern matches everything
        if not pattern:
            return True

        if not case_sensitive:
            name = name.lower()
            search_pattern = pattern.lower()
        else:
            search_pattern = pattern

        if use_regex:
            try:
                return bool(re.search(search_pattern, name))
            except re.error:
                # Invalid regex, fall back to substring match
                return search_pattern in name
        else:
            # Use glob pattern matching
            return fnmatch.fnmatch(name, search_pattern)

    def search_object(obj: Any, current_path: str, depth: int) -> None:
        """Recursively search object with depth limit."""
        if depth > max_depth:
            return

        obj_id = id(obj)
        if obj_id in visited:
            return
        visited.add(obj_id)

        try:
            members = inspect.getmembers(obj)
        except Exception:
            return

        for name, member in members:
            # Check max results before each iteration
            if max_results and len(results) >= max_results:
                return

            # Skip private members if requested
            if not include_private and name.startswith("_"):
                continue

            # Check if name matches pattern
            if _matches(name):
                elem_type = get_element_type(member)

                # Filter by element type if specified
                if element_type_filter and elem_type.value != element_type_filter:
                    continue

                # Create result
                results.append(
                    MatchResult(
                        path=f"{current_path}.{name}",
                        name=name,
                        element_type=elem_type.value,
                        module=current_path,
                        is_public=not name.startswith("_"),
                    )
                )

                # Check max results after adding
                if max_results and len(results) >= max_results:
                    return

            # Recursively search modules and classes
            if inspect.ismodule(member) or inspect.isclass(member):
                search_object(member, f"{current_path}.{name}", depth + 1)

    search_object(resolved.obj, resolved.path, depth=0)
    return results
