# Issue FEAT-005: Version Diff / Change Detection

## Description

Implement comparison of API elements across different versions to detect breaking changes, additions, and modifications. This feature is already documented in `docs/features/diff.md` but needs implementation.

## Problem Details

### Current State

The diff feature is **fully documented but not implemented**:

- Documentation exists: `docs/features/diff.md`
- No CLI implementation
- No backend logic
- Cannot compare versions

### Use Cases

1. **Migration assistance**
   ```bash
   $ pydocq pandas.DataFrame.merge --diff v1.5.0..v2.0.0
   ```

2. **Breaking change detection**
   ```bash
   $ pydocq pandas --diff v1.5..v2.0 --breaking-only
   ```

3. **Git history comparison**
   ```bash
   $ pydocq my_module.process --diff HEAD~5
   ```

### Requirements from Documentation

Based on `docs/features/diff.md`, the implementation must support:

- Version tag comparison (v1.5.0..v2.0.0)
- Git commit comparison (abc123..def456)
- Git relative references (HEAD~5, main..feature)
- Breaking change detection
- Signature changes
- Documentation changes
- Structural changes (methods added/removed)

## Impact Assessment

| Impact Type | Severity | Description |
|-------------|----------|-------------|
| Migration Support | 🟢 High | Enables API migration workflows |
| Breaking Changes | 🟢 High | Detect incompatible changes |
| Documentation | 🟡 Medium | Docs already exist, just need implementation |
| Enterprise Value | 🟡 Medium | Critical for large codebases |
| Complexity | 🟡 Medium | Requires git integration |

## Recommended Implementation

### Architecture

```
┌─────────────────────────────────────────────┐
│ CLI: --diff option                          │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│ VersionFetcher                              │
│ - fetch_version_tags()                      │
│ - fetch_git_commits()                       │
│ - checkout_version()                        │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│ ElementInspector (2 instances)              │
│ - inspect at version A                      │
│ - inspect at version B                      │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│ DiffAnalyzer                                │
│ - compare_signatures()                      │
│ - detect_breaking_changes()                 │
│ - categorize_changes()                      │
└──────────────┬──────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│ DiffFormatter                               │
│ - format_diff_json()                        │
│ - format_diff_summary()                     │
│ - format_diff_markdown()                    │
└─────────────────────────────────────────────┘
```

### Implementation

```python
# pydocq/analyzer/diff_analyzer.py

import tempfile
import subprocess
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from enum import Enum

class ChangeType(Enum):
    """Types of changes between versions."""
    PARAMETER_ADDED = "parameter_added"
    PARAMETER_REMOVED = "parameter_removed"
    PARAMETER_CHANGED = "parameter_changed"
    PARAMETER_RENAMED = "parameter_renamed"
    RETURN_TYPE_CHANGED = "return_type_changed"
    DOCSTRING_UPDATED = "docstring_updated"
    METHOD_ADDED = "method_added"
    METHOD_REMOVED = "method_removed"
    IMPLEMENTATION_CHANGED = "implementation_changed"


@dataclass
class Change:
    """Represents a single change."""
    type: ChangeType
    description: str
    breaking: bool = False
    old_value: Optional[str] = None
    new_value: Optional[str] = None


@dataclass
class DiffResult:
    """Result of comparing two versions."""
    path: str
    version_from: str
    version_to: str
    changes: list[Change] = field(default_factory=list)
    breaking: bool = False
    summary: dict = field(default_factory=dict)


class VersionFetcher:
    """Fetch different versions of code for comparison."""

    def __init__(self, repo_path: str = "."):
        """Initialize version fetcher.

        Args:
            repo_path: Path to git repository
        """
        self.repo_path = Path(repo_path)

    def fetch_version(self, version_ref: str) -> Path:
        """Fetch a specific version and return code path.

        Args:
            version_ref: Git reference (tag, commit, branch)

        Returns:
            Path to temporary directory with version code
        """
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix=f"pydocq_diff_{version_ref}_")
        temp_path = Path(temp_dir)

        try:
            # Clone repository at specific version
            subprocess.run(
                [
                    "git", "clone",
                    "--depth", "1",
                    "--branch", version_ref,
                    str(self.repo_path),
                    str(temp_path)
                ],
                check=True,
                capture_output=True
            )

            return temp_path

        except subprocess.CalledProcessError as e:
            # Try as commit hash
            try:
                subprocess.run(
                    [
                        "git", "clone",
                        str(self.repo_path),
                        str(temp_path)
                    ],
                    check=True,
                    capture_output=True
                )

                # Checkout specific commit
                subprocess.run(
                    ["git", "checkout", version_ref],
                    cwd=str(temp_path),
                    check=True,
                    capture_output=True
                )

                return temp_path

            except subprocess.CalledProcessError:
                raise ValueError(
                    f"Failed to fetch version {version_ref}: {e.stderr.decode()}"
                )


class DiffAnalyzer:
    """Analyze differences between two versions."""

    def compare_signatures(
        self,
        signature_old: dict,
        signature_new: dict
    ) -> list[Change]:
        """Compare function signatures.

        Args:
            signature_old: Old signature dict
            signature_new: New signature dict

        Returns:
            List of changes detected
        """
        changes = []

        old_params = {p["name"]: p for p in signature_old.get("parameters", [])}
        new_params = {p["name"]: p for p in signature_new.get("parameters", [])}

        # Check for removed parameters (breaking)
        for name, param in old_params.items():
            if name not in new_params:
                changes.append(Change(
                    type=ChangeType.PARAMETER_REMOVED,
                    description=f"Parameter '{name}' removed",
                    breaking=True,
                    old_value=self._format_param(param)
                ))

        # Check for added parameters
        for name, param in new_params.items():
            if name not in old_params:
                # Check if it has a default value
                if param.get("default") is None:
                    changes.append(Change(
                        type=ChangeType.PARAMETER_ADDED,
                        description=f"Required parameter '{name}' added",
                        breaking=True,
                        new_value=self._format_param(param)
                    ))
                else:
                    changes.append(Change(
                        type=ChangeType.PARAMETER_ADDED,
                        description=f"Optional parameter '{name}' added",
                        breaking=False,
                        new_value=self._format_param(param)
                    ))

            else:
                # Check for parameter changes
                old_param = old_params[name]
                new_param = new_params[name]

                # Type change
                if old_param.get("annotation") != new_param.get("annotation"):
                    changes.append(Change(
                        type=ChangeType.PARAMETER_CHANGED,
                        description=f"Parameter '{name}' type changed",
                        breaking=self._is_breaking_type_change(
                            old_param.get("annotation"),
                            new_param.get("annotation")
                        ),
                        old_value=old_param.get("annotation"),
                        new_value=new_param.get("annotation")
                    ))

                # Default change
                if old_param.get("default") != new_param.get("default"):
                    changes.append(Change(
                        type=ChangeType.PARAMETER_CHANGED,
                        description=f"Parameter '{name}' default changed",
                        breaking=self._is_breaking_default_change(
                            old_param.get("default"),
                            new_param.get("default")
                        ),
                        old_value=str(old_param.get("default")),
                        new_value=str(new_param.get("default"))
                    ))

        # Check return type change
        old_return = signature_old.get("return_type")
        new_return = signature_new.get("return_type")

        if old_return != new_return:
            changes.append(Change(
                type=ChangeType.RETURN_TYPE_CHANGED,
                description="Return type changed",
                breaking=self._is_breaking_type_change(old_return, new_return),
                old_value=old_return,
                new_value=new_return
            ))

        return changes

    def compare_docstrings(
        self,
        docstring_old: Optional[str],
        docstring_new: Optional[str]
    ) -> list[Change]:
        """Compare docstrings.

        Args:
            docstring_old: Old docstring
            docstring_new: New docstring

        Returns:
            List of changes (usually 0 or 1)
        """
        changes = []

        if docstring_old != docstring_new:
            changes.append(Change(
                type=ChangeType.DOCSTRING_UPDATED,
                description="Docstring updated",
                breaking=False,
                old_value=docstring_old[:100] if docstring_old else None,
                new_value=docstring_new[:100] if docstring_new else None
            ))

        return changes

    def detect_breaking_changes(self, changes: list[Change]) -> bool:
        """Determine if any changes are breaking.

        Args:
            changes: List of changes to check

        Returns:
            True if any breaking changes found
        """
        return any(change.breaking for change in changes)

    def _format_param(self, param: dict) -> str:
        """Format parameter for display.

        Args:
            param: Parameter dict

        Returns:
            Formatted parameter string
        """
        name = param.get("name", "unknown")
        annotation = param.get("annotation", "Any")
        default = param.get("default")

        if default is None:
            return f"{name}: {annotation}"
        else:
            return f"{name}: {annotation} = {default}"

    def _is_breaking_type_change(self, old_type: str, new_type: str) -> bool:
        """Determine if type change is breaking.

        Args:
            old_type: Old type annotation
            new_type: New type annotation

        Returns:
            True if breaking change
        """
        # Simplified heuristic
        # Going from specific to general is usually OK
        # Going from general to specific is breaking

        if old_type == "Any":
            return True  # Any -> specific is breaking

        if new_type == "Any":
            return False  # specific -> Any is OK

        # More specific analysis would go here
        return False

    def _is_breaking_default_change(self, old_default, new_default) -> bool:
        """Determine if default change is breaking.

        Args:
            old_default: Old default value
            new_default: New default value

        Returns:
            True if breaking change
        """
        # Changing from None to something else is breaking
        if old_default in [None, "None"] and new_default not in [None, "None"]:
            return True

        return False


def compare_versions(
    path: str,
    version_from: str,
    version_to: str,
    repo_path: str = "."
) -> DiffResult:
    """Compare an element across two versions.

    Args:
        path: Element path (e.g., pandas.DataFrame.merge)
        version_from: Starting version (tag, commit, etc.)
        version_to: Ending version
        repo_path: Path to git repository

    Returns:
        DiffResult with all changes
    """
    from pydocq.analyzer.resolver import resolve_path
    from pydocq.analyzer.inspector import inspect_element

    fetcher = VersionFetcher(repo_path)
    analyzer = DiffAnalyzer()

    # Fetch both versions
    with tempfile.TemporaryDirectory() as temp_base:
        path_from = fetcher.fetch_version(version_from)
        path_to = fetcher.fetch_version(version_to)

        try:
            # Inspect at version_from
            # (This would require modifying resolver to use custom PYTHONPATH)
            # For now, this is pseudocode

            # inspect_old = inspect_element_at_path(path, path_from)
            # inspect_new = inspect_element_at_path(path, path_to)

            # Compare signatures
            # changes = analyzer.compare_signatures(
            #     inspect_old.signature,
            #     inspect_new.signature
            # )

            # Compare docstrings
            # changes.extend(analyzer.compare_docstrings(
            #     inspect_old.docstring,
            #     inspect_new.docstring
            # ))

            return DiffResult(
                path=path,
                version_from=version_from,
                version_to=version_to,
                # changes=changes,
                # breaking=analyzer.detect_breaking_changes(changes)
            )

        finally:
            # Cleanup
            import shutil
            shutil.rmtree(path_from, ignore_errors=True)
            shutil.rmtree(path_to, ignore_errors=True)
```

### CLI Integration

```python
# pydocq/cli.py

@app.command()
def query(
    target: str,
    diff: str = Option(None, "--diff", help="Compare versions (e.g., v1.0..v2.0, HEAD~5)"),
    breaking_only: bool = Option(False, "--breaking-only", help="Show only breaking changes"),
    # ... existing options
) -> None:
    """Query Python package documentation."""
    if diff:
        from pydocq.analyzer.diff_analyzer import compare_versions

        # Parse version range
        if ".." in diff:
            version_from, version_to = diff.split("..", 1)
        else:
            # Single version, compare to current
            version_from = diff
            version_to = "HEAD"

        # Compare
        result = compare_versions(
            path=target,
            version_from=version_from.strip(),
            version_to=version_to.strip(),
            repo_path="."
        )

        # Filter if breaking only
        if breaking_only:
            result.changes = [c for c in result.changes if c.breaking]

        # Output
        output = {
            "path": result.path,
            "versions": {
                "from": result.version_from,
                "to": result.version_to
            },
            "changes": [
                {
                    "type": c.type.value,
                    "description": c.description,
                    "breaking": c.breaking,
                    "old": c.old_value,
                    "new": c.new_value
                }
                for c in result.changes
            ],
            "breaking": result.breaking
        }

        sys.stdout.write(json.dumps(output, indent=2))
        return

    # ... existing code
```

## Output Examples

### Example 1: Breaking Changes

**Input:**
```bash
$ pydocq pandas.DataFrame.merge --diff v1.5.0..v2.0.0
```

**Output:**
```json
{
  "path": "pandas.DataFrame.merge",
  "versions": {
    "from": "v1.5.0",
    "to": "v2.0.0"
  },
  "changes": [
    {
      "type": "parameter_added",
      "description": "Required parameter 'validate' added",
      "breaking": true,
      "old": null,
      "new": "validate: bool = None"
    },
    {
      "type": "parameter_changed",
      "description": "Parameter 'how' type changed",
      "breaking": true,
      "old": "str",
      "new": "Literal['inner', 'outer', 'left', 'right']"
    }
  ],
  "breaking": true
}
```

### Example 2: Breaking Only

**Input:**
```bash
$ pydocq pandas --diff v1.5..v2.0 --breaking-only
```

**Output:**
```json
{
  "path": "pandas",
  "versions": {"from": "v1.5", "to": "v2.0"},
  "breaking_changes": [
    {
      "element": "pandas.DataFrame.ix",
      "type": "method_removed",
      "reason": "Removed in favor of loc/iloc",
      "migration": "Replace df.ix[...] with df.loc[...] or df.iloc[...]"
    }
  ]
}
```

## Testing

```python
# tests/test_diff_analyzer.py
import pytest
from pydocq.analyzer.diff_analyzer import DiffAnalyzer, Change, ChangeType

class TestDiffAnalyzer:
    """Test suite for diff analysis."""

    def test_compare_signatures_no_change(self):
        """Test that identical signatures produce no changes."""
        analyzer = DiffAnalyzer()

        sig = {
            "parameters": [
                {"name": "x", "annotation": "int", "default": None}
            ],
            "return_type": "int"
        }

        changes = analyzer.compare_signatures(sig, sig)

        assert len(changes) == 0

    def test_detect_added_parameter(self):
        """Test detection of added parameter."""
        analyzer = DiffAnalyzer()

        old_sig = {"parameters": [], "return_type": "None"}
        new_sig = {
            "parameters": [
                {"name": "x", "annotation": "int", "default": None}
            ],
            "return_type": "None"
        }

        changes = analyzer.compare_signatures(old_sig, new_sig)

        assert len(changes) == 1
        assert changes[0].type == ChangeType.PARAMETER_ADDED
        assert changes[0].breaking is True

    def test_detect_removed_parameter(self):
        """Test detection of removed parameter."""
        analyzer = DiffAnalyzer()

        old_sig = {
            "parameters": [
                {"name": "x", "annotation": "int", "default": None}
            ],
            "return_type": "None"
        }
        new_sig = {"parameters": [], "return_type": "None"}

        changes = analyzer.compare_signatures(old_sig, new_sig)

        assert len(changes) == 1
        assert changes[0].type == ChangeType.PARAMETER_REMOVED
        assert changes[0].breaking is True

    def test_detect_breaking_changes(self):
        """Test breaking change detection."""
        analyzer = DiffAnalyzer()

        changes = [
            Change(ChangeType.PARAMETER_ADDED, "test", breaking=True),
            Change(ChangeType.DOCSTRING_UPDATED, "test", breaking=False)
        ]

        assert analyzer.detect_breaking_changes(changes) is True
```

## Implementation Priority

1. **Phase 1 (P1):** Core diff logic
2. **Phase 1 (P1):** CLI integration
3. **Phase 2 (P2):** Git integration
4. **Testing (P1):** Unit tests
5. **Documentation (P2):** Update examples

## Migration Plan

### Phase 1: Core Logic (Week 1-2)
- [ ] Implement `DiffAnalyzer` class
- [ ] Implement signature comparison
- [ ] Implement docstring comparison
- [ ] Implement breaking change detection

### Phase 2: CLI Integration (Week 2)
- [ ] Add `--diff` option
- [ ] Add `--breaking-only` option
- [ ] Implement output formatting
- [ ] Add version range parsing

### Phase 3: Git Integration (Week 3)
- [ ] Implement `VersionFetcher`
- [ ] Add git checkout logic
- [ ] Add temporary directory handling
- [ ] Add error handling

### Phase 4: Testing (Week 3-4)
- [ ] Add unit tests for all comparison methods
- [ ] Add integration tests with real repos
- [ ] Test on pandas/numpy versions
- [ ] Performance testing

## Benefits

| Benefit | Impact |
|---------|--------|
| **Migration Support** | Easier API upgrades |
| **Breaking Changes** | Detect incompatible changes |
| **Documentation** | Already exists, just needs code |
| **Enterprise Value** | Critical for large projects |
| **Automation** | Automate migration checks |

## Related Issues

- [FEAT-001: Expose AST Analysis to CLI](./008-expose-ast-analysis-to-cli.md)
- [docs/features/diff.md](../features/diff.md) - Feature documentation

## References

- [Feature Documentation](../features/diff.md)
- [Git Documentation](https://git-scm.com/docs)

## Checklist

- [ ] Implement `DiffAnalyzer` class
- [ ] Implement `compare_signatures()` method
- [ ] Implement `compare_docstrings()` method
- [ ] Implement `detect_breaking_changes()` method
- [ ] Implement `VersionFetcher` class
- [ ] Implement `fetch_version()` method
- [ ] Add `--diff` CLI option
- [ ] Add `--breaking-only` CLI option
- [ ] Implement output formatting
- [ ] Add unit tests for all comparison methods
- [ ] Add integration tests
- [ ] Test on real repositories
- [ ] Update README with examples
