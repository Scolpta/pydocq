# docs-cli

> **⚠️ Work in Progress**

A CLI tool that provides structured metadata about Python packages, designed specifically for AI agents to consume.

## Status

**Planning Stage** - This project is currently in the design and planning phase. See [docs/PROJECT.md](docs/PROJECT.md) for the project overview and [docs/features/roadmap.md](docs/features/roadmap.md) for the implementation plan.

## Documentation

### Internal Documentation

For contributors and developers:

- **[PROJECT.md](docs/PROJECT.md)** - Project goals, architecture, and design principles
- **[Features](docs/features/)** - Detailed feature specifications
  - [Getting Started](docs/features/getting-started.md) - Agent workflows and usage examples
  - [Roadmap](docs/features/roadmap.md) - Implementation phases and priorities
  - [Feature Index](docs/features/index.md) - Complete list of planned features

### Quick Overview

docs-cli extracts structured, machine-readable documentation from Python packages:

```bash
# Query package structure
doc pandas

# Get specific element details
doc pandas.DataFrame.merge

# Get structured output (JSON)
doc pandas.DataFrame --format json

# Extract examples
doc pandas.DataFrame.groupby --examples
```

**Output is optimized for AI agents, not humans:**
- Structured JSON (not text)
- Type information
- Relationships between elements
- Usage examples
- Semantic metadata

## Vision

Traditional documentation tools are designed for human reading. docs-cli is different:

| Traditional Tools | docs-cli |
|------------------|----------|
| Human-readable text | Machine-readable JSON |
- HTML docs | Structured metadata |
| Tutorials + reference | Signatures + types + relationships |
| For developers | For AI agents |

**Target users:** AI agents that need to understand Python code without reading source files.

## Example Use Case

```python
# Agent receives: "How do I load and filter CSV data in pandas?"

# Instead of reading source code:
1. doc pandas --search "CSV"
2. doc pandas.read_csv --examples
3. doc pandas.DataFrame --query "where param:DataFrame and returns:DataFrame"
4. doc pandas.DataFrame.filter --type-summary

# Agent gets structured information → generates working code
```

## Current State

- ✅ Complete feature specification (25+ features)
- ✅ Architecture design
- ✅ Implementation roadmap
- 🏗️ **Planning phase** - No code written yet

See [docs/features/roadmap.md](docs/features/roadmap.md) for the implementation plan.

## Contributing

Not ready for contributions yet. We're still in the planning phase.

Once implementation starts:
1. Check [Roadmap](docs/features/roadmap.md) for priorities
2. Review [Features](docs/features/) for specifications
3. Pick a feature from the backlog

## License

[Specify your license here]
