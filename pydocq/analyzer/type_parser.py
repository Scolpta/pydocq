"""Type annotation parsing for Python code.

This module provides utilities for parsing and analyzing type annotations
from Python code, including forward references, generics, and complex types.
"""

import ast
import inspect
import sys
import types
from typing import Any, Union, get_type_hints

from pydocq.analyzer.resolver import ElementType
from pydocq.utils.type_detection import ElementType


class TypeInfo:
    """Information about a type annotation."""

    def __init__(
        self,
        name: str,
        origin: str | None = None,
        args: list | None = None,
        is_optional: bool = False,
        is_union: bool = False,
    ) -> None:
        """Initialize type information.

        Args:
            name: Type name
            origin: Origin type (for generics like List, Dict)
            args: Type arguments (for generics like List[int])
            is_optional: Whether this is an Optional type
            is_union: Whether this is a Union type
        """
        self.name = name
        self.origin = origin
        self.args = args or []
        self.is_optional = is_optional
        self.is_union = is_union

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON output.

        Returns:
            Dictionary representation
        """
        result = {"name": self.name}

        if self.origin:
            result["origin"] = self.origin

        if self.args:
            result["args"] = [arg.to_dict() if isinstance(arg, TypeInfo) else arg for arg in self.args]

        if self.is_optional:
            result["is_optional"] = True

        if self.is_union:
            result["is_union"] = True

        return result


def parse_type_annotation(annotation: Any) -> TypeInfo:
    """Parse a type annotation into TypeInfo.

    Args:
        annotation: Type annotation (can be string, type, or typing object)

    Returns:
        TypeInfo with parsed information
    """
    # Handle string annotations (forward references)
    if isinstance(annotation, str):
        return TypeInfo(name=annotation)

    # Handle None (no annotation)
    if annotation is inspect.Parameter.empty or annotation is None:
        return TypeInfo(name="Any")

    # Get the string representation
    annotation_str = str(annotation)

    # Handle Optional types (Union[X, None])
    if hasattr(annotation, "__origin__"):
        origin = annotation.__origin__

        # Check for Optional (Union with None)
        if origin is types.UnionType or (sys.version_info >= (3, 10) and origin is Union):
            args = annotation.__args__ if hasattr(annotation, "__args__") else []
            # Check if None is in args
            if type(None) in args:
                non_none_args = [a for a in args if a is not type(None)]
                if len(non_none_args) == 1:
                    # Optional[T] case
                    inner_type = parse_type_annotation(non_none_args[0])
                    return TypeInfo(
                        name=inner_type.name,
                        origin=inner_type.origin,
                        args=inner_type.args,
                        is_optional=True,
                    )

        # Handle generic types (List, Dict, etc.)
        if hasattr(origin, "__name__"):
            type_name = origin.__name__
        else:
            type_name = annotation_str

        # Parse type arguments
        args = []
        if hasattr(annotation, "__args__"):
            args = [parse_type_annotation(arg) for arg in annotation.__args__]

        return TypeInfo(name=type_name, origin=type_name, args=args, is_union=False)

    # Handle built-in types
    if isinstance(annotation, type):
        return TypeInfo(name=annotation.__name__)

    # Default: return string representation
    return TypeInfo(name=annotation_str)


def get_type_hints_safe(obj: Any) -> dict:
    """Get type hints from an object, handling errors gracefully.

    Args:
        obj: Python object (function, class, method)

    Returns:
        Dictionary of parameter names to type annotations
    """
    try:
        # For Python 3.11+, we can use get_type_hints with include_extras
        if sys.version_info >= (3, 11):
            return get_type_hints(obj, include_extras=True)
        else:
            return get_type_hints(obj)
    except (NameError, TypeError, AttributeError):
        # Forward references or other issues
        # Try to get annotations directly
        if hasattr(obj, "__annotations__"):
            return obj.__annotations__
        return {}


def parse_signature_types(obj: Any) -> dict:
    """Parse all type annotations from a callable object.

    Args:
        obj: A callable object (function, method)

    Returns:
        Dictionary with 'parameters' and 'return' keys
    """
    try:
        sig = inspect.signature(obj)
    except (ValueError, TypeError):
        return {"parameters": {}, "return": None}

    # Get type hints
    type_hints = get_type_hints_safe(obj)

    result = {"parameters": {}, "return": None}

    for param_name, param in sig.parameters.items():
        if param_name in type_hints:
            annotation = type_hints[param_name]
            result["parameters"][param_name] = parse_type_annotation(annotation).to_dict()
        elif param.annotation != inspect.Parameter.empty:
            result["parameters"][param_name] = parse_type_annotation(param.annotation).to_dict()

    # Return type
    if "return" in type_hints:
        result["return"] = parse_type_annotation(type_hints["return"]).to_dict()
    elif sig.return_annotation != inspect.Parameter.empty:
        result["return"] = parse_type_annotation(sig.return_annotation).to_dict()

    return result


def get_class_type_hints(cls: type) -> dict:
    """Get type hints for class attributes and methods.

    Args:
        cls: A class

    Returns:
        Dictionary with 'attributes' and 'methods' keys
    """
    result = {"attributes": {}, "methods": {}}

    # Get class annotations
    if hasattr(cls, "__annotations__"):
        for attr_name, annotation in cls.__annotations__.items():
            result["attributes"][attr_name] = parse_type_annotation(annotation).to_dict()

    # Get method type hints
    for name, member in inspect.getmembers(cls):
        if inspect.isfunction(member) or inspect.ismethod(member):
            try:
                type_info = parse_signature_types(member)
                if type_info.get("parameters") or type_info.get("return"):
                    result["methods"][name] = type_info
            except Exception:
                # Skip methods that can't be parsed
                continue

    return result


def resolve_forward_reference(annotation_str: str, module_name: str | None = None) -> str:
    """Resolve a forward reference string to its full path.

    Args:
        annotation_str: String annotation (e.g., "List", "MyClass")
        module_name: Module where the annotation is used

    Returns:
        Resolved type string
    """
    # Simple forward references don't need resolution
    if "." in annotation_str:
        # Already a full path
        return annotation_str

    # Check if it's a typing module annotation
    typing_annotations = [
        "List",
        "Dict",
        "Set",
        "Tuple",
        "Optional",
        "Union",
        "Any",
        "Callable",
        "Type",
        "TypeVar",
        "Generic",
    ]

    if annotation_str in typing_annotations:
        return f"typing.{annotation_str}"

    # For other forward references, return as-is
    # In a full implementation, we would try to resolve these
    # from the module's namespace
    return annotation_str
