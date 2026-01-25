"""Discovery of module members and structure.

This module provides functions to discover and categorize members within
Python modules, classes, and other objects.
"""

import inspect
from dataclasses import dataclass, field
from typing import Any

from pydocq.utils.type_detection import ElementType, get_element_type


@dataclass
class MemberInfo:
    """Information about a discovered member."""

    name: str
    element_type: ElementType
    obj: Any
    is_public: bool = True
    is_defined_here: bool = True


@dataclass
class ModuleMembers:
    """Complete information about discovered members of a module."""

    path: str
    members: list[MemberInfo] = field(default_factory=list)
    classes: list[MemberInfo] = field(default_factory=list)
    functions: list[MemberInfo] = field(default_factory=list)
    methods: list[MemberInfo] = field(default_factory=list)
    properties: list[MemberInfo] = field(default_factory=list)
    submodules: list[MemberInfo] = field(default_factory=list)


def discover_module_members(
    module: Any, include_private: bool = False, include_imported: bool = False
) -> ModuleMembers:
    """Discover all members of a module.

    Args:
        module: The module object to inspect
        include_private: Whether to include private members (starting with _)
        include_imported: Whether to include imported members

    Returns:
        ModuleMembers with categorized member information
    """
    result = ModuleMembers(path=module.__name__)

    # Get all members
    for name, obj in inspect.getmembers(module):
        # Skip private members if requested
        if not include_private and name.startswith("_"):
            continue

        # Get the module where the member is defined
        defined_in = inspect.getmodule(obj)

        # Skip imported members if requested
        if not include_imported and defined_in and defined_in != module:
            # Still include submodules that were imported
            if not inspect.ismodule(obj):
                continue

        # Determine the element type
        element_type = get_element_type(obj)

        # Check if it's public
        is_public = not name.startswith("_")

        # Check if it's defined in this module
        is_defined_here = defined_in is None or defined_in == module

        member_info = MemberInfo(
            name=name,
            element_type=element_type,
            obj=obj,
            is_public=is_public,
            is_defined_here=is_defined_here,
        )

        result.members.append(member_info)

        # Categorize the member
        if element_type == ElementType.MODULE:
            result.submodules.append(member_info)
        elif element_type == ElementType.CLASS:
            result.classes.append(member_info)
        elif element_type == ElementType.FUNCTION:
            result.functions.append(member_info)
        elif element_type == ElementType.METHOD:
            result.methods.append(member_info)
        elif element_type == ElementType.PROPERTY:
            result.properties.append(member_info)

    return result


def discover_class_members(
    cls: type, include_private: bool = False, include_inherited: bool = False
) -> list[MemberInfo]:
    """Discover all members of a class.

    Args:
        cls: The class to inspect
        include_private: Whether to include private members (starting with _)
        include_inherited: Whether to include inherited members

    Returns:
        List of MemberInfo for class members
    """
    members = []

    # Get all members
    for name, obj in inspect.getmembers(cls):
        # Skip private members if requested
        if not include_private and name.startswith("_"):
            # Dunder methods are always private
            if name.startswith("__"):
                continue
            # Single underscore prefix
            if not name.startswith("__"):
                continue

        # Check if it's inherited
        if not include_inherited:
            # Check if the member is defined in this class or its bases
            if name in cls.__dict__:
                is_defined_here = True
            else:
                # Member is inherited
                continue
        else:
            is_defined_here = name in cls.__dict__

        # Determine the element type
        element_type = get_element_type(obj)

        # Check if it's public (dunder methods are considered private)
        is_public = not (name.startswith("_") and not name.startswith("__"))

        member_info = MemberInfo(
            name=name,
            element_type=element_type,
            obj=obj,
            is_public=is_public,
            is_defined_here=is_defined_here,
        )

        members.append(member_info)

    return members
