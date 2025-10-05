# Warning Categories

Deprecator provides version-aware warning categories that automatically adapt based on your package version.

## Warning Class Hierarchy

All deprecator warnings inherit from Python's built-in warning classes:

```
Warning
├── DeprecationWarning
│   └── PerPackageDeprecationWarning
├── PendingDeprecationWarning
│   └── PerPackagePendingDeprecationWarning
└── PerPackageExpiredDeprecationWarning (custom)
```

## Warning Types

### PerPackagePendingDeprecationWarning

**When**: `current_version < warn_in`

Used for future deprecations that aren't active yet. These warnings are hidden by default in Python, making them useful for early testing without affecting users.

```python
# If current version is 1.0.0
deprecation = deprecator.define(
    "Will be deprecated",
    warn_in="2.0.0",
    gone_in="3.0.0"
)
# Creates a PerPackagePendingDeprecationWarning
```

### PerPackageDeprecationWarning

**When**: `warn_in <= current_version < gone_in`

Active deprecation warnings that users should see and act upon.

```python
# If current version is 2.0.0
deprecation = deprecator.define(
    "Currently deprecated",
    warn_in="2.0.0",
    gone_in="3.0.0"
)
# Creates a PerPackageDeprecationWarning
```

### PerPackageExpiredDeprecationWarning

**When**: `current_version >= gone_in`

Indicates that deprecated code should have been removed. These can be configured to raise errors in tests.

```python
# If current version is 3.0.0
deprecation = deprecator.define(
    "Should be removed",
    warn_in="2.0.0",
    gone_in="3.0.0"
)
# Creates a PerPackageExpiredDeprecationWarning
```

## Dynamic Warning Creation

Deprecator creates package-specific warning classes dynamically:

```python
from deprecator import for_package

# Creates warning classes specific to 'mypackage'
deprecator = for_package("mypackage")

# The warning classes include the package name
warning = deprecator.define("test", warn_in="1.0", gone_in="2.0")
print(type(warning).__module__)  # 'mypackage._warnings'
```

## Filtering Warnings

You can filter warnings by package:

```python
import warnings

# Show only warnings from mypackage
warnings.filterwarnings("default", module="mypackage")

# Ignore pending deprecations
warnings.filterwarnings("ignore", category=PendingDeprecationWarning)

# Error on expired deprecations
warnings.filterwarnings("error", category=ExpiredDeprecationWarning)
```

## Using with pytest

Configure pytest to handle deprecation warnings:

```python
# conftest.py
import pytest
import warnings

@pytest.fixture(autouse=True)
def configure_warnings():
    # Show deprecation warnings during tests
    warnings.filterwarnings("default", category=DeprecationWarning)

    # Treat expired deprecations as errors
    warnings.filterwarnings("error", category=ExpiredDeprecationWarning)
```

Test specific warning types:

```python
def test_pending_deprecation():
    from mypackage._deprecations import FUTURE_DEPRECATION

    # Check it's a pending deprecation
    assert "PendingDeprecation" in type(FUTURE_DEPRECATION).__name__

    with pytest.warns(PendingDeprecationWarning):
        FUTURE_DEPRECATION.warn()

def test_active_deprecation():
    from mypackage._deprecations import CURRENT_DEPRECATION

    # Check it's an active deprecation
    assert "DeprecationWarning" in type(CURRENT_DEPRECATION).__name__

    with pytest.warns(DeprecationWarning):
        CURRENT_DEPRECATION.warn()
```

## Custom Warning Behavior

Override warning behavior for specific use cases:

```python
import warnings
from contextlib import contextmanager

@contextmanager
def strict_deprecations():
    """Context manager that treats all deprecations as errors."""
    with warnings.catch_warnings():
        warnings.filterwarnings("error", category=DeprecationWarning)
        warnings.filterwarnings("error", category=PendingDeprecationWarning)
        yield

# Usage
with strict_deprecations():
    # Any deprecation will raise an exception here
    old_function()  # Raises DeprecationWarning
```

## Warning Attributes

Each warning instance has attributes you can inspect:

```python
deprecation = deprecator.define(
    "Test deprecation",
    warn_in="2.0.0",
    gone_in="3.0.0"
)

# Access deprecation details
print(deprecation.message)     # "Test deprecation"
print(deprecation.warn_in)     # "2.0.0"
print(deprecation.gone_in)     # "3.0.0"
print(deprecation.category)    # The warning class
```

## Best Practices

1. **Use appropriate categories**: Let deprecator choose the right warning type based on version
2. **Filter in production**: Consider filtering PendingDeprecationWarning in production
3. **Error on expired**: Configure CI to error on ExpiredDeprecationWarning
4. **Test all categories**: Ensure your tests cover all warning types
5. **Document filtering**: Tell users how to control warning visibility

## Environment Configuration

Control warnings via environment variables:

```bash
# Show all deprecations
export PYTHONWARNINGS=default::DeprecationWarning

# Hide pending deprecations
export PYTHONWARNINGS=ignore::PendingDeprecationWarning

# Error on expired
export PYTHONWARNINGS=error::ExpiredDeprecationWarning

# Package-specific filtering
export PYTHONWARNINGS=default::DeprecationWarning:mypackage
```
