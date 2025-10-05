# Deprecator

A framework for managing deprecation warnings with version-aware categorization.

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
