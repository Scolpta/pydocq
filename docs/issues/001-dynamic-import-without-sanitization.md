# Issue SEC-001: Dynamic Import Without Sanitization

## Description

The `resolve_path()` function directly passes user input to `importlib.import_module()` without any validation or sanitization. This allows arbitrary module imports from the system.

## Vulnerability Details

### Affected Code
```python
# docs_cli/analyzer/resolver.py:82-83
try:
    module = importlib.import_module(package_name)
except ImportError as e:
    raise PackageNotFoundError(
        f"Package or module '{package_name}' not found or cannot be imported"
    ) from e
```

### Attack Vector

An attacker who can execute `pydocq` commands could:

1. **Import any installed module**, including sensitive system modules:
   ```bash
   pydocq subprocess.Popen
   pydocq os.system
   pydocq socket.socket
   ```

2. **Execute arbitrary code** if malicious packages are installed:
   ```python
   # Malicious package installed on system
   # pydocq malicious_package.evil_function
   ```

3. **Access packages that should be restricted** in certain environments

### Example Exploitation Scenarios

#### Scenario 1: Information Disclosure
```bash
# List all modules in subprocess package
pydocq --list-members subprocess

# Could reveal internal functions that shouldn't be exposed
```

#### Scenario 2: Code Execution
```python
# If a malicious package exists:
# evil_package/setup.py
def evil():
    __import__('subprocess').run(['rm', '-rf', '/'], shell=True)

# Attacker runs:
$ pydocq evil_package.evil
# Imports and potentially triggers execution
```

## Impact Assessment

| Impact Type | Severity | Description |
|-------------|----------|-------------|
| Arbitrary Code Execution | 🔴 Critical | If malicious packages installed |
| Information Disclosure | 🟡 Medium | Access to all installed packages |
| Privilege Escalation | 🟡 Medium | Combined with other vulnerabilities |
| Supply Chain Attack | 🔴 High | Compromised package could be exploited |

## Recommended Fix

### Option 1: Allowlist Approach (Recommended for Production)

```python
# docs_cli/analyzer/resolver.py
import importlib
from typing import Set

# Allowlist of safe module prefixes
SAFE_IMPORT_PREFIXES: Set[str] = {
    # Standard library modules
    'os', 'sys', 'json', 'pathlib', 'collections',
    'typing', 'dataclasses', 'datetime', 're', 'math',
    'itertools', 'functools', 'operator', 'io',
    'logging', 'threading', 'multiprocessing',
    # Add more as needed
}

def _is_safe_import(module_name: str) -> bool:
    """Check if a module import is safe.

    Args:
        module_name: Module name to validate

    Returns:
        True if import is allowed, False otherwise
    """
    # Check against allowlist
    for prefix in SAFE_IMPORT_PREFIXES:
        if module_name == prefix or module_name.startswith(f'{prefix}.'):
            return True

    # Block everything else by default
    return False

def resolve_path(path_string: str) -> ResolvedElement:
    """Resolve a path string to an actual Python element."""
    if not path_string:
        raise InvalidPathError("Path string cannot be empty")

    parts = path_string.split(".")
    if not parts:
        raise InvalidPathError(f"Invalid path: {path_string}")

    package_name = parts[0]

    # VALIDATION: Check before import
    if not _is_safe_import(package_name):
        raise InvalidPathError(
            f"Importing from '{package_name}' is not allowed by security policy. "
            f"Module '{package_name}' is not in the allowed import list."
        )

    try:
        module = importlib.import_module(package_name)
    except ImportError as e:
        raise PackageNotFoundError(
            f"Package or module '{package_name}' not found or cannot be imported"
        ) from e
    # ... rest of function
```

### Option 2: Blocklist Approach (Defense in Depth)

```python
# Blocklist of dangerous modules
BLOCKED_IMPORTS: Set[str] = {
    'subprocess',
    'os.system',
    'os.popen',
    'shutil',
    'commands',
}

def _is_blocked_import(module_name: str) -> bool:
    """Check if a module import is explicitly blocked."""
    for blocked in BLOCKED_IMPORTS:
        if module_name == blocked or module_name.startswith(f'{blocked}.'):
            return True
    return False
```

### Option 3: Configuration-Based (Most Flexible)

```python
# pyproject.toml
[tool.pydocq.security]
# Security mode: "strict", "permissive", "custom"
mode = "permissive"

# In permissive mode: allow these by default
allowed_packages = ["stdlib"]

# In any mode: block these explicitly
blocked_packages = ["subprocess", "os.system", "shutil"]

# Third-party package handling: "allow", "warn", "block"
third_party_action = "warn"
```

```python
# docs_cli/analyzer/resolver.py
from typing import Literal
import warnings

SecurityMode = Literal["strict", "permissive", "custom"]

def _check_import_security(
    module_name: str,
    mode: SecurityMode = "permissive",
    third_party_action: str = "warn"
) -> None:
    """Check if module import complies with security policy."""
    # Check blocklist first
    if module_name in BLOCKED_IMPORTS:
        raise InvalidPathError(
            f"Module '{module_name}' is blocked by security policy"
        )

    # Check if it's a stdlib module
    if _is_stdlib_module(module_name):
        return  # Always allow stdlib

    # Third-party package handling
    if third_party_action == "block" and mode == "strict":
        raise InvalidPathError(
            f"Third-party package '{module_name}' not allowed in strict mode"
        )
    elif third_party_action == "warn":
        warnings.warn(
            f"Importing third-party package: {module_name}",
            UserWarning
        )
```

### Option 4: Immediate Mitigation (Quick Fix)

Add a `--safe-mode` flag for backward compatibility:

```python
# docs_cli/cli.py
@app.command()
def query(
    target: str,
    safe_mode: bool = Option(
        True,
        "--safe-mode/--no-safe-mode",
        help="Restrict imports to safe modules only (default: enabled)"
    ),
    # ... other options
) -> None:
    """Query Python package documentation."""
    if safe_mode:
        # Enable security restrictions
        from docs_cli.analyzer.resolver import enable_safe_mode
        enable_safe_mode()

    # ... rest of function
```

## Testing

### Security Test Suite

```python
# tests/test_security_imports.py
import pytest
from docs_cli.analyzer.resolver import resolve_path, InvalidPathError

class TestDynamicImportSecurity:
    """Test suite for import security."""

    def test_should_block_subprocess(self):
        """Test that subprocess module is blocked."""
        with pytest.raises(InvalidPathError, match="not allowed|blocked"):
            resolve_path("subprocess.Popen")

    def test_should_block_os_system(self):
        """Test that os.system is blocked."""
        with pytest.raises(InvalidPathError, match="not allowed|blocked"):
            resolve_path("os.system")

    def test_should_allow_stdlib_modules(self):
        """Test that stdlib modules are allowed."""
        result = resolve_path("os.path.join")
        assert result.path == "os.path.join"

        result = resolve_path("json.dumps")
        assert result.path == "json.dumps"

    def test_should_warn_on_third_party(self):
        """Test that third-party packages trigger warnings."""
        import warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            try:
                resolve_path("pandas.DataFrame")
                # Check warning was issued
                assert len(w) > 0
                assert "third-party" in str(w[0].message).lower()
            except InvalidPathError:
                # In strict mode, should raise
                pass

    def test_should_prevent_code_execution(self):
        """Test that malicious code cannot be executed via import."""
        # This would require a test fixture with a malicious package
        # For now, ensure the validation runs before import
        pass
```

### Regression Tests

```python
# tests/test_security_regression.py
def test_normal_functionality_preserved():
    """Ensure security fixes don't break normal usage."""
    # Should still work
    result = resolve_path("json.dumps")
    assert result.element_type.name == "FUNCTION"

    result = resolve_path("collections.OrderedDict")
    assert result.element_type.name == "CLASS"
```

## Implementation Priority

1. **Immediate (P0):** Implement Option 1 or Option 4
2. **Short-term (P1):** Add configuration file support (Option 3)
3. **Long-term (P2):** Add comprehensive security audit logging

## Related Issues

- [SEC-002: File System Access Without Validation](./002-file-system-access-without-validation.md)
- [SEC-003: Code Execution via AST](./003-code-execution-via-ast.md)

## References

- [CWE-20: Improper Input Validation](https://cwe.mitre.org/data/definitions/20.html)
- [OWASP Code Injection](https://owasp.org/www-community/attacks/Code_Injection)
- [Python importlib documentation](https://docs.python.org/3/library/importlib.html)
- [Python Security Guidelines](https://docs.python.org/3/security_warnings.html)

## Checklist

- [ ] Implement input validation for package names
- [ ] Add allowlist/blocklist functionality
- [ ] Add security test cases
- [ ] Update documentation with security guidelines
- [ ] Consider adding `--safe-mode` CLI flag
- [ ] Add warnings for third-party package imports
- [ ] Add configuration file support
- [ ] Add audit logging for blocked imports
