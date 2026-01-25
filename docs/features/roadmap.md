# Roadmap

Implementation plan for docs-cli features.

## Status Legend

- 🏗️ **Planned** - Design complete, not started
- 🚧 **In Progress** - Currently being implemented
- ✅ **Done** - Implemented and tested
- 📋 **Backlog** - Idea, not prioritized

---

## Phase 1: MVP (Minimum Viable Product)

**Goal:** Basic CLI that can query Python packages and return structured documentation.

**Status:** 🏗️ Planned

### Features

- ✅ **CLI Basics** (`doc` command)
  - Package discovery (`doc pandas`)
  - Element access (`doc pandas.DataFrame`)
  - Path resolution (`pandas.DataFrame.merge`)
  - Basic JSON output

- ✅ **Core Discovery**
  - List public elements
  - Parse `__init__.py` imports
  - Fallback to non-private symbols
  - [Discovery](./discovery.md)

- ✅ **Runtime Introspection**
  - Extract signatures with `inspect`
  - Get docstrings
  - Parse type annotations
  - [Path Resolution](./path-resolution.md)

- ✅ **Basic Output Formats**
  - JSON (default)
  - Raw (docstring only)
  - Signature only
  - [Output Formats](./output-formats.md)

**Deliverables:**
- Working CLI with `doc` command
- Can query any installed package
- Returns structured JSON output

**Success Criteria:**
- `doc pandas.DataFrame` works
- Returns signature + docstring
- JSON output is valid

---

## Phase 2: Enhanced Analysis

**Goal:** Extract more information automatically without code modifications.

**Status:** 🏗️ Planned

### Features

- 🚧 **Usage Examples Extraction**
  - Parse docstrings for examples
  - Extract doctests
  - Google/NumPy/reST style support
  - [Usage Examples](./usage-examples.md)

- 🚧 **Type Inference Summary**
  - Analyze type annotations
  - Infer from docstrings
  - Simplified type descriptions
  - [Type Inference](./type-inference.md)

- 🚧 **Relationship Analysis**
  - Inheritance hierarchy
  - Call graph (basic)
  - Import dependencies
  - [Relationships](./relationship-analysis.md)

- 📋 **Search (Basic)**
  - Search by name
  - Search in docstrings
  - Filter by type
  - [Search](./search.md)

**Deliverables:**
- Automatic extraction of examples
- Basic relationship info
- Search functionality

**Success Criteria:**
- `doc pandas.DataFrame.merge --examples` returns examples
- `doc pandas.DataFrame --relations=inheritance` works
- `doc pandas --search "merge"` finds matches

---

## Phase 3: SDK Foundation

**Goal:** Allow developers to add custom metadata to their code.

**Status:** 🏗️ Planned

### Features

- 🚧 **Generic Metadata Decorator**
  - `@metadata(**kwargs)` decorator
  - Stores arbitrary metadata
  - Non-opinionated
  - [Metadata SDK](./metadata-sdk.md)

- 📋 **@example Decorator**
  - Add usage examples
  - With expected outputs
  - With setup code
  - [@example](./sdk-example.md)

- 📋 **@param Decorator**
  - Document parameters
  - Add constraints (min, max, choices)
  - Add descriptions
  - [@param](./sdk-param.md)

- 📋 **@returns Decorator**
  - Document return types
  - Add constraints
  - Add examples
  - [@returns](./sdk-returns.md)

**Deliverables:**
- SDK package installable
- Decorators work and are queryable
- CLI returns SDK metadata

**Success Criteria:**
- Can `pip install docs-cli-sdk`
- `@metadata` stores and retrieves data
- `doc myfunc` returns SDK metadata

---

## Phase 4: Advanced SDK

**Goal:** Rich metadata for better agent understanding.

**Status:** 📋 Backlog

### Features

- 📋 **@deprecated Decorator**
  - Mark deprecations
  - Add migration info
  - Version tracking
  - [@deprecated](./sdk-deprecated.md)

- 📋 **@category Decorator**
  - Categorize elements
  - Hierarchical categories
  - [@category](./sdk-category.md)

- 📋 **@tag Decorator**
  - Flexible tagging
  - Tag-based filtering
  - [@tag](./sdk-tag.md)

- 📋 **@note Decorator**
  - Add notes (warnings, tips)
  - Contextual information
  - [@note](./sdk-note.md)

- 📋 **@when Decorator**
  - Usage contexts
  - Requirements
  - [@when](./sdk-when.md)

**Deliverables:**
- Complete SDK decorator set
- All decorators queryable
- Filter by SDK metadata

---

## Phase 5: Advanced Querying

**Goal:** Powerful search and query capabilities.

**Status:** 📋 Backlog

### Features

- 📋 **Query Language**
  - SQL-like queries
  - Complex filters
  - Aggregations
  - [Query Language](./query-language.md)

- 📋 **Search (Advanced)**
  - Semantic search
  - Fuzzy matching
  - Full-text search
  - [Search](./search.md)

- 📋 **Deprecation Tracking**
  - Version info
  - Compatibility checks
  - Migration guides
  - [Deprecation](./deprecation.md)

- 📋 **Complexity Analysis**
  - Cyclomatic complexity
  - Metrics
  - [Complexity](./complexity-analysis.md)

**Deliverables:**
- Query language parser
- Advanced search
- Deprecation database

---

## Phase 6: Performance & Scalability

**Goal:** Handle large packages efficiently.

**Status:** 📋 Backlog

### Features

- 📋 **Documentation Index**
  - Pre-computed indexes
  - Instant queries
  - Incremental updates
  - [Doc Index](./doc-index.md)

- 📋 **Caching**
  - Query result cache
  - LRU cache
  - Persistent cache

- 📋 **Streaming**
  - NDJSON output
  - Large result handling
  - Pagination

**Deliverables:**
- Index building tools
- 100x faster queries with index
- Memory-efficient streaming

---

## Phase 7: Agent Integration

**Goal:** Deep integration with AI agent workflows.

**Status:** 📋 Backlog

### Features

- 📋 **Agent Hooks**
  - Query callbacks
  - Error handlers
  - Custom behavior
  - [Agent Hooks](./agent-hooks.md)

- 📋 **Execution Tracing**
  - Runtime tracing
  - Performance profiling
  - Call graphs
  - [Execution Tracing](./execution-tracing.md)

- 📋 **Semantic Similarity**
  - Find similar functions
  - Alternative detection
  - [Similarity](./semantic-similarity.md)

- 📋 **Source Diff**
  - Version comparison
  - Change detection
  - [Diff](./diff.md)

**Deliverables:**
- Hook system
- Tracing tools
- Diff capabilities

---

## Phase 8: Developer Tools

**Goal:** Tools for maintaining documentation quality.

**Status:** 📋 Backlog

### Features

- 📋 **Documentation Templates**
  - Generate templates
  - Scaffolding
  - Auto-fill from code
  - [Templates](./doc-templates.md)

- 📋 **Documentation Linter**
  - Completeness checks
  - Accuracy validation
  - Style checks
  - [Linter](./doc-lint.md)

- 📋 **Example Validator**
  - Run examples
  - Verify correctness
  - Auto-fix issues

**Deliverables:**
- Template generator
- Linter with rules
- Example runner

---

## Priority Matrix

### High Priority (MVP + Phase 2)

| Feature | Phase | Impact | Effort |
|---------|-------|--------|--------|
| CLI Basics | 1 | Critical | Medium |
| Core Discovery | 1 | Critical | Medium |
| Runtime Introspection | 1 | Critical | Low |
| Examples Extraction | 2 | High | Medium |
| Type Inference | 2 | High | Medium |
| Relationships | 2 | High | High |

### Medium Priority (Phase 3-4)

| Feature | Phase | Impact | Effort |
|---------|-------|--------|--------|
| SDK Foundation | 3 | High | Medium |
| @example | 3 | Medium | Low |
| @param | 3 | Medium | Low |
| @returns | 3 | Medium | Low |
| @deprecated | 4 | Medium | Low |
| @category | 4 | Low | Low |
| @tag | 4 | Low | Low |

### Low Priority (Phase 5-8)

| Feature | Phase | Impact | Effort |
|---------|-------|--------|--------|
| Query Language | 5 | Medium | High |
| Doc Index | 6 | High | High |
| Agent Hooks | 7 | Medium | Medium |
| Templates | 8 | Low | Medium |
| Linter | 8 | Low | Medium |

---

## Dependencies

```
Phase 1 (MVP)
    ↓
Phase 2 (Analysis)
    ↓
Phase 3 (SDK Foundation)
    ↓
Phase 4 (Advanced SDK)
    ↓
Phase 5 (Query) ← Phase 6 (Index) ← Phase 7 (Hooks)
    ↓
Phase 8 (Tools)
```

### Critical Dependencies

- **Query Language** requires **Doc Index** for performance
- **Agent Hooks** require **SDK Foundation**
- **Templates** benefit from **Linter**
- **Semantic Similarity** benefits from **Relationship Analysis**

---

## Timeline Estimate

| Phase | Duration | Start | End |
|-------|----------|-------|-----|
| Phase 1: MVP | 4 weeks | - | - |
| Phase 2: Enhanced Analysis | 3 weeks | - | - |
| Phase 3: SDK Foundation | 2 weeks | - | - |
| Phase 4: Advanced SDK | 2 weeks | - | - |
| Phase 5: Query | 3 weeks | - | - |
| Phase 6: Performance | 2 weeks | - | - |
| Phase 7: Agent Integration | 3 weeks | - | - |
| Phase 8: Tools | 2 weeks | - | - |
| **Total** | **21 weeks** | | |

**Note:** Timelines are estimates. Actual duration may vary.

---

## Current Status

### Completed ✅
- Documentation complete for all 25+ features
- Architecture design
- Feature specifications

### In Progress 🚧
- None (planning stage)

### Next Steps 🏗️
1. Implement Phase 1 (MVP)
2. Test with real packages (pandas, numpy)
3. Gather feedback
4. Iterate on Phase 2

---

## Contributing

Want to help? See priority matrix above.

**Good first issues:**
- Phase 1: CLI argument parsing
- Phase 1: Basic `inspect` integration
- Phase 2: Docstring parsing (Google style)

**Experienced contributors:**
- Phase 3: SDK decorator implementation
- Phase 5: Query language parser
- Phase 6: Index building and optimization

---

## Feedback & Questions

- See [Getting Started](./getting-started.md) for usage examples
- Check individual feature docs for details
- [Features Index](./index.md) for complete list
