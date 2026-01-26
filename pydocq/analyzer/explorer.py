"""Recursive package exploration functionality.

This module provides functions to explore package structures
recursively, building hierarchical trees of modules, classes, and members.
"""

import inspect
from dataclasses import dataclass, field
from typing import Any, List, Optional

from pydocq.analyzer.discovery import discover_module_members, ModuleMembers
from pydocq.utils.type_detection import ElementType, get_element_type


@dataclass
class TreeNode:
    """A node in the hierarchical package tree."""

    path: str
    name: str
    element_type: str
    docstring: Optional[str] = None
    children: List["TreeNode"] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    properties: List[str] = field(default_factory=list)

    def to_dict(self, include_contents: bool = False) -> dict:
        """Convert to dictionary for JSON output.

        Args:
            include_contents: If True, include docstrings and detailed info

        Returns:
            Dictionary representation
        """
        result = {
            "path": self.path,
            "name": self.name,
            "type": self.element_type,
        }

        if include_contents and self.docstring:
            result["docstring"] = self.docstring

        if self.children:
            result["children"] = [child.to_dict(include_contents) for child in self.children]

        if self.classes:
            result["classes"] = self.classes
        if self.functions:
            result["functions"] = self.functions
        if self.methods:
            result["methods"] = self.methods
        if self.properties:
            result["properties"] = self.properties

        return result


def explore_package_recursive(
    module_path: str,
    *,
    max_depth: int = 10,
    include_private: bool = False,
    include_imported: bool = False,
    include_contents: bool = False,
    current_depth: int = 0,
) -> Optional[TreeNode]:
    """Explore a package recursively, building a hierarchical tree.

    Args:
        module_path: Path to the module to explore
        max_depth: Maximum recursion depth (default: 10)
        include_private: Include private members
        include_imported: Include imported members
        include_contents: Include docstrings and detailed info
        current_depth: Current recursion depth (internal use)

    Returns:
        TreeNode representing the package hierarchy
    """
    import importlib

    # Check depth limit
    if current_depth >= max_depth:
        return None

    # Import the module
    try:
        module = importlib.import_module(module_path)
    except ImportError:
        return None

    # Get module docstring
    module_doc = inspect.getdoc(module)

    # Discover members
    members = discover_module_members(
        module,
        include_private=include_private,
        include_imported=include_imported,
    )

    # Create tree node
    node = TreeNode(
        path=module_path,
        name=module_path.split(".")[-1],
        element_type="module",
        docstring=module_doc if include_contents else None,
    )

    # Add non-module members to the node
    for member in members.classes:
        node.classes.append(member.name)
        # Optionally explore class members
        if include_contents:
            class_members = inspect.getmembers(member.obj)
            for method_name, method in class_members:
                if not method_name.startswith("_") or include_private:
                    elem_type = get_element_type(method)
                    if elem_type == ElementType.METHOD:
                        node.methods.append(f"{member.name}.{method_name}")
                    elif elem_type == ElementType.PROPERTY:
                        node.properties.append(f"{member.name}.{method_name}")

    for member in members.functions:
        node.functions.append(member.name)

    # Recursively explore submodules
    for submodule in members.submodules:
        child_node = explore_package_recursive(
            submodule.obj.__name__,
            max_depth=max_depth,
            include_private=include_private,
            include_imported=include_imported,
            include_contents=include_contents,
            current_depth=current_depth + 1,
        )

        if child_node:
            node.children.append(child_node)

    return node


def format_tree_ascii(node: TreeNode, prefix: str = "", is_last: bool = True) -> str:
    """Format a tree node as ASCII art.

    Args:
        node: The tree node to format
        prefix: Prefix for each line (for recursion)
        is_last: Whether this is the last child

    Returns:
        ASCII string representation of the tree
    """
    lines = []

    # Add current node
    connector = "└── " if is_last else "├── "
    lines.append(f"{prefix}{connector}{node.name}/")

    # Prepare children prefix
    child_prefix = prefix + ("    " if is_last else "│   ")

    # Add children
    for i, child in enumerate(node.children):
        is_last_child = i == len(node.children) - 1
        lines.append(format_tree_ascii(child, child_prefix, is_last_child))

    # Add classes/functions if at leaf level
    if not node.children:
        if node.classes:
            lines.append(f"{child_prefix}    Classes: {', '.join(node.classes[:3])}")
            if len(node.classes) > 3:
                lines.append(f"{child_prefix}    ... and {len(node.classes) - 3} more")
        if node.functions:
            lines.append(f"{child_prefix}    Functions: {', '.join(node.functions[:3])}")
            if len(node.functions) > 3:
                lines.append(f"{child_prefix}    ... and {len(node.functions) - 3} more")

    return "\n".join(lines)


def get_package_stats(node: TreeNode) -> dict:
    """Get statistics about a package tree.

    Args:
        node: Root tree node

    Returns:
        Dictionary with package statistics
    """
    stats = {
        "total_modules": 0,
        "total_classes": 0,
        "total_functions": 0,
        "total_methods": 0,
        "max_depth": 0,
    }

    def count_nodes(n: TreeNode, depth: int) -> None:
        """Recursively count nodes."""
        stats["total_modules"] += 1
        stats["total_classes"] += len(n.classes)
        stats["total_functions"] += len(n.functions)
        stats["total_methods"] += len(n.methods)
        stats["max_depth"] = max(stats["max_depth"], depth)

        for child in n.children:
            count_nodes(child, depth + 1)

    count_nodes(node, 0)
    return stats
