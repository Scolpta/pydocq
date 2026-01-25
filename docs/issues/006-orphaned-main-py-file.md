# Issue QUAL-003: Orphaned main.py File

## Description

A `main.py` file exists at the project root containing placeholder code, but the actual CLI entry point is defined as `docs_cli/cli.py` in `pyproject.toml`. This creates confusion about the project structure and which file is the actual entry point.

## Problem Details

### Orphaned File

```python
# main.py (project root - unused)
def main():
    print("Hello from docs-cli!")

if __name__ == "__main__":
    main()
```

### Actual Entry Point Configuration

```toml
# pyproject.toml:55
[project.scripts]
pydocq = "docs_cli.cli:app"  # Uses cli.py, not main.py
```

### Real Entry Point

```python
# docs_cli/cli.py (actual entry point)
from typer import Typer

app = Typer(
    help="Query Python package documentation for AI agents",
    no_args_is_help=True,
    add_completion=False,
)

@app.command()
def query(
    target: str,
    # ...
) -> None:
    """Query Python package documentation."""
    # ...

if __name__ == "__main__":
    app()
```

### Issues Identified

| Issue | Impact | Severity |
|-------|--------|----------|
| **Confusion** | Developers don't know which file is entry point | Low |
| **Dead Code** | File exists but is not used | Low |
| **Maintenance Burden** | File might get updated unnecessarily | Low |
| **Documentation Inconsistency** | May be referenced in docs incorrectly | Low |
| **Git History** | Shows up in diffs but doesn't affect functionality | Minimal |

## Impact Assessment

| Impact Type | Severity | Description |
|-------------|----------|-------------|
| Developer Experience | 🟢 Low | Minor confusion about project structure |
| Code Quality | 🟢 Low | Small amount of dead code |
| Documentation | 🟢 Low | Could lead to incorrect documentation |
| Build Process | 🟢 Low | No impact (correct entry point in pyproject.toml) |
| User Experience | 🟢 Low | No impact (users use CLI, not this file) |

## Investigation Results

### Checking File Usage

```bash
# Check if main.py is imported anywhere
$ grep -r "from main import" .
$ grep -r "import main" .
# No results - file is not imported

# Check if it's referenced in documentation
$ grep -r "main.py" docs/
$ grep -r "main.py" README.md
# No results - not documented

# Check pyproject.toml entry point
$ grep -A2 "\[project.scripts\]" pyproject.toml
pydocq = "docs_cli.cli:app"  # Uses cli.py, not main.py
```

### File History Analysis

The `main.py` file appears to be a vestige from early project development, likely created during initial setup before the proper CLI structure (`docs_cli/cli.py`) was implemented.

## Recommended Fix

### Option 1: Delete the File (Recommended)

**Rationale:** The file serves no purpose and creates confusion.

```bash
# Simply delete the file
rm main.py

# Verify CLI still works
pydocq --version
# Should work fine
```

**Benefits:**
- Removes confusion
- Cleans up project structure
- No loss of functionality

**Risks:**
- None - file is not used anywhere

### Option 2: Document as Development/Testing Entry Point

If the file is intentionally kept for development/testing:

```python
# main.py
"""
Development and testing entry point.

This file is NOT used in production. The actual CLI entry point is
docs_cli/cli.py, which is configured in pyproject.toml:

    [project.scripts]
    pydocq = "docs_cli.cli:app"

This file is kept for manual testing and development convenience.
"""

def run_tests():
    """Run quick development tests."""
    print("Running development tests...")
    # Add test code here

def manual_test():
    """Manual testing function."""
    print("Manual testing mode")
    # Add manual test code here

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test":
        run_tests()
    else:
        print("Use 'python main.py test' for development testing")
        print("For normal usage, use: pydocq <command>")
```

### Option 3: Convert to Development Helper

Make the file useful for development:

```python
# main.py
"""
Development helper script for pydocq.

This script provides convenience functions for development and testing.
It is NOT part of the production CLI.
"""

import subprocess
import sys


def run_tests():
    """Run the test suite."""
    print("Running tests...")
    subprocess.run([sys.executable, "-m", "pytest", "-v"])


def run_coverage():
    """Run tests with coverage report."""
    print("Running tests with coverage...")
    subprocess.run([
        sys.executable, "-m", "pytest",
        "--cov=docs_cli",
        "--cov-report=html",
        "-v"
    ])


def lint():
    """Run linting tools."""
    print("Running linters...")
    subprocess.run([sys.executable, "-m", "ruff", "check", "."])
    subprocess.run([sys.executable, "-m", "black", "--check", "."])


def format_code():
    """Format code with black."""
    print("Formatting code...")
    subprocess.run([sys.executable, "-m", "black", "."])


def install_dev():
    """Install package in development mode."""
    print("Installing in development mode...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."])


def main():
    """Main development helper entry point."""
    if len(sys.argv) < 2:
        print("Usage: python main.py <command>")
        print()
        print("Available commands:")
        print("  test      - Run test suite")
        print("  coverage  - Run tests with coverage")
        print("  lint      - Run linting (ruff + black check)")
        print("  format    - Format code with black")
        print("  install   - Install in development mode")
        print()
        print("For normal CLI usage, use: pydocq <command>")
        sys.exit(1)

    command = sys.argv[1]

    commands = {
        "test": run_tests,
        "coverage": run_coverage,
        "lint": lint,
        "format": format_code,
        "install": install_dev,
    }

    if command in commands:
        commands[command]()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

### Option 4: Add to .gitignore (Alternative)

If the file is used locally but not needed in repo:

```bash
# .gitignore
# Development scripts
main.py
dev.py
```

Then developers can have their own local `main.py` for testing.

## Testing

### Verification Steps

After making changes:

```bash
# 1. Verify CLI still works
pydocq --help
# Should show help text

# 2. Verify package can be imported
python -c "from docs_cli.cli import app; print('OK')"
# Should print "OK"

# 3. Verify entry point
pip show pydocq | grep "Entry-points"
# Should show: pydocq=docs_cli.cli:app

# 4. Run tests
pytest
# Should pass all tests
```

## Documentation Updates

If Option 1 is chosen (delete file), no documentation updates needed.

If Option 2 or 3 is chosen (keep as dev helper), update:

```markdown
# README.md (add Development section)

## Development

### Development Helper Script

For development convenience, a `main.py` helper script is available:

\`\`\`bash
# Run tests
python main.py test

# Run coverage
python main.py coverage

# Lint code
python main.py lint

# Format code
python main.py format
\`\`\`

**Note:** This script is for development only. The production CLI entry point
is `docs_cli/cli.py`, configured in `pyproject.toml`.
```

## Migration Plan

### If Deleting (Option 1)

1. [ ] Verify file is not used anywhere
2. [ ] Delete `main.py`
3. [ ] Run full test suite
4. [ ] Verify CLI still works
5. [ ] Update documentation if it references `main.py`

### If Keeping as Dev Helper (Option 3)

1. [ ] Rewrite `main.py` with development helpers
2. [ ] Add documentation to `README.md`
3. [ ] Add comment explaining it's for development only
4. [ ] Test all helper commands
5. [ ] Update CONTRIBUTING.md if needed

## Benefits of Fix

| Benefit | Impact |
|---------|--------|
| **Clarity** | Clearer project structure |
| **Less Confusion** | Developers know which file matters |
| **Cleaner Repository** | Removes dead code |
| **Better Development UX** | If converted to dev helper |

## Related Issues

- [QUAL-001: Code Duplication - Type Detection](./004-code-duplication-type-detection.md)
- [QUAL-002: Exception Handling Inconsistencies](./005-exception-handling-inconsistencies.md)

## Checklist

- [ ] Verify `main.py` is not used anywhere
- [ ] Choose fix approach (delete or convert to dev helper)
- [ ] If deleting: remove file
- [ ] If keeping: rewrite with development helpers
- [ ] Update documentation
- [ ] Run test suite
- [ ] Verify CLI still works
- [ ] Commit changes with clear message
