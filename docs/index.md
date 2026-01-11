# Deprecator

A framework for managing deprecation warnings with version-aware categorization.

## Why Deprecator?

Managing deprecations manually is tedious and error-prone. You end up:

- **Updating messages** as versions change ("will be removed in 2.0" → "removed in 3.0")
- **Changing warning types** manually (PendingDeprecationWarning → DeprecationWarning)
- **Forgetting to remove** deprecated code when the deadline arrives
- **Inconsistent patterns** across your codebase

**Deprecator solves this with automatic lifecycle management:**

```python
# Define once - never update
OLD_API = deprecator.define(
    "old_api is deprecated, use new_api instead",
    warn_in="2.0.0",   # Start warning at version 2.0.0
    gone_in="3.0.0"    # Should be removed at version 3.0.0
)
```

The warning type changes **automatically** based on your package version:

| Your Package Version | Warning Type | Meaning |
|---------------------|--------------|---------|
| 1.x (before warn_in) | `PendingDeprecationWarning` | Heads up for maintainers |
| 2.x (warn_in → gone_in) | `DeprecationWarning` | Active warning to users |
| 3.x (after gone_in) | `ExpiredDeprecationWarning` | Code should be removed |

### Surrounding Automation

Deprecator integrates with your development workflow:

- **pytest plugin**: Annotate deprecations in GitHub PRs without breaking builds
- **CLI tools**: Validate and inspect deprecations across packages
- **Entry points**: Discover deprecations from installed packages automatically

## Overview

The deprecator package provides a structured approach to handling deprecation warnings in Python packages, automatically categorizing warnings based on version comparisons and providing flexible management of deprecation policies across different packages and frameworks.

## Features

- **Version-Aware Warnings**: Automatically categorizes deprecations based on current package version
- **Multiple Warning Levels**: Pending, active, and expired deprecation warnings
- **Framework Support**: Manage deprecations across different frameworks and libraries
- **CLI Tools**: Command-line interface for managing and monitoring deprecations
- **Testing Integration**: pytest plugin for testing deprecation warnings
- **Type-Safe**: Full type annotations and mypy support

## Quick Example

```python
--8<-- "examples/basic_deprecation.py"
```

## Installation

Install deprecator with CLI support:

```bash
pip install 'deprecator[cli]'
```

Or add to your `pyproject.toml`:

```toml
[project]
dependencies = [
    "deprecator",
]

# Optional: CLI support
[project.optional-dependencies]
cli = ["deprecator[cli]"]
```

## Next Steps

- [Get Started](getting-started.md) - Set up deprecator in your project
- [Cookbook](cookbook.md) - Practical examples and patterns
- [API Reference](api/index.md) - Complete API documentation
- [CI/CD Integration](guides/ci-integration.md) - Integrate with your workflow
