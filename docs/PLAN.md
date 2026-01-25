# Implementation Plan

Step-by-step implementation plan for docs-cli.

> This is a living document. Update as we progress.

## Project Structure

```
docs-cli/
├── docs_cli/
│   ├── __init__.py
│   ├── cli.py              # Typer CLI
│   ├── commands/           # CLI command handlers
│   ├── analyzer/           # Code analysis
│   │   ├── inspector.py    # Runtime introspection
│   │   ├── parser.py       # AST parsing
│   │   └── resolver.py     # Path resolution
│   ├── formatter/          # Output formatters
│   │   ├── json.py
│   │   ├── raw.py
│   │   └── signature.py
│   ├── sdk/                # SDK decorators
│   │   └── decorators.py
│   └── utils/              # Utilities
├── tests/
│   ├── test_cli.py
│   ├── test_analyzer.py
│   └── fixtures/           # Test Python packages
├── pyproject.toml
└── main.py
```

---

## Phase 1: MVP (Week 1-4)

### Week 1: Project Setup & CLI Skeleton

**Goal:** Working CLI with basic structure

#### Tasks

- [ ] **Day 1-2: Project Structure**
  - [ ] Create directory structure
  - [ ] Setup `pyproject.toml` with dependencies (typer, rich)
  - [ ] Create `docs_cli/__init__.py`
  - [ ] Create `cli.py` with typer app
  - [ ] Basic `doc` command that prints "Hello"

```bash
# Expected result
$ doc
Hello from docs-cli!
```

- [ ] **Day 3-4: Path Resolution**
  - [ ] Create `analyzer/resolver.py`
  - [ ] Implement `resolve_path(path_string)` function
  - [ ] Handle: `package`, `package.module`, `package.module.Class`
  - [ ] Add error handling for not found
  - [ ] Write tests for resolution

```bash
# Expected result
$ doc pandas.DataFrame
Resolved: pandas.core.frame.DataFrame
```

- [ ] **Day 5: Basic Import Integration**
  - [ ] Use `importlib` to import modules
  - [ ] Use `getattr` to navigate to elements
  - [ ] Return actual Python objects
  - [ ] Error handling for import errors

**Validation:** Can resolve paths like `pandas.DataFrame` to actual class object

---

### Week 2: Runtime Introspection

**Goal:** Extract basic info from Python objects

#### Tasks

- [ ] **Day 1-2: Inspector**
  - [ ] Create `analyzer/inspector.py`
  - [ ] Implement `get_signature(obj)` using `inspect.signature()`
  - [ ] Implement `get_docstring(obj)` using `inspect.getdoc()`
  - [ ] Implement `get_source_location(obj)` using `inspect.getsourcefile()`
  - [ ] Handle functions, classes, methods

- [ ] **Day 3-4: Type Annotation Parsing**
  - [ ] Parse type annotations from signature
  - [ ] Handle `list[int]`, `dict[str, int]`, unions
  - [ ] Get default values
  - [ ] Format as structured dict

```python
# Expected output format
{
  "name": "merge",
  "parameters": [
    {"name": "right", "type": "DataFrame", "default": null}
  ],
  "return_type": "DataFrame"
}
```

- [ ] **Day 5: JSON Formatter**
  - [ ] Create `formatter/json.py`
  - [ ] Implement `format_json(obj)` function
  - [ ] Combine signature + docstring + location
  - [ ] Output valid JSON

```bash
# Expected result
$ doc pandas.DataFrame.merge
{
  "path": "pandas.DataFrame.merge",
  "type": "method",
  "docstring": "Merge DataFrame...",
  "signature": {...},
  "source_location": {...}
}
```

**Validation:** `doc pandas.DataFrame.merge` returns complete JSON

---

### Week 3: Discovery & Output Formats

**Goal:** List package contents, add output format options

#### Tasks

- [ ] **Day 1-2: Discovery**
  - [ ] Implement `discover(package)` function
  - [ ] Check `__all__` first
  - [ ] Parse `__init__.py` imports
  - [ ] Fallback to filtering `__` prefix
  - [ ] Return list of public members

```bash
# Expected result
$ doc pandas
{
  "members": [
    {"name": "DataFrame", "type": "class", "path": "pandas.DataFrame"},
    {"name": "Series", "type": "class", "path": "pandas.Series"}
  ]
}
```

- [ ] **Day 3: Raw Output Format**
  - [ ] Create `formatter/raw.py`
  - [ ] `--format raw` returns docstring only
  - [ ] No JSON wrapping

- [ ] **Day 4: Signature Output Format**
  - [ ] Create `formatter/signature.py`
  - [ ] `--format signature` returns type signature only
  - [ ] Format: `func(param: type, ...) -> return_type`

- [ ] **Day 5: CLI Integration**
  - [ ] Add `--format` option to CLI
  - [ ] Add `--include-source` option
  - [ ] Add `--include-private` flag
  - [ ] Error handling and validation

**Validation:** All output formats work, discovery works

---

### Week 4: Testing & Refinement

**Goal:** Solid MVP, tests pass, ready for real use

#### Tasks

- [ ] **Day 1-2: Test Suite**
  - [ ] Create test fixtures (simple Python package)
  - [ ] Test path resolution
  - [ ] Test introspection (functions, classes, methods)
  - [ ] Test discovery
  - [ ] Test output formats
  - [ ] Integration tests

- [ ] **Day 3: Real Package Testing**
  - [ ] Test with `pandas`
  - [ ] Test with `numpy`
  - [ ] Test with standard library
  - [ ] Fix edge cases

- [ ] **Day 4: Error Handling**
  - [ ] Package not installed
  - [ ] Element not found
  - [ ] Invalid syntax
  - [ ] Graceful error messages

- [ ] **Day 5: Documentation & Polish**
  - [ ] Update README with usage examples
  - [ ] Add `--help` documentation
  - [ ] Performance optimization
  - [ ] Code cleanup

**Validation:** MVP complete, tested, documented

---

## Phase 2: Enhanced Analysis (Week 5-7)

### Week 5: Examples Extraction

**Tasks:**

- [ ] **Day 1-2: Docstring Parsing**
  - [ ] Create `analyzer/parser.py`
  - [ ] Parse Google style docstrings
  - [ ] Parse NumPy style docstrings
  - [ ] Parse reST style docstrings
  - [ ] Extract Examples sections

- [ ] **Day 3-4: Doctest Extraction**
  - [ ] Parse `>>>` prompts
  - [ ] Extract code and output
  - [ ] Handle exceptions in doctests
  - [ ] Format as structured list

- [ ] **Day 5: CLI Integration**
  - [ ] Add `--examples` flag
  - [ ] Return extracted examples
  - [ ] Filter by examples with/without output

**Validation:** `doc pandas.DataFrame.merge --examples` returns examples

---

### Week 6: Type Inference & Relationships

**Tasks:**

- [ ] **Day 1-2: Type Inference**
  - [ ] Analyze type annotations
  - [ ] Infer from docstring types
  - [ ] Create simplified type descriptions
  - [ ] Handle unions, optionals, generics

- [ ] **Day 3-4: Relationship Analysis**
  - [ ] Extract inheritance (`__bases__`, `__mro__`)
  - [ ] Find subclasses via `__subclasses__()`
  - [ ] Basic call graph (AST, direct calls only)
  - [ ] Import dependencies from AST

- [ ] **Day 5: CLI Integration**
  - [ ] `--type-summary` flag
  - [ ] `--relations` flag (inheritance, calls)
  - [ ] JSON output for relationships

**Validation:** Type inference works, relationships extracted

---

### Week 7: Search Functionality

**Tasks:**

- [ ] **Day 1-2: Basic Search**
  - [ ] Search by element name
  - [ ] Search in docstrings
  - [ ] Filter by type (class, function, method)
  - [ ] Relevance scoring

- [ ] **Day 3-4: Search Filters**
  - [ ] `--filter "type:class"`
  - [ ] `--filter "docstring:keyword"`
  - [ ] `--filter "decorator:name"`
  - [ ] Combine multiple filters

- [ ] **Day 5: CLI Integration**
  - [ ] `--search` command
  - [ ] JSON results with relevance scores
  - [ ] Performance optimization

**Validation:** Search finds relevant elements

---

## Phase 3: SDK Foundation (Week 8-9)

### Week 8: SDK Package

**Tasks:**

- [ ] **Day 1-2: SDK Structure**
  - [ ] Create `docs_cli_sdk/` package
  - [ ] Create `sdk/__init__.py` in main package
  - [ ] Setup installation in `pyproject.toml`

- [ ] **Day 3-4: @metadata Decorator**
  - [ ] Implement `@metadata(**kwargs)`
  - [ ] Store in `__doc_metadata__`
  - [ ] CLI retrieves and includes in output
  - [ ] Tests

- [ ] **Day 5: SDK Integration**
  - [ ] CLI detects SDK metadata
  - [ ] Includes in JSON output
  - [ ] Filter by metadata

**Validation:** `@metadata` works, queryable via CLI

---

### Week 9: Specific Decorators

**Tasks:**

- [ ] **Day 1: @example**
  - [ ] Implement `@example(code, ...)`
  - [ ] Store examples
  - [ ] CLI `--examples` includes SDK examples

- [ ] **Day 2: @param**
  - [ ] Implement `@param()` decorator
  - [ ] Document parameters with constraints
  - [ ] CLI includes param metadata

- [ ] **Day 3: @returns**
  - [ ] Implement `@returns()` decorator
  - [ ] Document return values
  - [ ] CLI includes return metadata

- [ ] **Day 4-5: Testing & Polish**
  - [ ] Test all decorators
  - [ ] Documentation
  - [ ] Integration tests

**Validation:** All 3 decorators work

---

## Phase 4-8: Future Phases

Detailed task breakdown will be created when approaching these phases.

### Phase 4: Advanced SDK
- @deprecated, @category, @tag, @note, @when

### Phase 5: Advanced Querying
- Query language parser
- Semantic search
- Deprecation tracking
- Complexity analysis

### Phase 6: Performance
- Index building
- Caching layer
- Streaming output

### Phase 7: Agent Integration
- Hook system
- Execution tracing
- Semantic similarity
- Version diff

### Phase 8: Developer Tools
- Template generator
- Linter
- Example validator

---

## Daily Workflow

### Development

1. Pull latest changes
2. Checkout task branch
3. Implement feature
4. Write tests
5. Run tests
6. Create PR

### Commit Convention

```
feat: add basic path resolution
fix: handle import errors gracefully
test: add tests for discovery
docs: update CLI usage
refactor: simplify formatter logic
```

### Testing

```bash
# Run all tests
pytest

# Run specific test
pytest tests/test_resolver.py

# Run with coverage
pytest --cov=docs_cli

# Test on real package
doc pandas.DataFrame
```

---

## Definition of Done

Each phase is complete when:

- ✅ All tasks implemented
- ✅ Tests pass (>80% coverage)
- ✅ Documentation updated
- ✅ Tested on real packages (pandas, numpy)
- ✅ No critical bugs
- ✅ Code reviewed

---

## Risk Mitigation

### Technical Risks

| Risk | Mitigation |
|------|------------|
| AST parsing complexity | Start with simple cases, expand gradually |
| Performance on large packages | Add indexing in Phase 6 |
| Type inference accuracy | Use docstrings as fallback |

### Timeline Risks

| Risk | Mitigation |
|------|------------|
| Underestimated complexity | Buffer time in each phase |
| Blocked by dependency | Have parallel tasks ready |
| Testing takes longer | Test continuously, not at end |

---

## Dependencies

### Required Python Version
- Python 3.14+

### Required Packages
```
typer>=0.12.0
rich>=13.0.0
```

### Optional (Future)
- `griffe` for better AST parsing
- `numpy` for testing
- `pandas` for testing

---

## Success Metrics

### Phase 1 (MVP)
- [ ] `doc pandas.DataFrame` works
- [ ] Returns valid JSON
- [ ] <500ms response time
- [ ] No crashes on stdlib packages

### Phase 2
- [ ] Examples extraction >90% accuracy
- [ ] Relationships correctly identified
- [ ] Search returns relevant results

### Overall
- [ ] Can replace `help()` for agents
- [ ] Faster than reading source files
- [ ] More structured than docstrings

---

## Next Actions

1. ✅ **DONE:** Complete planning
2. **NOW:** Start Phase 1, Week 1
3. Create project structure
4. Implement basic CLI
5. Test path resolution

---

## Notes

- This is a flexible plan - adjust based on reality
- Focus on MVP first, enhancements later
- Keep tests passing
- Document as you go
- Get feedback early and often

**Last Updated:** 2025-01-25
