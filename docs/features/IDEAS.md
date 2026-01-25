# Feature Ideas - Accepted for Implementation

This document tracks feature ideas that have been evaluated and **accepted** for implementation in pydocq. These features are deemed technically feasible and aligned with the project's goal of providing the best documentation tool for AI agents.

## Evaluation Criteria

Features are accepted based on:

1. **Technical Feasibility** - Can be implemented with reasonable effort
2. **AI Agent Value** - Provides clear value to AI agents consuming the output
3. **Differentiation** - Sets pydocq apart from standard documentation tools
4. **Dependencies** - Doesn't require heavy external dependencies or complex infrastructure
5. **Maintenance** - Sustainable to maintain long-term

---

## Priority 1: Quick Wins (High Impact, Low Complexity)

### 1.1 Expose AST File Analysis to CLI

**Status:** Implementation exists, not exposed to CLI

**Description:**
The `ast_analyzer.py` module already provides static file analysis without importing code. This needs to be exposed through the CLI interface.

**Proposed CLI:**
```bash
pydocq --analyze-file ./path/to/file.py
pydocq --analyze-file ./src/utils.py MyClass
pydocq --analyze-file ./src/utils.py my_function
```

**Value for AI Agents:**
- Analyze code without executing it (security)
- Work with code that has missing dependencies
- Explore repositories without installation
- Safe analysis of untrusted code

**Technical Implementation:**
- ~50 lines of code in `cli.py`
- Reuses existing `analyze_file()` function
- Add file path validation (security)
- Output format consistent with regular queries

**Effort Estimate:** 2-4 hours

**Acceptance Rationale:**
- Code already exists in `ast_analyzer.py:315`
- Zero external dependencies
- High security value (no code execution)
- Addresses "analyze without importing" use case

---

### 1.2 LLM-Optimized Output Format

**Status:** New feature, high priority

**Description:**
Dedicated output format optimized for LLM token efficiency while preserving critical information.

**Proposed CLI:**
```bash
pydocq json.dump --llm-format
```

**Proposed Output:**
```json
{
  "path": "json.dump",
  "summary": "Serialize Python object to JSON file",
  "key_params": ["obj", "fp"],
  "common_usage": "Save data to JSON file",
  "example_concise": "json.dump(data, open('file.json', 'w'))",
  "common_pitfalls": [
    "fp must have .write() method",
    "obj must be JSON-serializable"
  ],
  "alternatives": [
    {"path": "json.dumps", "reason": "Returns string instead of writing to file"},
    {"path": "pickle.dump", "reason": "For Python-specific objects"}
  ],
  "token_count": 45
}
```

**Value for AI Agents:**
- 70-90% reduction in token usage vs full JSON
- Focus on information needed for code generation
- Faster context processing
- Reduced API costs for users

**Technical Implementation:**
- New formatter in `output_formats.py`
- Intelligent summarization logic (docstring → 1 sentence)
- Extract most common parameter combinations
- Identify critical warnings/errors
- Token count estimation

**Effort Estimate:** 4-6 hours

**Acceptance Rationale:**
- Core value proposition for AI agents
- No external dependencies
- Immediate user value
- Differentiates from standard doc tools
- Relatively simple implementation

---

### 1.3 Combined `--for-ai` Flag

**Status:** New feature, composites existing features

**Description:**
Convenience flag that combines all AI-optimizations into one command.

**Proposed CLI:**
```bash
pydocq pandas.DataFrame.merge --for-ai
```

**Equivalent to:**
```bash
pydocq pandas.DataFrame.merge \
  --llm-format \
  --include-metadata \
  --include-source \
  --examples \
  --warnings
```

**Value for AI Agents:**
- One command to get everything needed
- Consistent agent behavior
- Less CLI complexity for agent developers

**Technical Implementation:**
- Add `--for-ai` boolean flag in `cli.py`
- Enable all AI-relevant options when flag is set
- Ensure output format is optimized

**Effort Estimate:** 1-2 hours

**Acceptance Rationale:**
- UX improvement for agent developers
- Zero technical risk (composes existing features)
- Marketing value ("one command for AI agents")

---

## Priority 2: Strategic Features (Medium Effort, High Value)

### 2.1 Usage Examples from Test Files

**Status:** Partial (SDK decorators exist), needs automation

**Description:**
Automatically extract real usage examples from test files and documentation.

**Proposed CLI:**
```bash
pydocq json.dump --examples-from tests/
pydocq pandas.DataFrame.merge --examples-from docs/
```

**Proposed Output:**
```json
{
  "path": "json.dump",
  "examples": [
    {
      "source": "tests/test_json.py:42",
      "code": "json.dump({'key': 'value'}, open('out.json', 'w'))",
      "context": "basic serialization test"
    },
    {
      "source": "docs/examples.md",
      "code": "with open('data.json', 'w') as f:\n    json.dump(data, f, indent=2)",
      "context": "pretty-printed output"
    }
  ]
}
```

**Value for AI Agents:**
- Real usage patterns vs theoretical docstrings
- Edge case handling from tests
- Multiple perspectives on usage
- Docstrings can be outdated, tests show truth

**Technical Implementation:**
- **Phase 1 (Simple):** Grep-based extraction
  - Search for function calls in test files
  - Extract surrounding context
  - No dependency on test frameworks

- **Phase 2 (Advanced):** AST-based extraction
  - Parse test files with AST
  - Identify function calls with arguments
  - Extract assertion patterns
  - Better context understanding

**Effort Estimate:**
- Phase 1: 8-12 hours
- Phase 2: 16-24 hours

**Acceptance Rationale:**
- High differentiation factor
- Addresses "docstrings lie" problem
- Can be implemented incrementally
- Phase 1 is low-risk, high-value

**Dependencies:** None for Phase 1 (grep/file reading)

---

### 2.2 Version Diff / Change Detection

**Status:** Documented in `diff.md`, needs implementation

**Description:**
Compare API elements across versions to detect breaking changes and additions.

**Proposed CLI:**
```bash
pydocq pandas.DataFrame.merge --diff v1.5.0..v2.0.0
pydocq pandas.DataFrame.merge --diff HEAD~5
```

**Value for AI Agents:**
- Migration assistance
- Breaking change detection
- Deprecation warnings
- API evolution understanding

**Technical Implementation:**
- Use git to fetch different versions
- Run inspection on both versions
- Compare signatures, docstrings, parameters
- Categorize changes (breaking, additive, doc-only)

**Phased Approach:**
1. Git commit comparison (simpler)
2. Version tag comparison
3. PyPI package version comparison

**Effort Estimate:**
- Phase 1: 12-16 hours
- Full feature: 24-32 hours

**Acceptance Rationale:**
- Already documented and designed
- Strategic value for enterprise users
- Enables migration workflows
- Documentation exists, just needs implementation

---

## Priority 3: Advanced Features (Higher Effort, Specialized Value)

### 3.1 Semantic Search (Vector-Based)

**Status:** Documented in `semantic-similarity.md`, research phase

**Description:**
Find functions by semantic intent rather than exact name matching.

**Proposed CLI:**
```bash
pydocq pandas --search-semantic "filter rows by condition"
pydocq --similar "function to write CSV" pandas
```

**Value for AI Agents:**
- Discover functions when name is unknown
- Find alternatives by intent
- Natural language queries
- "I know what I want to do, not what it's called"

**Technical Challenges:**
- Requires embedding model (sentence-transformers)
- Indexing infrastructure
- Vector similarity search
- Model storage and distribution

**Proposed Implementation:**
- **Option 1 (Full):** Local embedding models
  - Dependencies: sentence-transformers, numpy
  - ~100MB download for models
  - High quality results

- **Option 2 (Hybrid):** TF-IDF + keyword matching
  - Dependencies: scikit-learn or just collections.Counter
  - No model download
  - Lower quality but simpler

- **Option 3 (Remote API):** Optional cloud embeddings
  - OpenAI/Cohere embeddings API
  - Requires API key from user
  - Best quality, requires internet

**Effort Estimate:**
- Option 2 (Hybrid): 16-24 hours
- Option 1 (Full): 32-48 hours
- Option 3 (Remote): 24-32 hours

**Acceptance Rationale:**
- High value for agents
- Can be implemented incrementally
- Start with Option 2 (low complexity)
- Add Option 1/3 as opt-in features
- Already documented in project

**Status:** **ACCEPTED for Phase 2 implementation (Option 2 first)**

---

### 3.2 Dependency Graphs / Call Graphs

**Status:** Concept phase

**Description:**
Visualize and query relationships between code elements.

**Proposed CLI:**
```bash
pydocq pandas.DataFrame.merge --call-graph
pydocq mymodule.process --depends-on
pydocq mymodule.process --used-by
```

**Value for AI Agents:**
- Understand architecture
- Identify side effects
- Refactoring assistance
- Impact analysis

**Technical Challenges:**
- Requires full codebase indexing
- Complex AST analysis
- Graph representation
- Large outputs for big projects

**Simplified Approach:**
- Start with direct dependencies only (1 level)
- Use existing AST analyzer
- Output as JSON, not visualization
- User can visualize with external tools

**Effort Estimate:**
- Direct dependencies (1 level): 16-20 hours
- Full call graph: 40+ hours

**Acceptance Rationale:**
- Valuable but specialized use case
- Start simple (direct deps only)
- Lower priority than core features
- Can be extended over time

**Status:** **ACCEPTED for future consideration, not immediate implementation**

---

## Priority 4: Future Considerations (Accepted but Deferred)

### 4.1 Interactive Mode

**Description:**
REPL-like interface for exploratory documentation queries.

**Rationale:** Useful for human users, but AI agents prefer programmatic interface.

**Status:** Accepted, but low priority. Core focus is AI agent consumption, not human UX.

---

### 4.2 Documentation Index Caching

**Description:**
Pre-build and cache documentation indexes for instant queries.

**Rationale:** Performance optimization, but premature before core features are complete.

**Status:** Accepted for Phase 3 (after core features are stable).

---

### 4.3 Cross-Package Semantic Search

**Description:**
Find similar functions across different packages (e.g., "pandas.DataFrame vs polars.DataFrame").

**Rationale:** High value but requires semantic search to be implemented first.

**Status:** Accepted, depends on Priority 3.1 (Semantic Search).

---

## Features NOT Accepted

### Rejected Ideas (out of scope)

1. **Code execution sandbox** - Security risk, out of scope
2. **Performance profiling** - Better tools exist (cProfile, py-spy)
3. **Code generation** - Agents do this, not the documentation tool
4. **Type checking** - mypy already exists
5. **Linting** - Tools like ruff, pylint exist

---

## Implementation Roadmap

### Phase 1: Foundation (Current → v0.3.0)
- [ ] Expose AST file analysis to CLI
- [ ] Implement `--llm-format` output
- [ ] Add `--for-ai` convenience flag
- [ ] Update tests and documentation

### Phase 2: Core Enhancements (v0.4.0 → v0.5.0)
- [ ] Usage examples from test files (Phase 1: grep-based)
- [ ] Simple semantic search (TF-IDF based)
- [ ] Enhanced search with filters

### Phase 3: Advanced Features (v0.6.0+)
- [ ] Version diff / change detection
- [ ] Advanced semantic search (embedding models)
- [ ] Dependency graphs (direct relationships)

### Phase 4: Optimization (v1.0.0 preparation)
- [ ] Documentation caching
- [ ] Performance profiling
- [ ] API stability guarantees

---

## Contributing Ideas

New feature ideas should be proposed through GitHub issues with:

1. Clear description of the problem it solves
2. Proposed CLI interface
3. Proposed output format
4. Technical feasibility assessment
5. Value proposition for AI agents

Each idea will be evaluated against the criteria above and added to this document if accepted.

---

## Changelog

### 2025-01-25
- Created IDEAS.md
- Accepted AST file analysis CLI exposure (Priority 1.1)
- Accepted LLM-optimized output format (Priority 1.2)
- Accepted `--for-ai` convenience flag (Priority 1.3)
- Accepted test file example extraction (Priority 2.1)
- Accepted version diff implementation (Priority 2.2)
- Accepted semantic search with phased approach (Priority 3.1)
- Accepted dependency graphs for future (Priority 3.2)
- Deferred interactive mode, caching, cross-package search (Priority 4)
