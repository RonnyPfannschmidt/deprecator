# Deprecator Cookbook

This cookbook provides practical recipes for common deprecation scenarios.

## Table of Contents
- [Basic Deprecation Patterns](#basic-deprecation-patterns)
- [Function and Method Deprecations](#function-and-method-deprecations)
- [Class Deprecations](#class-deprecations)
- [Parameter Deprecations](#parameter-deprecations)
- [Module-Level Deprecations](#module-level-deprecations)
- [Testing Deprecations](#testing-deprecations)
- [CI/CD Integration](#cicd-integration)

## Basic Deprecation Patterns

### Setting Up Deprecator

First, initialize deprecator in your project:

```bash
deprecator init
```

This creates `_deprecations.py` with your deprecator instance:

```python
from deprecator import for_package

deprecator = for_package(__package__)
```

### Defining Deprecations

Define deprecations as module-level constants using UPPER_CASE naming:

```python
# _deprecations.py
OLD_API_DEPRECATION = deprecator.define(
    "old_api() is deprecated, use new_api() instead",
    warn_in="2.0.0",
    gone_in="3.0.0"
)

LEGACY_FORMAT_DEPRECATION = deprecator.define(
    "Legacy format support will be removed",
    warn_in="1.5.0",
    gone_in="2.0.0",
    replace_with="Use JSON format instead"
)
```

## Function and Method Deprecations

### Simple Function Deprecation

```python
from ._deprecations import OLD_API_DEPRECATION

@OLD_API_DEPRECATION.apply
def old_api(data):
    """Process data using the old API."""
    # Existing implementation
    return process_data(data)

# The new API that replaces it
def new_api(data, *, format="json"):
    """Process data using the new API with format support."""
    return process_data(data, format=format)
```

### Method Deprecation in Classes

```python
from ._deprecations import LEGACY_METHOD_DEPRECATION

class DataProcessor:
    @LEGACY_METHOD_DEPRECATION.apply
    def process_legacy(self, data):
        """Legacy processing method."""
        return self.process(data, legacy=True)

    def process(self, data, *, legacy=False):
        """Modern processing method."""
        # Implementation
        pass
```

### Deprecating Optional Parameters

When you need to deprecate a parameter but maintain backward compatibility:

```python
from ._deprecations import OLD_PARAM_DEPRECATION

def process_data(data, old_format=None, *, new_format=None):
    """Process data with format specification."""
    if old_format is not None:
        OLD_PARAM_DEPRECATION.warn()
        new_format = old_format

    # Process with new_format
    return do_processing(data, new_format)
```

## Class Deprecations

### Entire Class Deprecation

```python
from ._deprecations import OLD_CLASS_DEPRECATION

@OLD_CLASS_DEPRECATION.apply
class LegacyProcessor:
    """This entire class is deprecated."""
    def process(self, data):
        return data

# Modern replacement
class DataProcessor:
    """Modern processor that replaces LegacyProcessor."""
    def process(self, data):
        return enhanced_processing(data)
```

### Deprecating Class Inheritance

```python
from ._deprecations import BASE_CLASS_DEPRECATION

@BASE_CLASS_DEPRECATION.apply
class DeprecatedBase:
    """Base class that should not be used anymore."""
    pass

# Encourage composition or different base
class ModernBase:
    """Use this base class instead."""
    pass
```

## Parameter Deprecations

### Keyword Argument Renaming

```python
from ._deprecations import PARAM_NAME_DEPRECATION

def configure(*, new_name=None, old_name=None):
    """Configure with renamed parameter."""
    if old_name is not None:
        PARAM_NAME_DEPRECATION.warn()
        if new_name is None:
            new_name = old_name

    if new_name is None:
        raise ValueError("new_name is required")

    # Use new_name
    do_configuration(new_name)
```

### Deprecating Positional Arguments

```python
from ._deprecations import POSITIONAL_ARG_DEPRECATION

def api_call(endpoint, *, data=None, **kwargs):
    """
    API call that no longer accepts positional data argument.

    Old usage: api_call('/users', {'name': 'Alice'})
    New usage: api_call('/users', data={'name': 'Alice'})
    """
    # Check if data was passed positionally (via kwargs trick)
    if 'deprecated_data' in kwargs:
        POSITIONAL_ARG_DEPRECATION.warn()
        data = kwargs.pop('deprecated_data')

    return make_request(endpoint, data)
```

## Module-Level Deprecations

### Deprecating Module Imports

Create a `_deprecated_module.py`:

```python
# _deprecated_module.py
from ._deprecations import MODULE_DEPRECATION

# Emit warning on import
MODULE_DEPRECATION.warn()

# Re-export from new location for compatibility
from new_module import *

__all__ = ['exported_function', 'ExportedClass']
```

### Deprecating Module Attributes

```python
# module.py
from ._deprecations import ATTRIBUTE_DEPRECATION

def __getattr__(name):
    if name == "OLD_CONSTANT":
        ATTRIBUTE_DEPRECATION.warn()
        return "old_value"
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
```

## Testing Deprecations

### Testing That Deprecation Warnings Are Emitted

```python
import pytest
from mypackage._deprecations import OLD_API_DEPRECATION

def test_old_api_emits_warning():
    """Test that old_api emits deprecation warning."""
    with pytest.warns(type(OLD_API_DEPRECATION)):
        from mypackage import old_api
        result = old_api("data")

    assert result == expected_result
```

### Testing Version Transitions

```python
from packaging.version import Version
from mypackage import deprecator

def test_deprecation_categories():
    """Test that deprecations have correct categories based on version."""
    # Simulate different versions
    future_deprecator = deprecator.for_package("mypackage", Version("3.0.0"))

    warning = future_deprecator.define(
        "Test warning",
        warn_in="2.0.0",
        gone_in="3.0.0"
    )

    # Should be expired at version 3.0.0
    assert "ExpiredDeprecationWarning" in str(type(warning))
```

### Using pytest Fixtures for Deprecation Testing

```python
# conftest.py
import pytest
from packaging.version import Version
from deprecator import for_package

@pytest.fixture
def test_deprecator():
    """Deprecator for testing with controllable version."""
    return for_package("test-package", Version("1.0.0"))

# test_deprecations.py
def test_warning_emission(test_deprecator):
    warning = test_deprecator.define(
        "Test deprecation",
        warn_in="0.5.0",
        gone_in="2.0.0"
    )

    with pytest.warns(DeprecationWarning):
        warning.warn()
```

## CI/CD Integration

### GitHub Actions Integration

Add to your test workflow:

```yaml
- name: Run tests with deprecation checking
  run: |
    pytest --deprecator-error --deprecator-github-annotations
```

This will:
- Fail tests if expired deprecations are found (`--deprecator-error`)
- Output GitHub annotations for deprecation warnings (`--deprecator-github-annotations`)

### Pre-commit Hook

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: validate-deprecations
        name: Validate deprecations
        entry: deprecator validate-package
        language: system
        args: [your-package-name]
        pass_filenames: false
```

### Monitoring Deprecation Status

Add a CI job to monitor deprecations:

```bash
#!/bin/bash
# check-deprecations.sh

# Show all deprecations
deprecator show

# Validate package configuration
deprecator validate-package mypackage

# Exit with error if expired deprecations exist
if deprecator show | grep -q "expired"; then
    echo "ERROR: Expired deprecations found!"
    exit 1
fi
```

## Best Practices

1. **Define deprecations early**: Add deprecations at least one major version before removal
2. **Use clear messages**: Explain what's deprecated and what to use instead
3. **Be consistent with versions**: Follow semantic versioning for `warn_in` and `gone_in`
4. **Test your deprecations**: Ensure warnings are emitted and upgrades paths work
5. **Document migrations**: Provide clear migration guides for deprecated features
6. **Group related deprecations**: Define related deprecations together in `_deprecations.py`
7. **Monitor in CI**: Use pytest plugin and CLI tools to catch expired deprecations early

## Migration Example

Here's a complete example of migrating from an old API to a new one:

```python
# _deprecations.py
from deprecator import for_package

deprecator = for_package(__package__)

# Define the deprecation timeline
OLD_PROCESS_API = deprecator.define(
    "process() is deprecated. Use process_data() with format parameter",
    warn_in="2.0.0",
    gone_in="3.0.0"
)

# api.py
from ._deprecations import OLD_PROCESS_API

@OLD_PROCESS_API.apply
def process(data, type="json"):
    """Old API - will be removed in 3.0.0."""
    return process_data(data, format=type)

def process_data(data, *, format="json"):
    """New API with keyword-only format parameter."""
    # Modern implementation
    return do_processing(data, format)

# Allow both during transition period
__all__ = ["process", "process_data"]  # Remove "process" in 3.0.0
```

Users can gradually migrate:
```python
# Old code (generates warning in 2.0+, fails in 3.0+)
result = process(my_data, "xml")

# New code (works in all versions)
result = process_data(my_data, format="xml")
```
