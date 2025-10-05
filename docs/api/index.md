# API Reference

The deprecator package provides a comprehensive API for managing deprecation warnings in Python packages.

## Core Components

### [Deprecator](core.md)
The main class for managing deprecations within a package. Handles version-aware warning categorization and deprecation lifecycle management.

### [Registry Management](registry.md)
Registry system for grouping related deprecations from multiple packages that contribute to a common framework or ecosystem.

### [Warning Categories](warnings.md)
Version-aware warning types that automatically categorize deprecations based on the current package version.

### [CLI Tool](cli.md)
Command-line interface for managing and monitoring deprecations across your project.

## Quick Reference

### Creating a Deprecator

```python
from deprecator import for_package

# Get a deprecator for your package
deprecator = for_package("mypackage")
```

### Defining Deprecations

```python
# Define a deprecation with version timeline
OLD_API_DEPRECATION = deprecator.define(
    "old_api is deprecated, use new_api instead",
    warn_in="2.0.0",  # Start warning at this version
    gone_in="3.0.0"   # Should be removed at this version
)
```

### Using Deprecations

```python
# As a decorator
@OLD_API_DEPRECATION.apply
def old_function():
    pass

# Manual warning emission
def complex_function():
    if condition:
        OLD_API_DEPRECATION.warn()

# With explicit location
OLD_API_DEPRECATION.warn_explicit("file.py", 42)
```

## Main Functions

### `for_package(package_name: str | PackageName, version: Optional[Version] = None) -> Deprecator`

Get or create a deprecator instance for a specific package.

**Parameters:**
- `package_name`: The package name (string or PackageName object)
- `version`: Optional specific version (defaults to installed package version)

**Returns:**
- A Deprecator instance bound to the package

### `registry_for(*, framework: str | PackageName) -> DeprecatorRegistry`

Get or create a registry for a framework to group deprecations from its contributing packages.

**Parameters:**
- `framework`: The framework name (keyword-only, e.g., "django", "flask")

**Returns:**
- A DeprecatorRegistry instance for that framework

### `deprecate(message: str, category: Optional[Type[Warning]] = None, stacklevel: int = 2)`

Legacy decorator function for simple deprecation warnings.

**Parameters:**
- `message`: The deprecation message
- `category`: Warning category (defaults to DeprecationWarning)
- `stacklevel`: Stack level for warning location

## Warning Methods

Each deprecation warning instance provides:

### `apply`
Decorator that automatically emits warnings when the decorated function/class is used.

```python
@deprecation.apply
def old_function():
    pass
```

### `warn(stacklevel: int = 2)`
Emit warning using the standard warnings system.

```python
def function():
    deprecation.warn()  # Warns at the caller's location
```

### `warn_explicit(filename: str, lineno: int, module: Optional[str] = None)`
Emit warning with explicit file location.

```python
deprecation.warn_explicit("module.py", 100)
```

## Type Annotations

The package is fully type-annotated for use with mypy and other type checkers:

```python
from deprecator import Deprecator, DeprecatorRegistry
from deprecator._types import PackageName
from packaging.version import Version

def create_deprecator(name: PackageName, ver: Version) -> Deprecator:
    return for_package(name, ver)
```

## Entry Points

The package uses entry points for plugin discovery:

```toml
[project.entry-points."deprecator.deprecator"]
mypackage = "mypackage._deprecations:deprecator"

[project.entry-points."deprecator.registry"]
myframework = "myframework._registry:registry"
```

## Environment Variables

Control deprecation behavior:

- `PYTHONWARNINGS`: Standard Python warnings control
- Example: `PYTHONWARNINGS=error::DeprecationWarning`

## Next Steps

- Explore the [Core Deprecator API](core.md)
- Learn about [Registry Management](registry.md)
- Understand [Warning Categories](warnings.md)
- Use the [CLI Tool](cli.md)
