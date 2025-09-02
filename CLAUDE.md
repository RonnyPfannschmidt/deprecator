# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development

this project uses uv for dependency management and running commands

```bash
# Install dependencies and dev environment
uv sync

# Run tests
uv run pytest

# Run lint and format code
pre-commit run --all-files

```

## Architecture Overview

The deprecator package provides a framework for managing deprecation warnings with version-aware categorization:

### Core Components

- **`Deprecator`** (`deprecator/_deprecator.py`): The main deprecation management class that:
  - Tracks package version and creates version-specific warning categories
  - Provides `define()` method to create deprecation warnings based on `gone_in`/`warn_in` versions
  - Automatically categorizes warnings as pending, active, or expired based on current version
  - Tracks all defined deprecations internally

- **`DeprecatorRegistry`** (`deprecator/_registry.py`): Manages multiple deprecator instances:
  - Caches deprecators by package name to avoid duplication
  - Provides `for_package()` method to get or create deprecators
  - Framework-specific registries allow different libraries to manage their own deprecation scopes

- **Warning Categories** (`deprecator/_deprecator.py`): Version-aware warning types:
  - `PerPackagePendingDeprecationWarning`: For future deprecations (current_version < warn_in)
  - `PerPackageDeprecationWarning`: For active deprecations (warn_in <= current_version < gone_in)
  - `PerPackageExpiredDeprecationWarning`: For expired deprecations (gone_in <= current_version)

### Public API

- `deprecate()`: Legacy decorator function for simple deprecation warnings
- `for_package(package_name)`: Get a deprecator bound to a specific package
- `registry_for_package(package_name)`: Get a registry bound to a specific package

### Version Logic

The deprecator automatically determines warning categories based on version comparison:
- If current version >= gone_in version → ExpiredDeprecationWarning (should cause errors)
- If current version >= warn_in version → DeprecationWarning (active warnings)
- Otherwise → PendingDeprecationWarning (future warnings, typically for tests)

### Testing Structure

Tests are organized by functionality:
- `test_deprecator.py`: Core deprecator functionality
- `test_registry.py`: Registry management and caching
- `test_exposed_api.py`: Public API surface
- `test_legacy_deprecator.py`: Legacy decorator compatibility
