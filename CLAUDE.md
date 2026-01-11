# Claude Development Guide

This document provides context and guidelines for AI assistants working on the deprecator project.

## Project Overview

Deprecator is a Python framework for managing deprecation warnings with version-aware categorization. The key insight is that deprecation warnings should automatically transition through different states (pending → active → expired) based on the package version, without requiring manual updates to deprecation messages.

## Development Philosophy

1. **No Manual Updates**: Once a deprecation is defined with `warn_in` and `gone_in` versions, it should never need updating. The framework handles all transitions automatically.

2. **Version-Driven**: Everything is driven by semantic versioning. The warning type changes automatically based on the current package version.

3. **Framework Agnostic**: While providing a default registry, deprecator supports multiple registries for different frameworks (Django, Flask, etc.).

## Development Environment

This project uses `uv` for dependency management. All commands should use `uv run`:

```bash
# Run tests
uv run pytest

# Format code
uv run ruff format

# Check linting
uv run ruff check

# Type checking
uv run mypy deprecator

# Serve documentation
uv run mkdocs serve

# Run pre-commit hooks
uv run pre-commit run --all-files
```

**Important**: Never suggest `pip install` or separate installation commands. The `uv run` command handles dependencies automatically.

## Code Structure

- `deprecator/_deprecator.py` - Core Deprecator class
- `deprecator/_registry.py` - Registry management for multiple deprecators
- `deprecator/_warnings.py` - Dynamic warning class creation
- `deprecator/cli.py` - Command-line interface
- `testing/` - Test files (not `tests/`)

## Key Concepts

### Automatic Warning Transitions

```python
# Define once - never update
DEPRECATION = deprecator.define(
    "old_api is deprecated, use new_api instead",
    warn_in="2.0.0",
    gone_in="3.0.0"
)

# Automatically becomes:
# - PendingDeprecationWarning (before 2.0.0)
# - DeprecationWarning (2.0.0 to 2.9.x)
# - ExpiredDeprecationWarning (3.0.0+)
```

### No Message Updates

Never suggest updating deprecation messages during the lifecycle. This is an anti-pattern:

```python
# ❌ WRONG - Don't do this
URGENT_DEPRECATION = deprecator.define(
    "old_api will be removed in next release!",  # Don't update messages
    warn_in="1.5.0",
    gone_in="2.0.0"
)

# ✅ CORRECT - Define once
OLD_API_DEPRECATION = deprecator.define(
    "old_api is deprecated, use new_api instead",
    warn_in="1.5.0",
    gone_in="2.0.0"
)
```

## Testing

Tests are in the `testing/` directory (not `tests/`). Key test files:
- `test_deprecator.py` - Core functionality
- `test_registry.py` - Registry management
- `test_exposed_api.py` - Public API surface

Run tests with:
```bash
uv run pytest
uv run pytest --cov=deprecator --cov-report=term-missing
```

## Documentation

Documentation uses MkDocs with Material theme. Source files are in `docs/`.

Key documentation principles:
- Focus on the automatic nature of version-based transitions
- Emphasize "define once" philosophy
- Show practical examples in the cookbook
- Keep API documentation synchronized with code

## Common Pitfalls to Avoid

1. **Don't suggest manual warning updates** - The whole point is automatic transitions
2. **Don't use pip commands** - Always use `uv run`
3. **Don't create wrapper scripts** - Use tools directly with `uv run`
4. **Don't suggest complex build processes** - Keep it simple

## GitHub Integration

- Documentation deploys via GitHub Actions to GitHub Pages
- Uses artifact-based deployment (not gh-pages branch)
- CI runs tests across Python 3.8-3.13

## Type Safety

The project uses type hints throughout. Always maintain type annotations:
- Use `from __future__ import annotations` for forward references
- Prefer `str | None` over `Optional[str]` (Python 3.10+ union syntax)
- Run `uv run mypy deprecator` to check types

## Code Style

- Ruff for formatting and linting
- Line length: default (88 characters)
- Use docstrings for public APIs
- Follow existing patterns in the codebase
