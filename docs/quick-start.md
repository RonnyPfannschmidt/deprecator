# Quick Start Guide

Get up and running with deprecator in 5 minutes.

## 1. Install

```bash
pip install 'deprecator[cli]'
```

## 2. Initialize

Run the initialization command in your project:

```bash
deprecator init
```

This creates `_deprecations.py` in your package:

```python
from deprecator import for_package

deprecator = for_package(__package__)
```

## 3. Define Deprecations

Add your first deprecation to `_deprecations.py`:

```python
OLD_API_DEPRECATION = deprecator.define(
    "old_api is deprecated, use new_api instead",
    warn_in="2.0.0",  # Start warning at version 2.0.0
    gone_in="3.0.0"   # Remove in version 3.0.0
)
```

## 4. Apply to Your Code

Use the deprecation as a decorator:

```python
from ._deprecations import OLD_API_DEPRECATION

@OLD_API_DEPRECATION.apply
def old_api():
    """This function is deprecated."""
    return "old implementation"
```

## 5. Test It

Write a test to ensure the deprecation works:

```python
import pytest

def test_old_api_warns():
    from mypackage._deprecations import OLD_API_DEPRECATION

    with pytest.warns(type(OLD_API_DEPRECATION)):
        from mypackage import old_api
        old_api()
```

## Complete Example

Here's a complete example of deprecating an old function:

### `mypackage/_deprecations.py`

```python
from deprecator import for_package

deprecator = for_package(__package__)

PROCESS_DATA_DEPRECATION = deprecator.define(
    "process_data() is deprecated, use transform_data() instead",
    warn_in="1.5.0",
    gone_in="2.0.0"
)
```

### `mypackage/api.py`

```python
from ._deprecations import PROCESS_DATA_DEPRECATION

@PROCESS_DATA_DEPRECATION.apply
def process_data(data):
    """Old data processing function."""
    return transform_data(data)

def transform_data(data):
    """New data transformation function."""
    return data.upper()
```

### `tests/test_deprecations.py`

```python
import pytest
from mypackage._deprecations import PROCESS_DATA_DEPRECATION
from mypackage import process_data, transform_data

def test_process_data_deprecated():
    """Test that process_data emits deprecation warning."""
    with pytest.warns(type(PROCESS_DATA_DEPRECATION)):
        result = process_data("hello")
    assert result == "HELLO"

def test_transform_data_no_warning():
    """Test that transform_data doesn't emit warnings."""
    with pytest.warns(None) as warnings:
        result = transform_data("hello")
    assert result == "HELLO"
    assert len(warnings) == 0
```

## What's Next?

- Check the [Cookbook](cookbook.md) for more patterns
- Learn about [testing deprecations](guides/testing.md)
- Set up [CI/CD integration](guides/ci-integration.md)
- Explore the full [API Reference](api/index.md)
