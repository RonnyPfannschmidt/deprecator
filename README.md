# Deprecator

A framework for managing deprecation warnings with version-aware categorization.

## Overview

The deprecator package provides a structured approach to handling deprecation warnings in Python packages, automatically categorizing warnings based on version comparisons and providing flexible management of deprecation policies across different packages and frameworks.

## Architecture

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
  - Each registry has a `framework` attribute identifying the framework/library it serves

- **Warning Categories** (`deprecator/_deprecator.py`): Version-aware warning types:
  - `PerPackagePendingDeprecationWarning`: For future deprecations (current_version < warn_in)
  - `PerPackageDeprecationWarning`: For active deprecations (warn_in <= current_version < gone_in)
  - `PerPackageExpiredDeprecationWarning`: For expired deprecations (gone_in <= current_version)

### Public API

- `deprecate()`: Legacy decorator function for simple deprecation warnings
- `for_package(package_name: PackageName | str)`: Get a deprecator bound to a specific package
- `registry_for_package(package_name: PackageName | str)`: Get a registry bound to a specific framework

### Version Logic

The deprecator automatically determines warning categories based on version comparison:
- If current version >= gone_in version → ExpiredDeprecationWarning (should cause errors)
- If current version >= warn_in version → DeprecationWarning (active warnings)
- Otherwise → PendingDeprecationWarning (future warnings, typically for tests)

## Usage

```python
from deprecator import for_package

# Get a deprecator for your package (accepts str or PackageName)
deprecator = for_package("mypackage")

# Define a deprecation
my_warning = deprecator.define(
    "old_function is deprecated",
    warn_in="2.0.0",
    gone_in="3.0.0"
)

# Use the warning in different ways
def old_function():
    # Standard warning (uses stacklevel=2 by default)
    my_warning.warn()
    # ... existing functionality

def wrapper_function():
    # Custom stacklevel for wrapper functions
    my_warning.warn(stacklevel=3)

def linter_integration():
    # Explicit file/line for tools and linters
    my_warning.warn_explicit("myfile.py", 42)
```

## Warning Methods

Each deprecation warning instance provides two methods for emitting warnings:

- **`warn(stacklevel=2)`**: Emit warning using the standard warnings system
- **`warn_explicit(filename, lineno, module=None)`**: Emit warning with explicit location

These mirror the stdlib `warnings.warn()` and `warnings.warn_explicit()` functions.

## Testing Structure

Tests are organized by functionality:
- `test_deprecator.py`: Core deprecator functionality
- `test_registry.py`: Registry management and caching
- `test_exposed_api.py`: Public API surface
- `test_legacy_deprecator.py`: Legacy decorator compatibility
