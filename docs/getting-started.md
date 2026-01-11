# Getting Started

## Quick Start (5 minutes)

Get up and running with deprecator quickly:

### 1. Install

```bash
pip install 'deprecator[cli]'
```

### 2. Initialize

Run the initialization command in your project:

```bash
deprecator init
```

This creates `_deprecations.py` in your package:

```python
from deprecator import for_package

deprecator = for_package(__package__)
```

### 3. Define Your First Deprecation

Add to `_deprecations.py`:

```python
--8<-- "examples/basic_deprecation.py"
```

### 4. Test It

```python
--8<-- "examples/test_deprecation.py"
```

## Detailed Installation Options

### Basic Installation

Install deprecator using pip:

```bash
pip install deprecator
```

### With CLI Support

To use the command-line tools, install with the CLI extra:

```bash
pip install 'deprecator[cli]'
```

### Development Installation

For development, clone the repository:

```bash
git clone https://github.com/RonnyPfannschmidt/deprecator.git
cd deprecator
# Use uv run for all development commands
```

## Project Setup

### Automatic Setup with CLI

The easiest way to set up deprecator in your project is using the CLI:

```bash
# If installed globally
deprecator init

# Or using uv in development
uv run deprecator init
```

This command will:
1. Create a `_deprecations.py` module in your package
2. Configure your `pyproject.toml` with entry points
3. Set up the deprecator instance for your package

### Manual Setup

If you prefer manual setup or need custom configuration:

1. **Create a deprecations module** (`_deprecations.py`):

```python
--8<-- "examples/package_setup.py"
```

2. **Configure entry points** in `pyproject.toml`:

```toml
[project.entry-points."deprecator.deprecator"]
mypackage = "mypackage._deprecations:deprecator"
```

## Basic Usage Patterns

### Deprecating a Function

See the basic example from earlier, or use the decorator pattern:

```python
--8<-- "examples/decorator_usage.py"
```

### Deprecating a Class

```python
--8<-- "examples/class_deprecation.py"
```

### Manual Warning Emission

```python
--8<-- "examples/manual_warning.py"
```

## Version Management

Deprecator automatically determines the warning type based on your package version:

| Current Version | warn_in | gone_in | Warning Type |
|-----------------|---------|---------|--------------|
| 1.0.0 | 2.0.0 | 3.0.0 | PendingDeprecationWarning |
| 2.0.0 | 2.0.0 | 3.0.0 | DeprecationWarning |
| 3.0.0 | 2.0.0 | 3.0.0 | ExpiredDeprecationWarning |

## Complete Example

Here's a complete example of deprecating an old function:

### `mypackage/_deprecations.py`

```python
--8<-- "examples/package_setup.py"
```

### `mypackage/api.py`

```python
--8<-- "examples/decorator_usage.py"
```

### `tests/test_deprecations.py`

```python
--8<-- "examples/complete_test.py"
```

## Next Steps

- Check the [Cookbook](cookbook.md) for more advanced patterns
- Learn about [testing deprecations](guides/testing.md) in detail
- Set up [CI/CD integration](guides/ci-integration.md)
- Explore the full [API Reference](api/index.md)
