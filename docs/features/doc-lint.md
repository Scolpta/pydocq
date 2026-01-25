# Documentation Linter / Quality Checker

Analyze documentation quality and suggest improvements.

## Usage

```bash
doc-lint mypackage
doc-lint mymodule.py
doc-lint mypackage --completeness
doc-lint mypackage --accuracy
```

## Examples

### Basic Linting

```bash
doc-lint mypackage
```

Output:
```json
{
  "overall_score": "B+",
  "score_breakdown": {
    "completeness": 78,
    "accuracy": 85,
    "consistency": 72,
    "style": 90
  },
  "summary": {
    "total_elements": 45,
    "documented": 35,
    "needs_work": 10,
    "critical_issues": 2
  }
}
```

### Completeness Check

```bash
doc-lint mypackage --completeness
```

Output:
```json
{
  "completeness_score": 78,
  "missing_items": [
    {
      "file": "mymodule.py",
      "element": "process",
      "type": "function",
      "issue": "missing_docstring",
      "severity": "high"
    },
    {
      "file": "mymodule.py",
      "element": "transform",
      "type": "function",
      "issue": "missing_parameter_docs",
      "severity": "medium",
      "details": ["Parameter 'opts' not documented"]
    },
    {
      "file": "mymodule.py",
      "element": "DataProcessor",
      "type": "class",
      "issue": "missing_class_docstring",
      "severity": "high"
    },
    {
      "file": "mymodule.py",
      "element": "analyze",
      "type": "function",
      "issue": "missing_return_doc",
      "severity": "medium"
    }
  ],
  "coverage": {
    "functions": "82%",
    "classes": "100%",
    "methods": "65%",
    "modules": "100%"
  }
}
```

### Accuracy Check

```bash
doc-lint mypackage --accuracy
```

Output:
```json
{
  "accuracy_score": 85,
  "issues": [
    {
      "file": "mymodule.py",
      "element": "process",
      "issue": "docstring_mismatch",
      "severity": "medium",
      "details": "Docstring says returns int, but actually returns str"
    },
    {
      "file": "mymodule.py",
      "element": "validate",
      "issue": "wrong_parameter_type",
      "severity": "high",
      "details": "Documented as int, actual type is str"
    },
    {
      "file": "mymodule.py",
      "element": "transform",
      "issue": "deprecated_not_marked",
      "severity": "low",
      "details": "Docstring mentions deprecated but no @deprecated decorator"
    }
  ]
}
```

### Example Validation

```bash
doc-lint mypackage --validate-examples
```

Output:
```json
{
  "examples_checked": 23,
  "examples_passed": 20,
  "examples_failed": 3,
  "failures": [
    {
      "file": "mymodule.py",
      "element": "process",
      "example": "process([1, 2, 3])",
      "error": "NameError: name 'process' is not defined",
      "line": 15
    },
    {
      "file": "mymodule.py",
      "element": "transform",
      "example": "transform(df)",
      "error": "AssertionError: Expected DataFrame, got None",
      "line": 42
    }
  ]
}
```

### Consistency Check

```bash
doc-lint mypackage --consistency
```

Output:
```json
{
  "consistency_score": 72,
  "issues": [
    {
      "issue": "inconsistent_docstring_style",
      "details": "Mix of Google and NumPy style docstrings",
      "affected_files": ["mymodule.py", "utils.py"]
    },
    {
      "issue": "inconsistent_parameter_order",
      "details": "Parameters documented in different order than signature",
      "elements": ["process", "transform"]
    },
    {
      "issue": "inconsistent_naming",
      "details": "Some functions use snake_case, others use camelCase",
      "elements": ["processData", "transform_data"]
    }
  ]
}
```

### Style Check

```bash
doc-lint mypackage --style
```

Output:
```json
{
  "style_score": 90,
  "issues": [
    {
      "file": "mymodule.py",
      "element": "process",
      "issue": "docstring_too_short",
      "severity": "low",
      "details": "Docstring is only 5 characters, minimum 50 recommended",
      "suggestion": "Add more detail about what process() does"
    },
    {
      "file": "mymodule.py",
      "element": "transform",
      "issue": "no_examples",
      "severity": "medium",
      "suggestion": "Add @example decorators with usage examples"
    }
  ]
}
```

## Lint Rules

### Completeness Rules

| Rule | Severity | Description |
|------|----------|-------------|
| `missing_docstring` | high | Element has no docstring |
| `missing_parameter_docs` | medium | Parameters not documented |
| `missing_return_doc` | medium | Return value not documented |
| `missing_raises_doc` | low | Exceptions not documented |
| `missing_examples` | low | No examples provided |
| `empty_docstring` | high | Docstring is empty |

### Accuracy Rules

| Rule | Severity | Description |
|------|----------|-------------|
| `docstring_mismatch` | high | Docstring doesn't match implementation |
| `wrong_parameter_type` | high | Documented type doesn't match actual |
| `wrong_return_type` | high | Documented return type doesn't match |
| `deprecated_not_marked` | medium | Deprecation mentioned but not marked |
| `example_fails` | high | Example code doesn't run |

### Consistency Rules

| Rule | Severity | Description |
|------|----------|-------------|
| `inconsistent_docstring_style` | medium | Mixed docstring styles |
| `inconsistent_parameter_order` | low | Param order differs from signature |
| `inconsistent_naming` | medium | Inconsistent naming conventions |
| `inconsistent_category` | low | Similar functions have different categories |

### Style Rules

| Rule | Severity | Description |
|------|----------|-------------|
| `docstring_too_short` | low | Docstring below minimum length |
| `no_examples` | low | No usage examples |
| `no_type_hints` | low | Missing type annotations |
| `vague_description` | low | Description is too vague |
| `missing_metadata` | low | No SDK metadata added |

## Configuration

### Lint Configuration

```yaml
# .docs-cli/lint-config.yaml
rules:
  enabled:
    - missing_docstring
    - missing_parameter_docs
    - docstring_mismatch
    - example_fails
  disabled:
    - missing_examples  # Optional
    - no_type_hints     # Optional

thresholds:
  docstring_min_length: 50
  max_parameter_count: 7
  require_examples_for: "public"

severity:
  missing_docstring: high
  docstring_too_short: low

style:
  docstring_style: google  # google, numpy, rest
  require_categories: true
  require_metadata: false
```

### Per-File Configuration

```yaml
# .docs-cli/lint-config.yaml
overrides:
  "tests/*":
    rules:
      disabled:
        - missing_docstring
        - missing_examples
  "migrations/*":
    rules:
      disabled:
        - deprecated_not_marked
```

## Auto-Fix

### Fix Auto-Fixable Issues

```bash
doc-lint mypackage --auto-fix
```

Automatically fixes:
- Adds basic docstrings
- Fixes parameter order
- Standardizes docstring style
- Adds type hints from inference

Output:
```json
{
  "fixed": 15,
  "skipped": 8,
  "failed": 2,
  "changes": [
    {
      "file": "mymodule.py",
      "element": "process",
      "fix": "added_docstring"
    }
  ]
}
```

### Dry Run

```bash
doc-lint mypackage --auto-fix --dry-run
```

Shows what would be fixed without making changes.

### Selective Fix

```bash
doc-lint mypackage --auto-fix --rule missing_docstring
```

Only fixes specific rule violations.

## Lint Profiles

### Strict Profile

```bash
doc-lint mypackage --profile strict
```

All rules enabled, high thresholds.

### Lenient Profile

```bash
doc-lint mypackage --profile lenient
```

Only critical issues, low thresholds.

### Custom Profile

```bash
doc-lint mypackage --profile .docs-cli/my-profile.yaml
```

Uses custom profile configuration.

## Use Cases for Agents

### Documentation Review

```python
# Agent: "Review documentation quality"

1. doc-lint mypackage
2. Gets overall score: B+
3. Identifies areas for improvement
4. "Your documentation is good but could be better:
    - Add docstrings to 3 functions
    - Document 2 missing parameters
    - Fix 2 docstring mismatches"
```

### Pre-Commit Checks

```python
# Git hook: Check documentation before commit

1. doc-lint --only-changed
2. Checks only modified files
3. Blocks commit if score < B
4. "Fix documentation issues before committing"
```

### Continuous Integration

```yaml
# .github/workflows/doc-lint.yml
- name: Lint documentation
  run: doc-lint mypackage --fail-on error
```

CI fails if documentation quality is poor.

### Improving Coverage

```python
# Agent: "Improve documentation coverage"

1. doc-lint mypackage --completeness
2. Identifies missing documentation
3. Generates templates for missing items
4. "Fill in these templates to reach 100% coverage"
```

### Validation

```python
# Agent: "Validate examples before release"

1. doc-lint mypackage --validate-examples
2. Runs all examples
3. Reports failures
4. "Fix these 3 broken examples before releasing"
```

### Migration Assistance

```python
# Agent: "Update documentation for new version"

1. doc-lint mypackage --accuracy
2. Detects mismatches with code
3. Suggests updates
4. "These 5 functions changed, update docs"
```

## Lint Output Formats

### JSON

```bash
doc-lint mypackage --format json
```

Machine-readable JSON output.

### HTML Report

```bash
doc-lint mypackage --format html --output report.html
```

Generates interactive HTML report.

### Markdown

```bash
doc-lint mypackage --format markdown --output REPORT.md
```

Generates markdown report.

### Console

```bash
doc-lint mypackage --format console
```

Human-readable console output with colors.

## Lint Filtering

### By Severity

```bash
doc-lint mypackage --severity high
```

Only shows high severity issues.

### By Rule

```bash
doc-lint mypackage --rule missing_docstring
```

Only checks for missing docstrings.

### By Element Type

```bash
doc-lint mypackage --type function
doc-lint mypackage --type class
```

Only checks specific element types.

### By Path

```bash
doc-lint mypackage --path "mymodule.py"
doc-lint mypackage --path "tests/*"
```

Only checks specific paths.

## Lint History

### Track Progress

```bash
doc-lint mypackage --track
```

Stores lint results over time:
```json
{
  "history": [
    {"date": "2024-01-10", "score": "C+", "issues": 45},
    {"date": "2024-01-12", "score": "B", "issues": 32},
    {"date": "2024-01-15", "score": "B+", "issues": 23}
  ],
  "trend": "improving"
}
```

### Compare Runs

```bash
doc-lint mypackage --compare-with HEAD~1
```

Shows changes since last commit.

## Lint Integration

### With Editor

```bash
doc-lint --watch mypackage
```

Watches files and shows issues in editor.

### With Pre-Commit

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: doc-lint
        name: Lint documentation
        entry: doc-lint
        language: system
```

### With CI/CD

```yaml
# GitHub Actions
- name: Lint docs
  run: |
    doc-lint mypackage --format json --output lint.json
    # Post results to PR
```

## Lint API

```python
from docs_cli import Linter

linter = Linter()

# Run linter
results = linter.lint("mypackage")

# Filter results
high_severity = results.filter(severity="high")
missing_docs = results.filter(rule="missing_docstring")

# Get score
score = results.get_score()
print(f"Overall: {score}")

# Auto-fix
fixed = results.auto_fix()
print(f"Fixed {fixed.count} issues")

# Generate report
html = results.to_html()
markdown = results.to_markdown()
```

Programmatic access to linting functionality.

## Custom Rules

### Define Custom Rule

```python
# .docs-cli/rules/custom_rules.py
from docs_cli.lint import Rule

class CompanyStandardRule(Rule):
    """Ensure company documentation standards."""

    def check(self, element):
        issues = []

        # Must have @category decorator
        if not element.has_decorator("category"):
            issues.append({
                "rule": "missing_category",
                "severity": "medium",
                "message": "Missing @category decorator"
            })

        # Must have @note if performance-critical
        if element.has_tag("performance-critical"):
            if not element.has_decorator("note"):
                issues.append({
                    "rule": "missing_performance_note",
                    "severity": "low",
                    "message": "Add @note for performance characteristics"
                })

        return issues
```

### Register Custom Rule

```bash
doc-lint mypackage --rules .docs-cli/rules/custom_rules.py
```

## Lint Best Practices

### Run Regularly

```bash
# Pre-commit hook
doc-lint --only-changed --fail-on error

# Weekly CI job
doc-lint mypackage --track
```

### Fix Incrementally

```bash
# Fix critical issues first
doc-lint mypackage --severity high --auto-fix

# Then medium and low
doc-lint mypackage --severity medium --auto-fix
```

### Set Realistic Goals

```yaml
# Target 80% coverage, not 100%
thresholds:
  min_coverage: 80
  min_score: B
```

### Use Templates

```bash
# Generate templates first
doc-template generate-module mymodule

# Then fill in documentation
# Finally lint to check quality
doc-lint mypackage
```
