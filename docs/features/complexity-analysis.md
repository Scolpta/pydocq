# Complexity Analysis

Analyze code complexity metrics to help agents evaluate difficulty and testing needs.

## Usage

```bash
doc <element> --complexity
doc <package> --complexity-report  # Report on all elements
```

## Examples

### Function Complexity

```bash
doc pandas.DataFrame.__init__ --complexity
```

Output:
```json
{
  "path": "pandas.DataFrame.__init__",
  "complexity": {
    "cyclomatic": 8,
    "cognitive": 12,
    "loc": 150,
    "loc_commented": 40,
    "loc_blank": 20,
    "nesting_depth": 3,
    "num_parameters": 5,
    "num_branches": 4,
    "num_loops": 2,
    "num_expressions": 45,
    "has_recursion": false,
    "has_exceptions": true,
    "has_lambdas": true,
    "estimated_comprehension_time": "medium"
  }
}
```

### Class Complexity

```bash
doc pandas.DataFrame --complexity
```

Output:
```json
{
  "path": "pandas.DataFrame",
  "complexity": {
    "total_methods": 250,
    "public_methods": 180,
    "private_methods": 70,
    "class_methods": 5,
    "static_methods": 10,
    "properties": 45,
    "average_method_complexity": 6.2,
    "max_method_complexity": {
      "method": "__init__",
      "complexity": 8
    },
    "inheritance_depth": 2,
    "num_base_classes": 1,
    "num_subclasses": 3,
    "class_size": "large"
  }
}
```

### Module Complexity

```bash
doc pandas.core.frame --complexity
```

Output:
```json
{
  "path": "pandas.core.frame",
  "complexity": {
    "total_classes": 2,
    "total_functions": 15,
    "total_loc": 5432,
    "average_complexity": 5.4,
    "max_complexity": {
      "element": "DataFrame._sanitize_columns",
      "complexity": 12
    },
    "import_complexity": {
      "total_imports": 25,
      "circular_imports": false,
      "external_dependencies": 8
    }
  }
}
```

## Complexity Metrics Explained

### Cyclomatic Complexity

Number of linearly independent paths through code:

```
1 (base) + number of decision points

if → +1
elif → +1
for/while → +1
except → +1
and/or → +1
```

Interpretation:
- 1-10: Simple
- 11-20: Moderate
- 21-50: Complex
- 50+: Very complex

### Cognitive Complexity

How difficult is it to understand the code:

```python
# Cognitive complexity: 1
def simple(x):
    return x + 1

# Cognitive complexity: 4
def medium(x):
    if x > 0:        # +1 (nesting)
        for i in x:  # +1 (nesting +1)
            if i:    # +1 (nesting +1)
                pass
```

### Lines of Code (LOC)

```json
{
  "loc": 150,              # Total lines
  "loc_code": 90,          # Code only
  "loc_comment": 40,       # Comments
  "loc_blank": 20,         # Blank lines
  "loc_docstring": 15      # Docstrings
}
```

### Parameter Count

```json
{
  "num_parameters": 5,
  "num_required": 2,
  "num_optional": 3,
  "num_varargs": true,
  "num_kwargs": true,
  "parameter_risk": "medium"  # low | medium | high
}
```

More parameters → harder to use and test.

### Halstead Metrics

```bash
doc mymodule.process --complexity --halstead
```

Output:
```json
{
  "halstead": {
    "num_operators": 45,
    "num_operands": 78,
    "unique_operators": 12,
    "unique_operands": 32,
    "vocabulary": 44,
    "difficulty": 15.2,
    "effort": 12500,
    "estimated_bugs": 0.12
  }
}
```

## Use Cases for Agents

### Test Generation Priority

```python
# Agent: "What functions need the most testing?"

1. doc myproject --complexity-report
2. Sort by complexity
3. Focus on functions with complexity > 10
4. "Generate comprehensive tests for process_data() (complexity: 15)"
```

### Code Review Focus

```python
# Agent: "Review this pull request"

1. Check complexity of changed functions
2. Flag high complexity additions
3. "New function extract_data() has complexity 18. Consider simplifying."
```

### Refactoring Suggestions

```python
# Agent: "Suggest refactoring candidates"

1. doc myproject --complexity-report
2. Find high complexity functions
3. Suggest breaking them down
4. "split_data() (complexity: 22) could be split into 3 smaller functions"
```

### Documentation Strategy

```python
# Agent: "What needs more documentation?"

1. Check complexity vs documentation
2. High complexity + low docs → flag
3. "process() has complexity 18 but minimal docstring. Consider adding examples."
```

### Code Selection for Explanation

```python
# Agent: "Explain how this works"

1. Check complexity
2. If simple: explain directly
3. If complex: break down step by step
4. "This function is complex (15). Let me explain it in parts..."
```

## Complexity Profiles

### Simple Profile

```json
{
  "profile": "simple",
  "cyclomatic": 3,
  "nesting_depth": 1,
  "num_parameters": 2,
  "recommendation": "Easy to understand and test"
}
```

### Moderate Profile

```json
{
  "profile": "moderate",
  "cyclomatic": 8,
  "nesting_depth": 2,
  "num_parameters": 4,
  "recommendation": "Requires careful reading, moderate testing"
}
```

### Complex Profile

```json
{
  "profile": "complex",
  "cyclomatic": 18,
  "nesting_depth": 4,
  "num_parameters": 7,
  "recommendation": "Consider refactoring, needs comprehensive testing"
}
```

## Complexity Comparison

```bash
doc pandas --complexity --compare
```

Output:
```json
{
  "package": "pandas",
  "comparison": {
    "highest_complexity": {
      "element": "pandas.core.groupby.GroupBy._wrap_aggregated",
      "complexity": 24
    },
    "lowest_complexity": {
      "element": "pandas.DataFrame.shape",
      "complexity": 1
    },
    "average_complexity": 6.8,
    "percentile_ranks": {
      "pandas.DataFrame.__init__": 75
    }
  }
}
```

## Complexity Trends

```bash
doc myproject --complexity --history
```

Output:
```json
{
  "trends": [
    {
      "commit": "abc123",
      "date": "2024-01-10",
      "average_complexity": 5.2
    },
    {
      "commit": "def456",
      "date": "2024-01-15",
      "average_complexity": 6.8,
      "change": "+1.6",
      "trend": "increasing"
    }
  ]
}
```

## Complexity by Module

```bash
doc pandas --complexity --by-module
```

Output:
```json
{
  "modules": [
    {
      "module": "pandas.core.frame",
      "average_complexity": 6.2,
      "max_complexity": 12
    },
    {
      "module": "pandas.core.series",
      "average_complexity": 5.8,
      "max_complexity": 10
    }
  ]
}
```

## Complexity Thresholds

```bash
doc myproject --complexity --threshold 10
```

Output only elements exceeding threshold:
```json
{
  "threshold": 10,
  "exceeding": [
    {
      "path": "mypackage.process",
      "complexity": 15,
      "threshold": 10,
      "over": 5
    }
  ]
}
```

## Test Coverage vs Complexity

```bash
doc myproject --complexity --coverage
```

Output:
```json
{
  "elements": [
    {
      "path": "mypackage.simple_func",
      "complexity": 3,
      "coverage": 100,
      "status": "good"
    },
    {
      "path": "mypackage.complex_func",
      "complexity": 18,
      "coverage": 45,
      "status": "warning",
      "recommendation": "High complexity with low coverage"
    }
  ]
}
```

## Maintainability Index

```bash
doc mymodule.process --complexity --maintainability
```

Output:
```json
{
  "maintainability_index": 65,
  "interpretation": "moderate",
  "factors": {
    "cyclomatic": "good (8)",
    "loc": "moderate (150)",
    "comment_ratio": "good (25%)",
    "parameter_count": "moderate (5)"
  },
  "recommendation": "Consider reducing function length and adding more documentation"
}
```

Scale:
- 85-100: Highly maintainable
- 65-85: Moderately maintainable
- 0-65: Difficult to maintain

## Complexity Reduction Suggestions

```bash
doc mymodule.complex_func --complexity --suggestions
```

Output:
```json
{
  "complexity": 18,
  "suggestions": [
    {
      "issue": "High nesting depth (4)",
      "suggestion": "Extract nested conditions into separate functions",
      "potential_reduction": "-4 complexity"
    },
    {
      "issue": "Multiple exception handlers (4)",
      "suggestion": "Group similar exceptions or use exception hierarchy",
      "potential_reduction": "-2 complexity"
    },
    {
      "issue": "Many parameters (7)",
      "suggestion": "Use dataclass or config object",
      "potential_reduction": "N/A (readability)"
    }
  ]
}
```

## Complexity Visualization

```bash
doc myproject --complexity --graph --output complexity.png
```

Generates a graph showing complexity distribution across the project.
