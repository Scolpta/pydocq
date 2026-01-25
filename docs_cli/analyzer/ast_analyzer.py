"""Static analysis using Python's AST module.

This module provides functions to analyze Python source code using the
Abstract Syntax Tree (AST) without importing or executing the code.

IMPORTANT: This module only parses and analyzes code structure. It does NOT
execute any code. All analysis is performed on the AST representation only,
which makes it safe to analyze untrusted or malicious code without side effects.

Security guarantees:
- Code is parsed with ast.parse() which only creates an AST
- No functions are called, no code is executed
- No import statements are processed
- Only the structure (functions, classes, imports) is extracted
"""

import ast
import inspect
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# Patterns that should not appear in file paths for security reasons
_DANGEROUS_PATH_PATTERNS = [
    r"\.\./",  # Parent directory traversal
    r"\.\./.*",  # Parent directory with path
    r"/etc/",  # System configuration files
    r"/sys/",  # System files
    r"/proc/",  # Process files
    r"/root/",  # Root user directory
    r"~",  # Home directory shortcut
]


class ASTSecurityError(Exception):
    """Raised when a file path is rejected for security reasons."""

    pass


@dataclass
class ASTFunctionInfo:
    """Information about a function from AST analysis."""

    name: str
    lineno: int
    args: list[str] = field(default_factory=list)
    returns: str | None = None
    is_async: bool = False
    docstring: str | None = None
    decorator_list: list[str] = field(default_factory=list)


@dataclass
class ASTClassInfo:
    """Information about a class from AST analysis."""

    name: str
    lineno: int
    bases: list[str] = field(default_factory=list)
    docstring: str | None = None
    methods: list[ASTFunctionInfo] = field(default_factory=list)
    decorators: list[str] = field(default_factory=list)


@dataclass
class ASTImportInfo:
    """Information about an import."""

    module: str
    names: list[str] = field(default_factory=list)
    level: int = 0  # For relative imports
    is_from: bool = False
    lineno: int = 0


@dataclass
class ASTModuleInfo:
    """Complete information about a module from AST analysis."""

    path: str
    docstring: str | None = None
    functions: list[ASTFunctionInfo] = field(default_factory=list)
    classes: list[ASTClassInfo] = field(default_factory=list)
    imports: list[ASTImportInfo] = field(default_factory=list)
    globals: list[str] = field(default_factory=list)


def _validate_file_path(file_path: str) -> None:
    """Validate that a file path is safe to access.

    Args:
        file_path: Path to validate

    Raises:
        ASTSecurityError: If the path contains dangerous patterns
    """
    # Check for dangerous patterns
    for pattern in _DANGEROUS_PATH_PATTERNS:
        if re.search(pattern, file_path):
            raise ASTSecurityError(
                f"File path contains dangerous pattern: {file_path}. "
                f"Path traversal and system file access are not allowed."
            )

    # Check for absolute paths (absolute paths are generally not needed for this tool)
    path = Path(file_path)
    if path.is_absolute():
        raise ASTSecurityError(
            f"Absolute paths are not allowed: {file_path}. "
            f"Please use relative paths."
        )

    # Check file extension - should be .py
    if not file_path.endswith(".py"):
        raise ASTSecurityError(
            f"Only Python files (.py) are allowed: {file_path}"
        )


def parse_source(source: str) -> ast.Module:
    """Parse Python source code into an AST.

    Args:
        source: Python source code string

    Returns:
        AST module node

    Raises:
        SyntaxError: If source has invalid syntax
    """
    try:
        return ast.parse(source)
    except SyntaxError as e:
        raise SyntaxError(f"Failed to parse source: {e}")


def parse_file(file_path: str) -> ast.Module:
    """Parse a Python file into an AST.

    Args:
        file_path: Path to Python file

    Returns:
        AST module node

    Raises:
        ASTSecurityError: If file path is dangerous
        FileNotFoundError: If file doesn't exist
        SyntaxError: If file has invalid syntax
    """
    # Validate file path for security
    _validate_file_path(file_path)

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    source = path.read_text(encoding="utf-8")
    return parse_source(source)


def analyze_module(module_node: ast.Module, path: str) -> ASTModuleInfo:
    """Analyze an AST module node.

    Args:
        module_node: AST module node
        path: Module path for reference

    Returns:
        ASTModuleInfo with analysis results
    """
    info = ASTModuleInfo(path=path)

    # Get module docstring
    docstring = ast.get_docstring(module_node)
    if docstring:
        info.docstring = docstring

    for node in module_node.body:
        if isinstance(node, ast.FunctionDef):
            func_info = _analyze_function(node)
            info.functions.append(func_info)
        elif isinstance(node, ast.AsyncFunctionDef):
            func_info = _analyze_function(node)
            func_info.is_async = True
            info.functions.append(func_info)
        elif isinstance(node, ast.ClassDef):
            class_info = _analyze_class(node)
            info.classes.append(class_info)
        elif isinstance(node, ast.Import):
            import_info = _analyze_import(node)
            info.imports.append(import_info)
        elif isinstance(node, ast.ImportFrom):
            import_info = _analyze_import_from(node)
            info.imports.append(import_info)
        elif isinstance(node, ast.Global):
            info.globals.extend(node.names)

    return info


def _analyze_function(node: ast.FunctionDef | ast.AsyncFunctionDef) -> ASTFunctionInfo:
    """Analyze a function definition node.

    Args:
        node: Function or async function definition node

    Returns:
        ASTFunctionInfo
    """
    args = [arg.arg for arg in node.args.args]

    returns = None
    if node.returns:
        returns = ast.unparse(node.returns)

    docstring = ast.get_docstring(node)

    decorators = []
    for decorator in node.decorator_list:
        decorators.append(ast.unparse(decorator))

    return ASTFunctionInfo(
        name=node.name,
        lineno=node.lineno,
        args=args,
        returns=returns,
        docstring=docstring,
        decorator_list=decorators,
    )


def _analyze_class(node: ast.ClassDef) -> ASTClassInfo:
    """Analyze a class definition node.

    Args:
        node: Class definition node

    Returns:
        ASTClassInfo
    """
    bases = []
    for base in node.bases:
        bases.append(ast.unparse(base))

    docstring = ast.get_docstring(node)

    methods = []
    for item in node.body:
        if isinstance(item, ast.FunctionDef):
            methods.append(_analyze_function(item))
        elif isinstance(item, ast.AsyncFunctionDef):
            func_info = _analyze_function(item)
            func_info.is_async = True
            methods.append(func_info)

    decorators = []
    for decorator in node.decorator_list:
        decorators.append(ast.unparse(decorator))

    return ASTClassInfo(
        name=node.name,
        lineno=node.lineno,
        bases=bases,
        docstring=docstring,
        methods=methods,
        decorators=decorators,
    )


def _analyze_import(node: ast.Import) -> ASTImportInfo:
    """Analyze an import statement.

    Args:
        node: Import node

    Returns:
        ASTImportInfo
    """
    names = [alias.name for alias in node.names]

    return ASTImportInfo(
        module="",
        names=names,
        is_from=False,
        lineno=node.lineno,
    )


def _analyze_import_from(node: ast.ImportFrom) -> ASTImportInfo:
    """Analyze a from...import statement.

    Args:
        node: ImportFrom node

    Returns:
        ASTImportInfo
    """
    module = node.module or ""
    names = [alias.name for alias in node.names]

    return ASTImportInfo(
        module=module,
        names=names,
        level=node.level,
        is_from=True,
        lineno=node.lineno,
    )


def analyze_file(file_path: str) -> ASTModuleInfo:
    """Analyze a Python file using AST.

    Args:
        file_path: Path to Python file

    Returns:
        ASTModuleInfo with complete analysis

    Raises:
        ASTSecurityError: If file path is dangerous
        FileNotFoundError: If file doesn't exist
        SyntaxError: If file has invalid syntax
    """
    tree = parse_file(file_path)
    return analyze_module(tree, file_path)


def analyze_object(obj: Any) -> ASTModuleInfo | ASTClassInfo | ASTFunctionInfo:
    """Analyze a Python object using its source code.

    Args:
        obj: Python object to analyze

    Returns:
        Analysis result based on object type
    """
    try:
        source = inspect.getsource(obj)
    except (TypeError, OSError):
        # Built-in or compiled object
        raise ValueError("Cannot get source for built-in or compiled objects")

    tree = parse_source(source)

    if isinstance(obj, type):
        # It's a class - find the class definition
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == obj.__name__:
                return _analyze_class(node)
    elif inspect.isfunction(obj) or inspect.ismethod(obj):
        # It's a function - find the function definition
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == obj.__name__:
                return _analyze_function(node)

    # Default: analyze as module
    return analyze_module(tree, obj.__name__)


def find_calls(module_info: ASTModuleInfo, function_name: str) -> list[dict]:
    """Find all calls to a specific function in the module.

    Args:
        module_info: Module analysis result
        function_name: Name of function to find

    Returns:
        List of dictionaries with call information
    """
    calls = []

    # This would require more detailed AST analysis
    # For now, return empty list as placeholder
    return calls


def get_dependencies(module_info: ASTModuleInfo) -> dict[str, list[str]]:
    """Get all dependencies from a module.

    Args:
        module_info: Module analysis result

    Returns:
        Dictionary with external and internal dependencies
    """
    dependencies = {"external": [], "internal": []}

    for import_info in module_info.imports:
        if import_info.is_from:
            if import_info.module:
                dependencies["external"].append(import_info.module)
        else:
            for name in import_info.names:
                dependencies["external"].append(name.split(".")[0])

    return dependencies
