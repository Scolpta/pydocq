# Issue SEC-003: Code Execution via AST

## Description

AST parsing could potentially execute code in certain scenarios, particularly when evaluating type annotations, decorators, or default arguments that contain function calls or complex expressions. While `ast.parse()` itself doesn't execute code, subsequent processing or evaluation of AST nodes might trigger execution.

## Vulnerability Details

### Affected Code
```python
# docs_cli/analyzer/ast_analyzer.py
import ast

def analyze_file(file_path: str):
    """Analyze a Python file using AST."""
    with open(file_path, 'r') as f:
        source = f.read()

    # Parsing itself is safe
    tree = ast.parse(source)

    # But if we evaluate nodes or annotations...
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign):
            # If we evaluate annotation: UNSAFE
            value = eval(compile(ast.Expression(node.annotation), '', 'eval'))

    return tree
```

### Attack Vector

#### Type Annotation Execution
```python
# malicious.py
from subprocess import run

def dangerous(
    config: __import__('subprocess').run(['rm', '-rf', '/tmp'], shell=True)
) -> None:
    """Function with dangerous type annotation."""
    pass
```

#### Decorator Execution
```python
# malicious.py
def evil_decorator(func):
    __import__('subprocess').run(['evil_command'], shell=True)
    return func

@evil_decorator
def my_function():
    pass
```

#### Default Argument Evaluation
```python
# malicious.py
def dangerous(
    config = __import__('os').system('evil_command')
) -> None:
    """Function with dangerous default argument."""
    pass
```

### Example Exploitation Scenarios

#### Scenario 1: Annotation Evaluation
```python
# If ast_analyzer evaluates type annotations
def vulnerable(
    data: exec("import os; os.system('pwned')")
) -> None:
    pass

# Running: pydocq analyze malicious.py
# Could execute: exec("import os; os.system('pwned')")
```

#### Scenario 2: Decorator Analysis
```python
# If analyzer instantiates decorators to get metadata
class MaliciousDecorator:
    def __init__(self):
        __import__('subprocess').run(['evil'], shell=True)

@MaliciousDecorator()
def function():
    pass

# If analyzer does: decorator_instance = decorator.cls()
# Code executes!
```

## Impact Assessment

| Impact Type | Severity | Description |
|-------------|----------|-------------|
| Remote Code Execution | 🟡 Medium | If AST nodes are evaluated |
| Lateral Movement | 🟡 Medium | Execute commands on system |
| Data Exfiltration | 🟢 Low | Could exfiltrate via executed code |
| Denial of Service | 🟢 Low | Could cause system instability |

**Note:** Current risk is **Medium** because `ast.parse()` itself doesn't execute code. The risk increases if the analyzer:
- Evaluates type annotations
- Instantiates decorators or classes
- Evaluates default arguments
- Uses `eval()` or `exec()` on AST nodes

## Recommended Fix

### Option 1: Safe AST Traversal (Recommended)

```python
# docs_cli/analyzer/ast_analyzer.py
import ast
from typing import Any, Dict, List, Optional

class SafeASTAnalyzer(ast.NodeVisitor):
    """Safe AST analyzer that doesn't execute code."""

    def __init__(self):
        self.dangerous_nodes: List[Dict[str, Any]] = []

    def visit_Call(self, node: ast.Call) -> None:
        """Detect function calls in AST."""
        # Flag function calls as potentially dangerous
        self.dangerous_nodes.append({
            'type': 'Call',
            'line': node.lineno,
            'function': ast.unparse(node.func) if hasattr(ast, 'unparse') else 'Unknown',
        })
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Detect import statements."""
        self.dangerous_nodes.append({
            'type': 'Import',
            'line': node.lineno,
            'modules': [alias.name for alias in node.names],
        })
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Detect from...import statements."""
        self.dangerous_nodes.append({
            'type': 'ImportFrom',
            'line': node.lineno,
            'module': node.module,
            'names': [alias.name for alias in node.names],
        })
        self.generic_visit(node)

    def has_dangerous_code(self) -> bool:
        """Check if AST contains potentially dangerous code."""
        return len(self.dangerous_nodes) > 0


def safe_parse_ast(source: str, filename: str = '<unknown>') -> ast.AST:
    """Safely parse Python source code without evaluation.

    Args:
        source: Python source code
        filename: Filename for error messages

    Returns:
        AST tree

    Raises:
        SyntaxError: If source has invalid syntax
        ValueError: If source contains potentially dangerous patterns
    """
    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as e:
        raise SyntaxError(f"Invalid Python syntax in {filename}:{e.lineno}: {e.msg}")

    # Analyze for dangerous patterns
    analyzer = SafeASTAnalyzer()
    analyzer.visit(tree)

    # Optional: Warn or block dangerous code
    if analyzer.has_dangerous_code():
        import warnings
        warnings.warn(
            f"File {filename} contains potentially dangerous code patterns: "
            f"{len(analyzer.dangerous_nodes)} function(s)/import(s) detected. "
            f"Analysis is read-only and code will not be executed.",
            UserWarning
        )

    return tree


def safe_get_annotation(annotation: ast.AST) -> str:
    """Get string representation of annotation without evaluation.

    Args:
        annotation: AST annotation node

    Returns:
        String representation of the annotation

    Raises:
        ValueError: If annotation would require evaluation
    """
    # Convert to string without evaluating
    if hasattr(ast, 'unparse'):
        # Python 3.9+
        return ast.unparse(annotation)
    else:
        # Fallback: generate string representation
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Subscript):
            return f"{safe_get_annotation(annotation.slice)}[...]"
        elif isinstance(annotation, ast.Attribute):
            return f"{safe_get_annotation(annotation.value)}.{annotation.attr}"
        else:
            # Complex annotation that might be dangerous
            raise ValueError(f"Cannot safely evaluate annotation: {type(annotation)}")
```

### Option 2: Static Analysis without Evaluation

```python
# docs_cli/analyzer/ast_analyzer.py
import ast

class StaticAnalyzer(ast.NodeVisitor):
    """Static analyzer that never evaluates code."""

    def analyze_function_signature(self, node: ast.FunctionDef) -> Dict:
        """Analyze function signature without evaluation.

        Args:
            node: Function definition AST node

        Returns:
            Dictionary with signature information
        """
        signature_info = {
            'name': node.name,
            'args': [],
            'returns': None,
            'decorators': []
        }

        # Analyze decorators (names only, don't instantiate)
        for decorator in node.decorator_list:
            decorator_name = self._get_decorator_name(decorator)
            if decorator_name:
                signature_info['decorators'].append(decorator_name)

        # Analyze arguments
        for arg in node.args.args:
            arg_info = {
                'name': arg.arg,
                'annotation': self._safe_annotation_string(arg.annotation) if arg.annotation else None
            }
            signature_info['args'].append(arg_info)

        # Return type (string only)
        if node.returns:
            signature_info['returns'] = self._safe_annotation_string(node.returns)

        return signature_info

    def _get_decorator_name(self, decorator: ast.AST) -> Optional[str]:
        """Get decorator name without instantiation.

        Args:
            decorator: Decorator AST node

        Returns:
            Decorator name or None
        """
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return f"{self._get_decorator_name(decorator.value)}.{decorator.attr}"
        elif isinstance(decorator, ast.Call):
            # Decorator with arguments - just get the name
            return self._get_decorator_name(decorator.func)
        return None

    def _safe_annotation_string(self, annotation: ast.AST) -> str:
        """Get annotation as string without evaluation.

        Args:
            annotation: Annotation AST node

        Returns:
            String representation
        """
        if hasattr(ast, 'unparse'):
            return ast.unparse(annotation)

        # Manual unparsing for simple cases
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Attribute):
            value = self._safe_annotation_string(annotation.value)
            return f"{value}.{annotation.attr}"
        elif isinstance(annotation, ast.Subscript):
            value = self._safe_annotation_string(annotation.value)
            return f"{value}[...]"  # Simplified
        else:
            # For complex annotations, return a placeholder
            return "<complex-type>"


def analyze_file_safe(file_path: str) -> Dict:
    """Analyze Python file without executing code.

    Args:
        file_path: Path to Python file

    Returns:
        Analysis results

    Raises:
        SyntaxError: If file has invalid syntax
    """
    with open(file_path, 'r') as f:
        source = f.read()

    tree = safe_parse_ast(source, filename=file_path)
    analyzer = StaticAnalyzer()

    results = {
        'file': file_path,
        'functions': [],
        'classes': [],
        'imports': []
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            results['functions'].append(analyzer.analyze_function_signature(node))
        elif isinstance(node, ast.ClassDef):
            results['classes'].append({'name': node.name})
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            results['imports'].append(ast.unparse(node) if hasattr(ast, 'unparse') else str(type(node)))

    return results
```

### Option 3: Sandboxed Evaluation (If Evaluation is Necessary)

```python
# docs_cli/analyzer/ast_analyzer.py
import ast
import types

class Sandbox:
    """Restricted execution environment."""

    # Blocked builtins
    DISALLOWED_BUILTINS = {
        'eval', 'exec', 'compile', '__import__',
        'open', 'file', 'input',
        'reload', '__builtins__'
    }

    def __init__(self):
        """Create sandboxed environment."""
        self.globals = {
            '__builtins__': {
                name: getattr(__builtins__, name)
                for name in dir(__builtins__)
                if name not in self.DISALLOWED_BUILTINS and not name.startswith('_')
            }
        }

    def safe_eval(self, expr: str) -> Any:
        """Safely evaluate an expression.

        Args:
            expr: Expression to evaluate

        Returns:
            Result of evaluation

        Raises:
            ValueError: If expression is unsafe
        """
        # Check for dangerous patterns
        dangerous_patterns = [
            '__import__',
            'eval(',
            'exec(',
            'compile(',
            'open(',
            'import ',
        ]

        expr_lower = expr.lower()
        for pattern in dangerous_patterns:
            if pattern in expr_lower:
                raise ValueError(f"Expression contains potentially dangerous code: {pattern}")

        try:
            return eval(expr, self.globals, {})
        except Exception as e:
            raise ValueError(f"Failed to evaluate expression: {e}")


def safe_eval_annotation(annotation: ast.AST, sandbox: Sandbox) -> Any:
    """Safely evaluate annotation in sandbox.

    Args:
        annotation: AST annotation node
        sandbox: Sandbox for evaluation

    Returns:
        Evaluated annotation or string representation
    """
    try:
        # Try to evaluate in sandbox
        code = compile(ast.Expression(annotation), '<annotation>', 'eval')
        return sandbox.safe_eval(code)
    except Exception:
        # Fallback to string representation
        return ast.unparse(annotation) if hasattr(ast, 'unparse') else str(type(annotation))
```

### Option 4: Validation Before Processing

```python
# docs_cli/analyzer/ast_analyzer.py
import ast
import re

DANGEROUS_PATTERNS = [
    r'__import__',
    r'eval\s*\(',
    r'exec\s*\(',
    r'compile\s*\(',
    r'open\s*\(',
    r'\.system\s*\(',
    r'\.popen\s*\(',
    r'subprocess',
    r'os\.system',
    r'os\.popen',
]

def validate_source_safety(source: str) -> None:
    """Validate that source code doesn't contain obvious dangerous patterns.

    Args:
        source: Python source code

    Raises:
        ValueError: If dangerous patterns are detected
    """
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, source):
            raise ValueError(
                f"Potentially dangerous code pattern detected: {pattern}. "
                f"This file will not be analyzed to prevent code execution."
            )
```

## Testing

### Security Test Suite

```python
# tests/test_security_ast_execution.py
import pytest
import tempfile
import os
from docs_cli.analyzer.ast_analyzer import (
    safe_parse_ast,
    safe_get_annotation,
    analyze_file_safe,
    validate_source_safety,
    SafeASTAnalyzer
)

class TestASTExecutionSecurity:
    """Test suite for AST execution security."""

    def test_should_prevent_annotation_execution(self):
        """Test that annotations with function calls are not executed."""
        source = """
def dangerous(
    data: __import__('subprocess').run(['evil'])
) -> None:
    pass
"""
        tree = safe_parse_ast(source)

        # Should parse successfully
        assert tree is not None

        # But annotation should not execute
        # (We can't easily test that code DIDN'T run, but we can verify the string representation)
        func = tree.body[0]
        annotation_str = ast.unparse(func.returns) if hasattr(ast, 'unparse') else str(type(func.returns))
        assert annotation_str is not None

    def test_should_detect_dangerous_imports(self):
        """Test that dangerous imports are flagged."""
        source = """
import subprocess
import os.system
from subprocess import run
"""
        tree = safe_parse_ast(source)
        analyzer = SafeASTAnalyzer()
        analyzer.visit(tree)

        # Should detect dangerous imports
        assert analyzer.has_dangerous_code()
        assert len(analyzer.dangerous_nodes) >= 2

    def test_should_block_eval_in_source(self):
        """Test that eval() in source is detected."""
        source = """
def dangerous():
    eval('evil code')
"""

        with pytest.raises(ValueError, match="dangerous"):
            validate_source_safety(source)

    def test_should_prevent_decorator_instantiation(self):
        """Test that decorators are not instantiated."""
        source = """
class MaliciousDecorator:
    def __init__(self):
        raise RuntimeError("Should not execute")

@MaliciousDecorator()
def function():
    pass
"""

        # Should not raise RuntimeError
        tree = safe_parse_ast(source)
        func = tree.body[1]

        # Should have decorator info but not instantiate
        assert len(func.decorator_list) > 0

    def test_should_handle_complex_annotations_safely(self):
        """Test that complex type annotations don't execute."""
        source = """
from typing import List, Dict

def complex_function(
    data: Dict[str, List[int]]
) -> List[str]:
    pass
"""

        tree = safe_parse_ast(source)
        func = tree.body[1]

        # Should parse without executing
        assert func is not None

    def test_should_analyze_malicious_file_safely(self, tmp_path):
        """Test that malicious files can be analyzed without execution."""
        malicious_file = tmp_path / "malicious.py"
        malicious_file.write_text("""
# This file attempts to execute code via annotations
def evil(
    config: __import__('os').system('pwned')
) -> None:
    pass
""")

        # Should not execute code
        result = analyze_file_safe(str(malicious_file))

        # Should return analysis results
        assert 'functions' in result
        assert len(result['functions']) == 1
```

### Regression Tests

```python
def test_normal_analysis_still_works():
    """Ensure security measures don't break normal analysis."""
    source = """
def normal_function(x: int, y: str) -> bool:
    '''A normal function.'''
    return True
"""

    tree = safe_parse_ast(source)
    func = tree.body[0]

    assert func.name == "normal_function"
    assert len(func.args.args) == 2
```

## Implementation Priority

1. **Immediate (P0):** Implement Option 1 (safe traversal) or Option 4 (validation)
2. **Short-term (P1):** Add comprehensive dangerous pattern detection
3. **Long-term (P2):** Consider sandboxed execution if necessary

## Security Best Practices

1. **Never use `eval()` or `exec()`** on untrusted code
2. **Never instantiate classes or call functions** from AST
3. **Always use string representation** for annotations
4. **Validate source code** before parsing
5. **Log flagged dangerous code** for monitoring
6. **Document security assumptions** clearly
7. **Use `ast.NodeVisitor`** for safe traversal

## Related Issues

- [SEC-001: Dynamic Import Without Sanitization](./001-dynamic-import-without-sanitization.md)
- [SEC-002: File System Access Without Validation](./002-file-system-access-without-validation.md)

## References

- [CWE-94: Code Injection](https://cwe.mitre.org/data/definitions/94.html)
- [Python AST Security](https://docs.python.org/3/library/ast.html)
- [Safe AST Parsing](https://greentreesnakes.readthedocs.io/)
- [Python eval() Security](https://realpython.com/python-eval-function/)

## Checklist

- [ ] Implement safe AST traversal without evaluation
- [ ] Add dangerous pattern detection
- [ ] Ensure annotations are treated as strings only
- [ ] Never instantiate decorators or call functions
- [ ] Add security test suite with malicious code samples
- [ ] Add warnings for detected dangerous patterns
- [ ] Document security assumptions
- [ ] Add audit logging for flagged code
