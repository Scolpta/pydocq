# docs-cli

> **⚠️ Internal Documentation**
>
> This is internal documentation for the docs-cli project development. It describes the design, architecture, and planned features for contributors.
>
> For end-user documentation, see [README.md](../README.md) (when available).

## Goal

A CLI tool that provides structured metadata about Python packages, designed specifically for AI agents to consume.

## Problem

When AI agents need to understand Python code, they typically rely on:
- Reading source files directly (`Read`, `grep`) → noisy, includes implementation details
- Extracting docstrings → inconsistent format, missing semantic context
- Installing and importing packages → heavy, not always possible

This results in:
- High token usage (parsing entire source files)
- Loss of semantic information (intent, relationships, constraints)
- Inconsistent metadata across packages

## Solution

A CLI that outputs **structured, agent-consumable metadata** about Python code elements:

```bash
doc pandas DataFrame
# → JSON with signature, docstring, members, semantics, etc.

doc pandas.core.frame.DataFrame.__init__
# → Structured info about specific method
```

## Design Principles

### Agent-first
- Primary output format: JSON (structured, parseable)
- Include semantic metadata, not just syntax
- Machine-readable over human-readable

### Non-opinionated SDK
- Generic decorator for storing metadata
- No prescribed schema for custom metadata
- Users define what "semantic" means for their project

### Automatic extraction
- Works on any Python package without modification
- Extract as much as possible automatically:
  - Signatures (with type annotations)
  - Docstrings
  - Class/module members
  - Source location
  - Decorators

### No abuse
- Avoid fragile analysis (dataflow, type inference without annotations)
- Don't try to understand behavior from function bodies
- Keep it reliable and fast

## Use Cases

```python
# AI agent workflow
1. Query: "What DataFrame methods handle missing values?"
2. CLI: doc pandas.DataFrame --filter "docstring contains 'na'"
3. Agent receives structured list with signatures → can reason about usage
```

## Architecture

```
docs-cli/
├── cli.py          # Typer CLI interface
├── analyzer/       # Automatic code analysis
│   ├── inspector.py    # Runtime introspection (inspect)
│   ├── parser.py       # Static analysis (ast)
│   └── resolver.py     # Path resolution
├── formatter/      # Output formats
│   ├── json.py
│   └── schema.py
└── sdk/            # Optional metadata decorators
    └── decorators.py
```

## Example Output

```json
{
  "path": "pandas.DataFrame",
  "type": "class",
  "docstring": "Two-dimensional, size-mutable, potentially heterogeneous tabular data.",
  "source_location": {
    "file": "pandas/core/frame.py",
    "line": 123
  },
  "members": [
    {"name": "__init__", "type": "method", "signature": {...}},
    {"name": "groupby", "type": "method", "signature": {...}}
  ],
  "metadata": {}  // Optional SDK metadata
}
```

## Roadmap

1. CLI + path resolution
2. Runtime introspection (inspect)
3. JSON formatter
4. Static analysis (AST) for members
5. SDK generic decorator
