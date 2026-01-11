# Deprecator

A framework for managing deprecation warnings with version-aware categorization.

## Overview

The deprecator package provides a structured approach to handling deprecation warnings in Python packages, automatically categorizing warnings based on version comparisons and providing flexible management of deprecation policies across different packages and frameworks.

## Requirements

- Python 3.10 or higher

## Quick Start

1. Install deprecator with CLI support:
   ```bash
   pip install 'deprecator[cli]'
   ```

2. Initialize deprecator in your project:
   ```bash
   deprecator init
   ```
   This creates a `_deprecations.py` module and configures your `pyproject.toml`.

3. Define your deprecations:
   ```python
   # In _deprecations.py
   from deprecator import for_package

   deprecator = for_package(__package__)

   OLD_API_DEPRECATION = deprecator.define(
       "old_api is deprecated, use new_api instead",
       warn_in="2.0.0",
       gone_in="3.0.0"
   )
   ```

4. Use deprecations in your code:
   ```python
   from ._deprecations import OLD_API_DEPRECATION

   @OLD_API_DEPRECATION.apply
   def old_api():
       pass
   ```

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

# Define a deprecation (using UPPER_CASE for constants)
OLD_FUNCTION_DEPRECATION = deprecator.define(
    "old_function is deprecated, use new_function instead",
    warn_in="2.0.0",
    gone_in="3.0.0"
)

# Method 1: Use as a decorator
@OLD_FUNCTION_DEPRECATION.apply
def old_function():
    # The decorator automatically emits the warning
    # ... existing functionality
    pass

# Method 2: Emit warning manually
def another_old_function():
    # Standard warning (uses stacklevel=2 by default)
    OLD_FUNCTION_DEPRECATION.warn()
    # ... existing functionality

# Method 3: Custom stacklevel for wrapper functions
def wrapper_function():
    # Custom stacklevel for wrapper functions
    OLD_FUNCTION_DEPRECATION.warn(stacklevel=3)

# Method 4: Explicit file/line for tools and linters
def linter_integration():
    # Explicit file/line for tools and linters
    OLD_FUNCTION_DEPRECATION.warn_explicit("myfile.py", 42)
```

## Warning Methods

Each deprecation warning instance provides three methods for using deprecations:

- **`apply`**: Use as a decorator to automatically emit warnings when the decorated function/class is used
- **`warn(stacklevel=2)`**: Emit warning using the standard warnings system
- **`warn_explicit(filename, lineno, module=None)`**: Emit warning with explicit location

The `apply` decorator uses `typing_extensions.deprecated` under the hood, while `warn()` and `warn_explicit()` mirror the stdlib `warnings.warn()` and `warnings.warn_explicit()` functions.

## Cookbook

For practical examples and common patterns, see the [Cookbook](COOKBOOK.md).

## Testing Structure

Tests are organized by functionality:
- `test_deprecator.py`: Core deprecator functionality
- `test_registry.py`: Registry management and caching
- `test_exposed_api.py`: Public API surface
- `test_legacy_deprecator.py`: Legacy decorator compatibility
