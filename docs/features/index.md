# Features

> **⚠️ Internal Documentation**
>
> This documentation describes the design and planned features of docs-cli for internal development purposes.
>
> - For project overview, see [PROJECT.md](../PROJECT.md)
> - For implementation roadmap, see [Roadmap](./roadmap.md)
> - For usage examples, see [Getting Started](./getting-started.md)

Overview of docs-cli functionality.

## Quick Start

New to docs-cli? Start with:
- **[Getting Started](./getting-started.md)** - Learn the basics with agent workflows
- **[Roadmap](./roadmap.md)** - Implementation phases and priorities
- **[Configuration Example](./config-example.md)** - Example configuration file

## Core Features

**Essential functionality** - Start here for basic usage:

- **[Discovery](./discovery.md)** - Listing package contents
- **[Path Resolution](./path-resolution.md)** - Resolving package paths to elements
- **[Output Formats](./output-formats.md)** - Structured data formats (JSON, schema, raw)
- **[Metadata SDK](./metadata-sdk.md)** - Custom metadata via generic decorator

## Analysis Features

**Extract information automatically** from code without modifications:

- **[Relationship Analysis](./relationship-analysis.md)** - Inheritance, calls, dependencies
- **[Usage Examples Extraction](./usage-examples.md)** - Extract examples from docstrings
- **[Type Inference Summary](./type-inference.md)** - Type information optimized for agents
- **[Search](./search.md)** - Search across packages by criteria
- **[Deprecation Info](./deprecation.md)** - Version and deprecation tracking
- **[Complexity Analysis](./complexity-analysis.md)** - Code complexity metrics
- **[Source Diff / Change Detection](./diff.md)** - Compare versions and changes
- **[Execution Tracing](./execution-tracing.md)** - Runtime behavior tracing
- **[Semantic Similarity](./semantic-similarity.md)** - Find similar elements

## SDK Decorators

**Enhanced documentation** - Decorators to add metadata to code:

- **[@example](./sdk-example.md)** - Add usage examples
- **[@deprecated](./sdk-deprecated.md)** - Mark as deprecated with migration info
- **[@param](./sdk-param.md)** - Document parameters with constraints
- **[@category](./sdk-category.md)** - Categorize elements
- **[@when](./sdk-when.md)** - Specify usage contexts
- **[@returns](./sdk-returns.md)** - Document return values
- **[@tag](./sdk-tag.md)** - Add flexible tags
- **[@note](./sdk-note.md)** - Add notes (warnings, tips, gotchas)

## Advanced Features

**Powerful capabilities** for complex use cases:

- **[Documentation Index](./doc-index.md)** - Pre-computed indexes for instant queries
- **[Query Language](./query-language.md)** - Powerful query language for documentation
- **[Agent Hooks](./agent-hooks.md)** - Callback system for agent events

## Developer Tools

**Tools for maintaining documentation quality**:

- **[Documentation Templates](./doc-templates.md)** - Generate documentation templates
- **[Documentation Linter](./doc-lint.md)** - Validate and check documentation quality

## Usage Examples

### Basic Queries

```bash
# List package contents
doc pandas

# Get specific element
doc pandas.DataFrame

# Get method details
doc pandas.DataFrame.groupby
```

### Structured Output

```bash
# JSON (default)
doc pandas.DataFrame

# Type signature
doc pandas.DataFrame.append --format signature

# With source code
doc pandas.DataFrame --include-source
```

### Filtering

```bash
# Classes only
doc pandas --filter "type:class"

# By docstring content
doc pandas --filter "docstring:na"

# By decorator
doc pandas --filter "decorator:cache"
```

## Quick Reference

| Feature | Command | Description |
|---------|---------|-------------|
| Discovery | `doc <package>` | List public elements |
| Element | `doc <package>.<element>` | Get element details |
| Signature | `--format signature` | Type signature only |
| Raw | `--format raw` | Docstring only |
| Schema | `--format schema` | JSON Schema |
| Source | `--include-source` | Include source code |
| Stream | `--stream` | NDJSON output |

## Architecture

```
CLI Input
    ↓
Path Resolution → Python Element
    ↓
Analyzer
    ├─ Runtime (inspect)
    ├─ Static (AST)
    └─ Metadata (SDK)
    ↓
Formatter → JSON/Schema/Raw
    ↓
Output
```
