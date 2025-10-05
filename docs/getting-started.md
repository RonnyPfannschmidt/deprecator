# Getting Started

## Installation

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

### Quick Setup with CLI

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
from deprecator import for_package

# Create a deprecator instance for your package
deprecator = for_package(__package__)

# Define your deprecations
OLD_FEATURE_DEPRECATION = deprecator.define(
    "old_feature is deprecated, use new_feature instead",
    warn_in="2.0.0",
    gone_in="3.0.0"
)
```

2. **Configure entry points** in `pyproject.toml`:

```toml
[project.entry-points."deprecator.deprecator"]
mypackage = "mypackage._deprecations:deprecator"
```

## Basic Usage

### Deprecating a Function

```python
from ._deprecations import OLD_API_DEPRECATION

@OLD_API_DEPRECATION.apply
def old_api():
    """This function is deprecated."""
    return "old implementation"

def new_api():
    """The new API that replaces old_api."""
    return "new implementation"
```

### Deprecating a Class

```python
from ._deprecations import LEGACY_CLASS_DEPRECATION

@LEGACY_CLASS_DEPRECATION.apply
class LegacyProcessor:
    """This class is deprecated."""
    pass

class ModernProcessor:
    """The replacement for LegacyProcessor."""
    pass
```

### Manual Warning Emission

```python
def complex_deprecation():
    if some_condition:
        OLD_FEATURE_DEPRECATION.warn()
    # Rest of the implementation
```

## Version Management

Deprecator automatically determines the warning type based on your package version:

| Current Version | warn_in | gone_in | Warning Type |
|-----------------|---------|---------|--------------|
| 1.0.0 | 2.0.0 | 3.0.0 | PendingDeprecationWarning |
| 2.0.0 | 2.0.0 | 3.0.0 | DeprecationWarning |
| 3.0.0 | 2.0.0 | 3.0.0 | ExpiredDeprecationWarning |

## Testing Your Deprecations

Use pytest to test that deprecations work correctly:

```python
import pytest
from mypackage._deprecations import OLD_API_DEPRECATION

def test_deprecation_warning():
    with pytest.warns(type(OLD_API_DEPRECATION)):
        from mypackage import old_api
        old_api()
```

## Next Steps

- Learn from [practical examples](cookbook.md)
- Set up [CI/CD integration](guides/ci-integration.md)
- Explore the [API reference](api/index.md)
