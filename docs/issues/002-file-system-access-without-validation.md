# Issue SEC-002: File System Access Without Validation

## Description

The AST analyzer reads files directly from the filesystem without validating the file paths. This could potentially allow access to sensitive files through path traversal attacks or reading files outside the intended project directory.

## Vulnerability Details

### Affected Code
```python
# docs_cli/analyzer/ast_analyzer.py (estimated location based on module purpose)
def read_file_ast(file_path: str) -> ast.AST:
    """Parse a Python file using AST."""
    with open(file_path, 'r') as f:
        source = f.read()
    return ast.parse(source)
```

### Attack Vector

#### Path Traversal Attacks
```bash
# Read sensitive system files
pydocq ../../../../../etc/passwd
pydocq ../../../../../root/.ssh/id_rsa
pydocq ~/.ssh/config
pydocq /etc/shadow

# Read files from other projects
pydocq ../../other-project/secrets.py
```

#### Information Disclosure
```bash
# List files in arbitrary directories
pydocq --list-members ../../../../../tmp/

# Could reveal:
# - API keys and credentials
# - Database configuration
# - Private SSH keys
# - Password files
```

### Example Exploitation Scenarios

#### Scenario 1: Path Traversal
```bash
$ cd /home/user/project
$ pydocq ../../../../etc/passwd
{
  "path": "../../../../../etc/passwd",
  "type": "module",
  "docstring": "root:x:0:0:root:/root:/bin/bash\n..."
}
```

#### Scenario 2: Absolute Path Access
```bash
$ pydocq /etc/hosts
{
  "path": "/etc/hosts",
  "type": "module",
  "docstring": "127.0.0.1 localhost\n..."
}
```

#### Scenario 3: Home Directory Access
```bash
$ pydocq ~/.aws/credentials
{
  "path": "/home/user/.aws/credentials",
  "type": "module",
  "docstring": "[default]\naws_access_key_id = AKIA...\n..."
}
```

## Impact Assessment

| Impact Type | Severity | Description |
|-------------|----------|-------------|
| Path Traversal | 🔴 Critical | Access files outside project directory |
| Information Disclosure | 🔴 Critical | Read sensitive files (keys, passwords) |
| Privacy Violation | 🔴 High | Access user's private files |
| Compliance Violation | 🟡 Medium | GDPR/PCI-DSS violations possible |

## Recommended Fix

### Option 1: Directory Allowlist (Recommended)

```python
# docs_cli/analyzer/ast_analyzer.py
import os
from typing import Set, Optional

# Default safe directories
SAFE_DIRECTORIES: Set[str] = set()

def initialize_safe_directories(project_root: Optional[str] = None) -> None:
    """Initialize the list of safe directories.

    Args:
        project_root: Project root directory. If None, uses current directory.
    """
    global SAFE_DIRECTORIES

    if project_root is None:
        project_root = os.getcwd()

    SAFE_DIRECTORIES.add(os.path.abspath(project_root))

    # Add common Python project directories
    for subdir in ['src', 'lib', 'tests', 'docs']:
        subdir_path = os.path.join(project_root, subdir)
        if os.path.exists(subdir_path):
            SAFE_DIRECTORIES.add(os.path.abspath(subdir_path))


def _is_safe_file_path(file_path: str) -> bool:
    """Validate that a file path is safe to read.

    Args:
        file_path: Path to validate

    Returns:
        True if file is within safe directories, False otherwise
    """
    # Convert to absolute path
    abs_path = os.path.abspath(file_path)

    # Check if within safe directories
    for safe_dir in SAFE_DIRECTORIES:
        # Check if abs_path is within safe_dir or is safe_dir itself
        if abs_path == safe_dir or abs_path.startswith(safe_dir + os.sep):
            return True

    return False


def _validate_file_path(file_path: str) -> str:
    """Validate and normalize a file path.

    Args:
        file_path: File path to validate

    Returns:
        Normalized absolute path

    Raises:
        ValueError: If path is outside safe directories
    """
    # Check for path traversal attempts
    if '../' in file_path or file_path.startswith('~'):
        raise ValueError(
            f"Path traversal detected: {file_path}. "
            f"Cannot access files outside project directory."
        )

    # Normalize the path
    abs_path = os.path.abspath(file_path)

    # Check if within safe directories
    if not _is_safe_file_path(abs_path):
        raise ValueError(
            f"Cannot read file outside safe directories: {file_path}\n"
            f"Resolved path: {abs_path}\n"
            f"Safe directories: {SAFE_DIRECTORIES}"
        )

    return abs_path


def safe_read_file(file_path: str) -> str:
    """Safely read a file's contents.

    Args:
        file_path: Path to file to read

    Returns:
        File contents

    Raises:
        ValueError: If path is outside safe directories
        FileNotFoundError: If file doesn't exist
        IOError: If file cannot be read
    """
    validated_path = _validate_file_path(file_path)

    try:
        with open(validated_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {validated_path}")
    except IOError as e:
        raise IOError(f"Cannot read file {validated_path}: {e}")


def parse_ast_safe(file_path: str) -> ast.AST:
    """Safely parse a Python file using AST.

    Args:
        file_path: Path to Python file

    Returns:
        AST tree

    Raises:
        ValueError: If path is outside safe directories
        SyntaxError: If file has invalid Python syntax
    """
    source = safe_read_file(file_path)
    try:
        return ast.parse(source, filename=file_path)
    except SyntaxError as e:
        raise SyntaxError(f"Invalid Python syntax in {file_path}: {e}")
```

### Option 2: Configuration-Based Approach

```python
# pyproject.toml or .pydocq.toml
[tool.pydocq.security]
# Allowed root directories
allowed_roots = [
    ".",           # Current directory
    "./src",       # src directory
    "./lib",       # lib directory
]

# Block specific paths
blocked_paths = [
    "/etc",
    "/root",
    "~/.ssh",
    "~/.aws",
]

# Maximum file size to read (prevent DoS)
max_file_size = "1MB"
```

```python
# docs_cli/analyzer/ast_analyzer.py
import tomli
from pathlib import Path

class SecurityConfig:
    """Security configuration for file access."""

    def __init__(self, config_path: Optional[str] = None):
        """Load security configuration.

        Args:
            config_path: Path to config file (pyproject.toml or .pydocq.toml)
        """
        self.allowed_roots = [os.getcwd()]
        self.blocked_paths = []
        self.max_file_size = 1024 * 1024  # 1MB default

        if config_path and os.path.exists(config_path):
            self._load_config(config_path)

    def _load_config(self, config_path: str) -> None:
        """Load configuration from TOML file."""
        with open(config_path, 'rb') as f:
            config = tomli.load(f)

        security = config.get('tool', {}).get('pydocq', {}).get('security', {})

        # Load allowed roots
        for root in security.get('allowed_roots', []):
            self.allowed_roots.append(os.path.abspath(root))

        # Load blocked paths
        for path in security.get('blocked_paths', []):
            expanded = os.path.expanduser(path)
            self.blocked_paths.append(os.path.abspath(expanded))

    def is_safe_path(self, file_path: str) -> bool:
        """Check if file path is safe."""
        abs_path = os.path.abspath(file_path)

        # Check blocked paths first
        for blocked in self.blocked_paths:
            if abs_path == blocked or abs_path.startswith(blocked + os.sep):
                return False

        # Check allowed roots
        for root in self.allowed_roots:
            if abs_path.startswith(root + os.sep):
                return True

        return False
```

### Option 3: Temporary File Isolation

For maximum security, work in a temporary directory:

```python
import tempfile
import shutil

class SecureASTAnalyzer:
    """AST analyzer that operates in isolated directory."""

    def __init__(self):
        self.temp_dir = None
        self.project_root = os.getcwd()

    def __enter__(self):
        """Create temporary working directory."""
        self.temp_dir = tempfile.mkdtemp(prefix='pydocq_')
        return self

    def __exit__(self, *args):
        """Clean up temporary directory."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def analyze_file(self, file_path: str) -> ast.AST:
        """Analyze a file safely."""
        # Copy file to temp directory
        filename = os.path.basename(file_path)
        temp_path = os.path.join(self.temp_dir, filename)

        shutil.copy2(file_path, temp_path)

        # Analyze in isolated environment
        with open(temp_path, 'r') as f:
            source = f.read()

        return ast.parse(source)
```

### Option 4: Immediate Mitigation (Quick Fix)

```python
def quick_path_validation(file_path: str) -> None:
    """Quick path validation for immediate security improvement."""
    abs_path = os.path.abspath(file_path)

    # Block obvious path traversal
    if '../' in file_path or file_path.startswith('/') or file_path.startswith('~'):
        raise ValueError(
            f"Path traversal detected: {file_path}. "
            f"Only relative paths within project directory are allowed."
        )

    # Ensure we're staying in current directory tree
    cwd = os.getcwd()
    if not abs_path.startswith(cwd):
        raise ValueError(
            f"Cannot access files outside current directory: {file_path}"
        )
```

## Testing

### Security Test Suite

```python
# tests/test_security_filesystem.py
import pytest
import os
import tempfile
from docs_cli.analyzer.ast_analyzer import (
    _is_safe_file_path,
    _validate_file_path,
    safe_read_file,
    initialize_safe_directories
)

class TestFileSystemSecurity:
    """Test suite for filesystem access security."""

    @pytest.fixture(autouse=True)
    def setup_safe_directories(self, tmp_path):
        """Setup safe directories for testing."""
        initialize_safe_directories(str(tmp_path))

    def test_should_block_path_traversal(self):
        """Test that path traversal is blocked."""
        with pytest.raises(ValueError, match="traversal|outside"):
            _validate_file_path("../../../etc/passwd")

    def test_should_block_absolute_paths(self):
        """Test that absolute paths are blocked."""
        with pytest.raises(ValueError, match="traversal|outside"):
            _validate_file_path("/etc/hosts")

    def test_should_block_home_directory(self):
        """Test that home directory paths are blocked."""
        with pytest.raises(ValueError, match="traversal|outside"):
            _validate_file_path("~/.ssh/config")

    def test_should_allow_project_files(self, tmp_path):
        """Test that project files are allowed."""
        # Create a test file
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")

        # Should not raise
        validated = _validate_file_path(str(test_file))
        assert os.path.isabs(validated)

    def test_should_prevent_reading_sensitive_files(self):
        """Test that sensitive files cannot be read."""
        with pytest.raises(ValueError):
            safe_read_file("/etc/shadow")

    def test_should_detect_malicious_paths(self):
        """Test detection of various malicious path patterns."""
        malicious_paths = [
            "../../../etc/passwd",
            "/etc/passwd",
            "~/.ssh/id_rsa",
            "..\\..\\windows\\system32\\config",  # Windows traversal
            "/proc/version",
            "C:\\Windows\\System32\\config",  # Windows absolute
        ]

        for path in malicious_paths:
            with pytest.raises(ValueError, match="traversal|outside"):
                _validate_file_path(path)

    def test_should_handle_symlinks(self, tmp_path):
        """Test that symlinks outside safe dir are blocked."""
        # Create symlink to /etc
        symlink = tmp_path / "etc_link"
        try:
            symlink.symlink_to("/etc")
        except OSError:
            pytest.skip("Cannot create symlinks on this system")

        # Should not allow following symlink
        with pytest.raises(ValueError):
            safe_read_file(str(symlink / "passwd"))
```

### Integration Tests

```python
# tests/test_security_integration.py
def test_cannot_exploit_via_cli():
    """Test that CLI cannot be exploited for file access."""
    import subprocess

    result = subprocess.run(
        ['pydocq', '../../../etc/passwd'],
        capture_output=True,
        text=True
    )

    assert result.returncode != 0
    assert 'traversal' in result.stderr.lower() or 'outside' in result.stderr.lower()
```

## Implementation Priority

1. **Immediate (P0):** Implement Option 1 or Option 4 (quick fix)
2. **Short-term (P1):** Add configuration file support (Option 2)
3. **Long-term (P2):** Consider sandboxed execution (Option 3)

## Security Best Practices

1. **Always validate file paths** before reading
2. **Use absolute paths** for comparisons
3. **Implement allowlist approach** (whitelist safe directories)
4. **Normalize paths** before validation
5. **Block symbolic links** that point outside safe directories
6. **Limit file size** to prevent DoS
7. **Log blocked access attempts** for monitoring

## Related Issues

- [SEC-001: Dynamic Import Without Sanitization](./001-dynamic-import-without-sanitization.md)
- [SEC-003: Code Execution via AST](./003-code-execution-via-ast.md)

## References

- [CWE-22: Path Traversal](https://cwe.mitre.org/data/definitions/22.html)
- [CWE-23: Relative Path Traversal](https://cwe.mitre.org/data/definitions/23.html)
- [OWASP Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)
- [Python File I/O Security](https://docs.python.org/3/library/os.html#os.filesystem)

## Checklist

- [ ] Implement path validation before file reads
- [ ] Add directory allowlist functionality
- [ ] Add path traversal detection
- [ ] Block symbolic links to unsafe locations
- [ ] Add file size limits
- [ ] Add security test suite
- [ ] Add audit logging for blocked file access
- [ ] Update documentation with security guidelines
- [ ] Add configuration file support
