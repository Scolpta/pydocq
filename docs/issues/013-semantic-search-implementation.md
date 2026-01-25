# Issue FEAT-006: Semantic Search Implementation

## Description

Implement semantic search functionality to find functions by intent rather than exact name matching. This feature is documented in `docs/features/semantic-similarity.md` with a phased implementation approach.

## Problem Details

### Current State

The semantic search feature is **documented but not implemented**:

- Documentation exists: `docs/features/semantic-similarity.md`
- No search implementation
- No similarity computation
- Cannot find functions by intent

### Use Cases

1. **Find functions when name is unknown**
   ```bash
   $ pydocq pandas --search-semantic "filter rows by condition"
   # Returns: query, loc, __getitem__
   ```

2. **Find alternatives**
   ```bash
   $ pydocq --similar "function to write CSV" pandas
   # Returns: to_csv, DataFrame.to_csv
   ```

3. **Discover functionality**
   ```bash
   $ pydocq pandas --search "aggregate data"
   # Returns: groupby, agg, transform
   ```

### Current Limitations

| Limitation | Impact | Severity |
|------------|--------|----------|
| **Name-Only Search** | Must know exact function name | High |
| **No Discovery** | Can't explore by intent | High |
| **No Alternatives** | Hard to find similar functions | Medium |
| **Manual Lookup** | Must read documentation | Medium |

## Recommended Phased Implementation

### Phase 1: TF-IDF Based Search (Quick Win)

**Goal:** Implement basic semantic search without external ML dependencies.

**Approach:** Use TF-IDF (Term Frequency-Inverse Document Frequency) for similarity scoring.

```python
# pydocq/analyzer/semantic_search.py

import re
import math
from collections import Counter
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class SemanticMatch:
    """A semantic search match."""
    path: str
    element_type: str
    similarity: float
    reason: str
    example: str = ""


class TFIDFSemanticSearch:
    """TF-IDF based semantic search.

    This implementation uses:
    - Term Frequency (TF): How often terms appear in a document
    - Inverse Document Frequency (IDF): How unique terms are across all documents
    - Cosine Similarity: Measure of similarity between vectors
    """

    def __init__(self):
        """Initialize the search engine."""
        self.documents: Dict[str, str] = {}  # path -> text content
        self.vocabulary: Dict[str, int] = {}  # term -> document frequency
        self.total_documents = 0

    def index_document(self, path: str, content: str) -> None:
        """Add a document to the index.

        Args:
            path: Document identifier (e.g., function path)
            content: Text content to index
        """
        self.documents[path] = content
        self.total_documents += 1

        # Update vocabulary
        terms = self._tokenize(content)
        unique_terms = set(terms)

        for term in unique_terms:
            self.vocabulary[term] = self.vocabulary.get(term, 0) + 1

    def index_module(self, module_path: str) -> None:
        """Index all elements in a module.

        Args:
            module_path: Path to module to index
        """
        from pydocq.analyzer.resolver import resolve_path
        from pydocq.analyzer.inspector import inspect_element
        from pydocq.analyzer.discovery import discover_module_members

        try:
            # Resolve module
            resolved = resolve_path(module_path)

            # Get all members
            members = discover_module_members(
                resolved.obj,
                include_private=False,
                include_imported=False
            )

            # Index each member
            for member in members.members:
                try:
                    # Inspect member
                    member_resolved = resolve_path(f"{module_path}.{member.name}")
                    inspected = inspect_element(member_resolved)

                    # Create searchable content
                    content = self._create_search_content(inspected)

                    # Index it
                    self.index_document(
                        inspected.path,
                        content
                    )

                except Exception:
                    # Skip members that can't be inspected
                    continue

        except Exception:
            pass

    def search(
        self,
        query: str,
        top_k: int = 10
    ) -> List[SemanticMatch]:
        """Search for similar documents.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of semantic matches ranked by similarity
        """
        if not self.documents:
            return []

        # Tokenize query
        query_terms = self._tokenize(query)
        query_tf = self._compute_tf(query_terms)

        # Compute similarity for each document
        results = []

        for doc_path, doc_content in self.documents.items():
            # Compute document TF-IDF
            doc_terms = self._tokenize(doc_content)
            doc_tfidf = self._compute_tfidf(doc_terms)

            # Compute cosine similarity
            similarity = self._cosine_similarity(query_tf, doc_tfidf)

            if similarity > 0:
                # Extract element info
                element_type = self._infer_type_from_path(doc_path)
                reason = self._generate_reason(doc_path, doc_terms, query_terms)
                example = self._generate_example(doc_path)

                results.append(SemanticMatch(
                    path=doc_path,
                    element_type=element_type,
                    similarity=similarity,
                    reason=reason,
                    example=example
                ))

        # Sort by similarity and return top-k
        results.sort(key=lambda x: x.similarity, reverse=True)
        return results[:top_k]

    def find_similar(
        self,
        target_path: str,
        top_k: int = 10
    ) -> List[SemanticMatch]:
        """Find elements similar to a target element.

        Args:
            target_path: Path to target element
            top_k: Number of results to return

        Returns:
            List of similar elements
        """
        if target_path not in self.documents:
            return []

        # Use target's content as query
        query_content = self.documents[target_path]

        return self.search(query_content, top_k)

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into terms.

        Args:
            text: Text to tokenize

        Returns:
            List of terms
        """
        # Convert to lowercase
        text = text.lower()

        # Split on word boundaries
        tokens = re.findall(r'\b\w+\b', text)

        # Remove stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are',
            'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did',
            'will', 'would', 'could', 'should', 'may', 'might', 'must',
            'this', 'that', 'these', 'those', 'it', 'its'
        }

        return [t for t in tokens if t not in stop_words and len(t) > 2]

    def _compute_tf(self, terms: List[str]) -> Dict[str, float]:
        """Compute term frequency.

        Args:
            terms: List of terms

        Returns:
            Dictionary of term -> TF score
        """
        term_count = Counter(terms)
        max_count = max(term_count.values()) if term_count else 1

        # Normalized TF
        return {term: count / max_count for term, count in term_count.items()}

    def _compute_idf(self, term: str) -> float:
        """Compute inverse document frequency.

        Args:
            term: Term to compute IDF for

        Returns:
            IDF score
        """
        if term not in self.vocabulary:
            return 0.0

        # IDF = log(total_docs / doc_freq)
        return math.log(self.total_documents / self.vocabulary[term])

    def _compute_tfidf(self, terms: List[str]) -> Dict[str, float]:
        """Compute TF-IDF for terms.

        Args:
            terms: List of terms

        Returns:
            Dictionary of term -> TF-IDF score
        """
        tf = self._compute_tf(terms)
        tfidf = {}

        for term, tf_score in tf.items():
            idf_score = self._compute_idf(term)
            tfidf[term] = tf_score * idf_score

        return tfidf

    def _cosine_similarity(
        self,
        vec1: Dict[str, float],
        vec2: Dict[str, float]
    ) -> float:
        """Compute cosine similarity between two vectors.

        Args:
            vec1: First vector (term -> score)
            vec2: Second vector

        Returns:
            Similarity score (0-1)
        """
        # Get all terms
        all_terms = set(vec1.keys()) | set(vec2.keys())

        if not all_terms:
            return 0.0

        # Compute dot product
        dot_product = sum(
            vec1.get(term, 0) * vec2.get(term, 0)
            for term in all_terms
        )

        # Compute magnitudes
        mag1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
        mag2 = math.sqrt(sum(v ** 2 for v in vec2.values()))

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot_product / (mag1 * mag2)

    def _create_search_content(self, inspected) -> str:
        """Create searchable content from inspected element.

        Args:
            inspected: InspectedElement

        Returns:
            Searchable text content
        """
        parts = []

        # Add name
        parts.append(inspected.path.split('.')[-1])

        # Add docstring
        if inspected.docstring:
            parts.append(inspected.docstring)

        # Add parameter names
        if inspected.signature:
            for param in inspected.signature.parameters:
                parts.append(param.get("name", ""))

        return " ".join(parts)

    def _infer_type_from_path(self, path: str) -> str:
        """Infer element type from path.

        Args:
            path: Element path

        Returns:
            Element type string
        """
        # This would need actual type checking
        # For now, simple heuristic
        if "(" in path or ")" in path:
            return "function"
        else:
            return "unknown"

    def _generate_reason(
        self,
        path: str,
        doc_terms: List[str],
        query_terms: List[str]
    ) -> str:
        """Generate explanation for match.

        Args:
            path: Element path
            doc_terms: Document terms
            query_terms: Query terms

        Returns:
            Reason string
        """
        # Find matching terms
        matches = set(doc_terms) & set(query_terms)

        if matches:
            return f"Matches terms: {', '.join(list(matches)[:3])}"
        else:
            return "Similar semantic meaning"

    def _generate_example(self, path: str) -> str:
        """Generate example usage.

        Args:
            path: Element path

        Returns:
            Example string
        """
        name = path.split('.')[-1]
        return f"{name}(...)"
```

### CLI Integration

```python
# pydocq/cli.py

@app.command()
def search_semantic(
    module_path: str = Argument(..., help="Module to search"),
    query: str = Option(None, "--query", "-q", help="Semantic search query"),
    similar_to: str = Option(None, "--similar-to", help="Find elements similar to target"),
    top_k: int = Option(10, "--top-k", "-k", help="Number of results"),
) -> None:
    """Semantic search for functions by intent.

    MODULE_PATH is the module to search (e.g., pandas).

    Examples:
        pydocq-search-semantic pandas --query "filter rows"
        pydocq-search-semantic pandas --similar-to DataFrame.merge
    """
    from pydocq.analyzer.semantic_search import TFIDFSemanticSearch

    # Initialize search engine
    search_engine = TFIDFSemanticSearch()

    # Index module
    sys.stderr.write(f"Indexing {module_path}...\n")
    search_engine.index_module(module_path)

    # Perform search
    if query:
        results = search_engine.search(query, top_k=top_k)
    elif similar_to:
        results = search_engine.find_similar(similar_to, top_k=top_k)
    else:
        sys.stderr.write("Error: Must specify --query or --similar-to\n")
        raise Exit(code=1)

    # Output results
    output = [
        {
            "path": r.path,
            "type": r.element_type,
            "similarity": round(r.similarity, 3),
            "reason": r.reason,
            "example": r.example
        }
        for r in results
    ]

    sys.stdout.write(json.dumps(output, indent=2))
```

**Usage:**
```bash
# Search by intent
pydocq-search-semantic pandas --query "filter rows"

# Find similar functions
pydocq-search-semantic pandas --similar-to DataFrame.merge

# Control results
pydocq-search-semantic pandas --query "aggregate" --top-k 5
```

## Output Examples

### Example 1: Search by Intent

**Input:**
```bash
$ pydocq-search-semantic pandas --query "filter rows by condition"
```

**Output:**
```json
[
  {
    "path": "pandas.DataFrame.query",
    "type": "method",
    "similarity": 0.856,
    "reason": "Matches terms: query, condition, filter",
    "example": "df.query('age > 18')"
  },
  {
    "path": "pandas.DataFrame.loc",
    "type": "method",
    "similarity": 0.724,
    "reason": "Matches terms: filter, rows",
    "example": "df.loc[df['age'] > 18]"
  },
  {
    "path": "pandas.DataFrame.__getitem__",
    "type": "method",
    "similarity": 0.681,
    "reason": "Matches terms: filter",
    "example": "df[df['age'] > 18]"
  }
]
```

### Example 2: Find Similar

**Input:**
```bash
$ pydocq-search-semantic pandas --similar-to DataFrame.merge
```

**Output:**
```json
[
  {
    "path": "pandas.DataFrame.join",
    "type": "method",
    "similarity": 0.792,
    "reason": "Matches terms: join, dataframes, combine",
    "example": "df.join(other, on='key')"
  },
  {
    "path": "pandas.concat",
    "type": "function",
    "similarity": 0.745,
    "reason": "Matches terms: combine, concatenate",
    "example": "pd.concat([df1, df2])"
  }
]
```

## Testing

```python
# tests/test_semantic_search.py
import pytest
from pydocq.analyzer.semantic_search import TFIDFSemanticSearch

class TestTFIDFSemanticSearch:
    """Test suite for TF-IDF semantic search."""

    def test_index_document(self):
        """Test document indexing."""
        engine = TFIDFSemanticSearch()

        engine.index_document("test_func", "This function processes data")

        assert "test_func" in engine.documents
        assert engine.total_documents == 1

    def test_search_finds_matches(self):
        """Test that search finds matching documents."""
        engine = TFIDFSemanticSearch()

        # Index documents
        engine.index_document("func1", "process data efficiently")
        engine.index_document("func2", "parse JSON files")
        engine.index_document("func3", "handle network requests")

        # Search
        results = engine.search("data processing")

        # Should find func1
        assert len(results) > 0
        assert "func1" in [r.path for r in results]

    def test_similarity_scores(self):
        """Test that similarity scores are computed correctly."""
        engine = TFIDFSemanticSearch()

        engine.index_document("func1", "data processing function")
        engine.index_document("func2", "network request handler")

        results = engine.search("process data")

        # func1 should rank higher
        assert results[0].path == "func1"
        assert results[0].similarity > 0

    def test_find_similar(self):
        """Test finding similar elements."""
        engine = TFIDFSemanticSearch()

        engine.index_document("func1", "merge dataframes")
        engine.index_document("func2", "join dataframes")
        engine.index_document("func3", "parse xml files")

        results = engine.find_similar("func1")

        # func2 should be similar (both about dataframes)
        paths = [r.path for r in results]
        assert "func2" in paths

    def test_top_k_limit(self):
        """Test that top-k limits results."""
        engine = TFIDFSemanticSearch()

        # Index many documents
        for i in range(20):
            engine.index_document(f"func{i}", f"function number {i}")

        results = engine.search("function", top_k=5)

        # Should return at most 5
        assert len(results) <= 5
```

## Implementation Priority

### Phase 1: TF-IDF Implementation (P1 - Immediate)
1. Implement `TFIDFSemanticSearch` class
2. Add tokenization logic
3. Implement TF-IDF computation
4. Implement cosine similarity
5. Add CLI command
6. Add tests

### Phase 2: Enhanced Features (P2 - Short-term)
1. Improve tokenization (stemming, lemmatization)
2. Add synonyms support
3. Add caching for indexed modules
4. Performance optimization

### Phase 3: Optional ML Enhancement (P3 - Future)
1. Add support for sentence-transformers (optional dependency)
2. Implement embedding-based search
3. Add hybrid TF-IDF + embedding approach

## Migration Plan

### Phase 1: Core Implementation (Week 1-2)
- [ ] Implement `TFIDFSemanticSearch` class
- [ ] Implement tokenization
- [ ] Implement TF-IDF computation
- [ ] Implement cosine similarity
- [ ] Add module indexing

### Phase 2: CLI Integration (Week 2)
- [ ] Add `search-semantic` command
- [ ] Add `--query` option
- [ ] Add `--similar-to` option
- [ ] Add `--top-k` option
- [ ] Implement output formatting

### Phase 3: Testing (Week 2-3)
- [ ] Add unit tests for all methods
- [ ] Add integration tests
- [ ] Test on real packages (pandas, json)
- [ ] Performance benchmarking

### Phase 4: Enhancement (Week 3-4)
- [ ] Improve tokenization
- [ ] Add caching
- [ ] Optimize performance
- [ ] Update documentation

## Benefits

| Benefit | Impact |
|---------|--------|
| **Intent-Based Search** | Find functions without knowing names |
| **Discovery** | Explore packages by purpose |
| **No ML Dependencies** | TF-IDF uses only Python stdlib |
| **Fast** | Quick indexing and search |
| **Extensible** | Can add ML enhancements later |

## Related Issues

- [FEAT-002: LLM-Optimized Output Format](./009-llm-output-format.md)
- [docs/features/semantic-similarity.md](../features/semantic-similarity.md) - Feature documentation

## References

- [Feature Documentation](../features/semantic-similarity.md)
- [TF-IDF Wikipedia](https://en.wikipedia.org/wiki/Tf%E2%80%93idf)
- [Cosine Similarity](https://en.wikipedia.org/wiki/Cosine_similarity)

## Checklist

- [ ] Implement `TFIDFSemanticSearch` class
- [ ] Implement `_tokenize()` method
- [ ] Implement `_compute_tf()` method
- [ ] Implement `_compute_idf()` method
- [ ] Implement `_compute_tfidf()` method
- [ ] Implement `_cosine_similarity()` method
- [ ] Implement `index_document()` method
- [ ] Implement `index_module()` method
- [ ] Implement `search()` method
- [ ] Implement `find_similar()` method
- [ ] Add `search-semantic` CLI command
- [ ] Add `--query` option
- [ ] Add `--similar-to` option
- [ ] Add `--top-k` option
- [ ] Add unit tests for all methods
- [ ] Add integration tests
- [ ] Test on real packages
- [ ] Performance benchmarking
- [ ] Update README with examples
- [ ] Document for AI agent developers
