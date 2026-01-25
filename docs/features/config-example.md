# Configuration Example

Example configuration file for docs-cli.

## Location

Configuration file: `.docs-cli/config.yaml` (project root) or `~/.config/docs-cli/config.yaml` (global)

## Basic Configuration

```yaml
# .docs-cli/config.yaml

# Project information
project:
  name: "myproject"
  version: "1.0.0"
  description: "My awesome project"

# Documentation settings
documentation:
  # Default output format
  default_format: json  # json | schema | raw | signature

  # Include source code in output
  include_source: false

  # Include private members (starting with _)
  include_private: false

# Discovery settings
discovery:
  # How to discover public elements
  # Options: __all__ | init_imports | naming_convention
  strategy: __all__

  # Fallback strategies if primary fails
  fallback_strategies:
    - init_imports
    - naming_convention

# SDK settings
sdk:
  # Enable SDK decorators
  enabled: true

  # Require specific decorators
  require:
    - category
    - examples

  # Allowed tag prefixes
  allowed_tags:
    - "stable"
    - "experimental"
    - "deprecated"
    - "perf:*"
    - "domain:*"

# Output settings
output:
  # JSON indentation
  indent: 2

  # Sort keys in JSON output
  sort_keys: false

  # Include metadata in output
  include_metadata: true

  # Compact output (no extra whitespace)
  compact: false

# Analysis settings
analysis:
  # Relationship analysis
  relationships:
    enabled: true
    include_external: false
    max_depth: 2

  # Complexity analysis
  complexity:
    enabled: true
    metrics:
      - cyclomatic
      - cognitive
      - loc

# Index settings
indexing:
  # Auto-build index on first query
  auto_build: true

  # Index location
  index_dir: ".docs-cli/indexes"

  # Compress indexes
  compress: true

  # Auto-update indexes (when package changes)
  auto_update: false

# Caching
cache:
  # Enable query result cache
  enabled: true

  # Cache directory
  cache_dir: ".docs-cli/cache"

  # Max cache size (MB)
  max_size: 100

  # Cache TTL (seconds)
  ttl: 3600

# Logging
logging:
  # Log level: debug | info | warning | error
  level: info

  # Log file (optional, defaults to stdout)
  # file: ".docs-cli/logs/docs-cli.log"

# Hook settings
hooks:
  # Enable hook system
  enabled: false

  # Hook scripts directory
  hooks_dir: ".docs-cli/hooks"

# Linter settings
lint:
  # Enabled rules
  rules:
    - missing_docstring
    - missing_parameter_docs
    - docstring_mismatch
    - example_fails

  # Disabled rules
  disabled:
    - missing_examples
    - no_type_hints

  # Severity thresholds
  thresholds:
    fail_on: error  # error | warning | info
    min_score: B     # A | B | C | D | F

# Template settings
templates:
  # Template directory
  templates_dir: ".docs-cli/templates"

  # Default template style
  default_style: full  # basic | full | sdk

  # Docstring style
  docstring_style: google  # google | numpy | rest
```

## Environment-Specific Configuration

```yaml
# .docs-cli/config.yaml

# Development environment
development:
  output:
    include_source: true
    include_private: true
  analysis:
    complexity:
      enabled: true
  logging:
    level: debug

# Production environment
production:
  output:
    include_source: false
    include_private: false
  analysis:
    complexity:
      enabled: false
  cache:
    enabled: true
    ttl: 86400  # 24 hours
```

Use environment:
```bash
doc mypackage --env development
```

## Package-Specific Configuration

```yaml
# .docs-cli/config.yaml

packages:
  pandas:
    # Use pre-built index
    index: ".docs-cli/indexes/pandas.docs-index"

    # Custom settings
    discovery:
      strategy: __all__

    output:
      include_metadata: true

  numpy:
    # Different settings
    discovery:
      strategy: init_imports

    analysis:
      relationships:
        include_external: true
```

## Feature Flags

```yaml
# .docs-cli/config.yaml

features:
  # Experimental features
  experimental:
    semantic_search: true
    ai_summaries: false

  # Beta features
  beta:
    query_language: true
    auto_categorization: false

  # Deprecated features
  deprecated:
    legacy_format: false
```

## Profile Configuration

```yaml
# .docs-cli/config.yaml

profiles:
  # Quick profile - fast queries, minimal output
  quick:
    output:
      compact: true
      include_metadata: false
    cache:
      enabled: true
      ttl: 7200

  # Detailed profile - full information
  detailed:
    output:
      include_source: true
      include_metadata: true
    analysis:
      relationships:
        enabled: true
      complexity:
        enabled: true

  # Development profile - verbose, debug info
  development:
    output:
      include_source: true
      include_private: true
    logging:
      level: debug
    cache:
      enabled: false

  # Production profile - optimized, cached
  production:
    output:
      compact: true
      include_metadata: false
    cache:
      enabled: true
      ttl: 86400
    indexing:
      auto_build: true
```

Use profile:
```bash
doc mypackage --profile quick
```

## Integration Configuration

```yaml
# .docs-cli/config.yaml

# Editor integration
editor:
  # Supported editors: vscode | vim | emacs
  enabled: true
  editor: vscode

  # Show documentation in editor
  show_in_editor: true

# Git integration
git:
  # Check documentation in pre-commit
  pre_commit:
    enabled: true
    run_lint: true

  # Generate changelog from doc changes
  changelog:
    enabled: false
    output: "CHANGELOG.md"

# CI/CD integration
ci:
  # Fail build on documentation errors
  fail_on_error: true

  # Generate documentation report
  report:
    enabled: true
    format: html
    output: "docs/report.html"
```

## Custom Decorators

```yaml
# .docs-cli/config.yaml

custom_decorators:
  # Define custom decorators
  my_decorator:
    module: "myproject.decorators"
    name: "documented"
    metadata:
      category: "custom"
      priority: "high"

  # Alias for existing decorator
  fast:
    alias_for: "tag"
    default_value: "perf:fast"
```

## Validation Rules

```yaml
# .docs-cli/config.yaml

validation:
  # Require documentation for public APIs
  require_docstrings:
    public: true
    protected: false
    private: false

  # Require type hints
  require_type_hints: false

  # Require examples
  require_examples:
    functions: true
    classes: true
    methods: false

  # Docstring quality
  docstring:
    min_length: 50
    max_length: 1000
    style: google  # google | numpy | rest
```

## Plugin Configuration

```yaml
# .docs-cli/config.yaml

plugins:
  # Load custom plugins
  - name: "my_plugin"
    module: "myproject.docs_plugin"
    enabled: true

  # Plugin options
  - name: "company_standards"
    module: "company.docs.plugins"
    options:
      strict_mode: true
      require_author: true
```

## Remote Configuration

```yaml
# .docs-cli/config.yaml

# Remote index server
remote:
  base_url: "https://docs.example.com"

  # Download indexes from remote
  download_indexes: true

  # Upload local indexes
  upload_indexes: false

  # Authentication
  auth:
    token: "${DOCS_CLI_TOKEN}"  # Environment variable
```

## Complete Example

```yaml
# .docs-cli/config.yaml - Complete example

project:
  name: "myproject"
  version: "1.0.0"

documentation:
  default_format: json
  include_source: false
  include_private: false

discovery:
  strategy: __all__
  fallback_strategies:
    - init_imports

sdk:
  enabled: true
  require:
    - category
  allowed_tags:
    - "stable"
    - "perf:*"
    - "domain:*"

output:
  indent: 2
  sort_keys: false
  include_metadata: true

analysis:
  relationships:
    enabled: true
    max_depth: 2
  complexity:
    enabled: true
    metrics:
      - cyclomatic
      - loc

indexing:
  auto_build: true
  index_dir: ".docs-cli/indexes"
  compress: true

cache:
  enabled: true
  cache_dir: ".docs-cli/cache"
  max_size: 100
  ttl: 3600

logging:
  level: info

lint:
  rules:
    - missing_docstring
    - docstring_mismatch
  thresholds:
    fail_on: error
    min_score: B

profiles:
  quick:
    output:
      compact: true
  detailed:
    analysis:
      relationships:
        enabled: true

validation:
  require_docstrings:
    public: true
  docstring:
    min_length: 50
    style: google
```

## Command-Line Override

Config values can be overridden via CLI:

```bash
# Override default format
doc mypackage --format schema

# Override include_private
doc mypackage --include-private

# Override log level
doc mypackage --log-level debug

# Use specific profile
doc mypackage --profile detailed
```

## Configuration Validation

Validate configuration:

```bash
doc-config validate
```

Output:
```json
{
  "valid": true,
  "errors": [],
  "warnings": [
    "Unknown option 'unknown_option' in section 'output'"
  ]
}
```

## Configuration Inheritance

Global config → Project config → CLI flags

Example:
1. Global: `~/.config/docs-cli/config.yaml`
2. Project: `.docs-cli/config.yaml`
3. CLI: `doc mypackage --format schema`

Project config overrides global, CLI flags override both.

## Multiple Environments

```yaml
# .docs-cli/config.yaml

environments:
  development:
    logging:
      level: debug
    cache:
      enabled: false

  testing:
    logging:
      level: warning
    cache:
      enabled: true

  production:
    logging:
      level: error
    cache:
      enabled: true
      ttl: 86400
```

Activate:
```bash
doc mypackage --env production
# or
export DOCS_CLI_ENV=production
doc mypackage
```

## See Also

- **[Documentation Index](./doc-index.md)** - Index configuration for performance
- **[Documentation Linter](./doc-lint.md)** - Lint configuration
- **[Agent Hooks](./agent-hooks.md)** - Hook configuration
