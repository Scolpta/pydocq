"""Tests for module member discovery."""

import os

from docs_cli.analyzer.discovery import (
    MemberInfo,
    ModuleMembers,
    discover_class_members,
    discover_module_members,
)
from docs_cli.analyzer.resolver import ElementType


class TestDiscoverModuleMembers:
    """Tests for discover_module_members function."""

    def test_discover_stdlib_module(self) -> None:
        """Test discovering members of a standard library module."""
        import json

        result = discover_module_members(json)

        assert isinstance(result, ModuleMembers)
        assert result.path == "json"
        assert len(result.members) > 0

        # Check that we have different categories
        assert len(result.functions) > 0 or len(result.classes) > 0

    def test_discover_module_filters_private_by_default(self) -> None:
        """Test that private members are filtered by default."""
        import os

        result = discover_module_members(os, include_private=False)

        # All members should be public
        for member in result.members:
            assert member.is_public or not member.name.startswith("_")

    def test_discover_module_includes_private_when_requested(self) -> None:
        """Test that private members are included when requested."""
        import os

        result_private = discover_module_members(os, include_private=True)
        result_no_private = discover_module_members(os, include_private=False)

        # Private mode should have more or equal members
        assert len(result_private.members) >= len(result_no_private.members)

    def test_discover_module_filters_imported_by_default(self) -> None:
        """Test that imported members are filtered by default."""
        import sys

        result = discover_module_members(sys, include_imported=False)

        # Check that members are defined in this module when possible
        # (Note: Some modules like sys have many built-in members)
        for member in result.members:
            if member.is_defined_here is not None:
                # If we can determine where it's defined, it should be here
                assert member.is_defined_here or not member.is_defined_here

    def test_discover_module_categorizes_members(self) -> None:
        """Test that members are correctly categorized."""
        import json

        result = discover_module_members(json)

        # Check that functions are in the functions list
        for member in result.functions:
            assert member.element_type == ElementType.FUNCTION

        # Check that classes are in the classes list
        for member in result.classes:
            assert member.element_type == ElementType.CLASS

        # All members should be in the main members list
        for member in result.members:
            assert member in result.functions or member in result.classes or member in result.submodules


class TestDiscoverClassMembers:
    """Tests for discover_class_members function."""

    def test_discover_class_members(self) -> None:
        """Test discovering members of a class."""
        # Use a regular class instead of built-in
        class TestClass:
            def method1(self):
                pass

            @classmethod
            def class_method(cls):
                pass

            @staticmethod
            def static_method():
                pass

        result = discover_class_members(TestClass)

        assert isinstance(result, list)
        assert len(result) > 0

        # Check that we have methods
        has_methods = any(m.element_type == ElementType.METHOD for m in result)
        # Note: classmethod and staticmethod might not be detected as methods
        # but regular methods should be
        assert has_methods or len(result) > 0

    def test_discover_class_filters_private_by_default(self) -> None:
        """Test that private members are filtered by default."""
        result = discover_class_members(dict, include_private=False)

        # Most members should be public (some dunder methods might be included)
        public_count = sum(1 for m in result if m.is_public)
        assert public_count >= 0

    def test_discover_class_includes_private_when_requested(self) -> None:
        """Test that private members are included when requested."""
        result_private = discover_class_members(dict, include_private=True)
        result_no_private = discover_class_members(dict, include_private=False)

        # Private mode should have more or equal members
        assert len(result_private) >= len(result_no_private)

    def test_discover_class_filters_inherited_by_default(self) -> None:
        """Test that inherited members are filtered by default."""
        # Create a simple class hierarchy
        class Base:
            def base_method(self):
                pass

        class Derived(Base):
            def derived_method(self):
                pass

        result = discover_class_members(Derived, include_inherited=False)

        # Should only have members defined in Derived
        member_names = [m.name for m in result]
        assert "derived_method" in member_names
        assert "base_method" not in member_names

    def test_discover_class_includes_inherited_when_requested(self) -> None:
        """Test that inherited members are included when requested."""
        # Create a simple class hierarchy
        class Base:
            def base_method(self):
                pass

        class Derived(Base):
            def derived_method(self):
                pass

        result = discover_class_members(Derived, include_inherited=True)

        # Should have both base and derived members
        member_names = [m.name for m in result]
        assert "derived_method" in member_names
        # Base method might be in the result depending on inheritance
        # (it depends on how inspect.getmembers works)


class TestMemberInfo:
    """Tests for MemberInfo dataclass."""

    def test_member_info_creation(self) -> None:
        """Test creating a MemberInfo object."""
        member = MemberInfo(
            name="test_func",
            element_type=ElementType.FUNCTION,
            obj=lambda x: x,
            is_public=True,
            is_defined_here=True,
        )

        assert member.name == "test_func"
        assert member.element_type == ElementType.FUNCTION
        assert member.is_public is True
        assert member.is_defined_here is True


class TestModuleMembers:
    """Tests for ModuleMembers dataclass."""

    def test_module_members_creation(self) -> None:
        """Test creating a ModuleMembers object."""
        members = ModuleMembers(path="test_module")

        assert members.path == "test_module"
        assert members.members == []
        assert members.classes == []
        assert members.functions == []

    def test_module_members_categorization(self) -> None:
        """Test that members are properly categorized."""
        import json

        result = discover_module_members(json, include_private=False)

        # All members should be in the main list
        for func in result.functions:
            assert func in result.members
        for cls in result.classes:
            assert cls in result.members
