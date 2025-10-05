# Testing Deprecations

This guide covers how to effectively test deprecation warnings in your code.

## Basic Testing with pytest

### Testing That Warnings Are Emitted

```python
import pytest
from mypackage._deprecations import OLD_API_DEPRECATION
from mypackage import old_api

def test_deprecated_function_warns():
    """Test that deprecated function emits warning."""
    with pytest.warns(type(OLD_API_DEPRECATION)):
        result = old_api("test data")
    assert result == expected_result
```

### Testing Warning Messages

```python
def test_deprecation_message():
    """Test that deprecation has correct message."""
    with pytest.warns(type(OLD_API_DEPRECATION)) as warning_info:
        old_api()

    # Check the warning message
    assert len(warning_info) == 1
    assert "use new_api instead" in str(warning_info[0].message)
```

### Testing That New APIs Don't Warn

```python
def test_new_api_no_warning():
    """Ensure new API doesn't emit deprecation warnings."""
    with warnings.catch_warnings():
        warnings.simplefilter("error")  # Turn warnings into errors
        result = new_api("test data")  # Should not raise
    assert result == expected_result
```

## Testing Different Warning Categories

Deprecator automatically changes warning categories based on version:

```python
from packaging.version import Version
from deprecator import for_package

def test_warning_categories():
    """Test that deprecations have correct categories based on version."""
    # Test with different versions
    early_deprecator = for_package("mypackage", Version("1.0.0"))
    active_deprecator = for_package("mypackage", Version("2.0.0"))
    expired_deprecator = for_package("mypackage", Version("3.0.0"))

    # Same definition, different warning types based on version
    early_warning = early_deprecator.define(
        "Test warning", warn_in="2.0.0", gone_in="3.0.0"
    )
    active_warning = active_deprecator.define(
        "Test warning", warn_in="2.0.0", gone_in="3.0.0"
    )
    expired_warning = expired_deprecator.define(
        "Test warning", warn_in="2.0.0", gone_in="3.0.0"
    )

    # Check warning types
    assert "PendingDeprecationWarning" in str(type(early_warning))
    assert "DeprecationWarning" in str(type(active_warning))
    assert "ExpiredDeprecationWarning" in str(type(expired_warning))
```

## Testing Migration Paths

Ensure that old and new APIs produce equivalent results:

```python
class TestMigrationPath:
    def test_old_new_equivalence(self):
        """Ensure old and new APIs produce same results."""
        test_data = "sample data"

        # Old API (with warning)
        with pytest.warns(DeprecationWarning):
            old_result = old_api(test_data)

        # New API (no warning)
        new_result = new_api(test_data)

        assert old_result == new_result

    def test_parameter_migration(self):
        """Test that old parameters map correctly to new ones."""
        # Old parameter name (with warning)
        with pytest.warns(DeprecationWarning):
            old_result = process(old_param="value")

        # New parameter name (no warning)
        new_result = process(new_param="value")

        assert old_result == new_result
```

## Using pytest Fixtures

Create reusable fixtures for testing deprecations:

```python
# conftest.py
import pytest
from packaging.version import Version
from deprecator import for_package

@pytest.fixture
def test_deprecator():
    """Deprecator with controllable version for testing."""
    return for_package("test-package", Version("1.0.0"))

@pytest.fixture
def sample_deprecation(test_deprecator):
    """Sample deprecation for testing."""
    return test_deprecator.define(
        "Test feature is deprecated",
        warn_in="0.5.0",
        gone_in="2.0.0"
    )

# test_deprecations.py
def test_with_fixture(sample_deprecation):
    """Test using deprecation fixture."""
    with pytest.warns(type(sample_deprecation)):
        sample_deprecation.warn()
```

## Testing with Different Python Warning Filters

```python
import warnings

def test_warning_filters():
    """Test deprecations with different warning filters."""

    # Test with warnings as errors
    with warnings.catch_warnings():
        warnings.filterwarnings("error", category=DeprecationWarning)

        with pytest.raises(DeprecationWarning):
            old_api()

    # Test with warnings ignored
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        # Should not produce any warnings
        with pytest.warns(None) as warning_list:
            old_api()
        # Note: The warning is still generated but filtered
```

## Testing Decorators

Test that the deprecation decorator works correctly:

```python
def test_decorator_application():
    """Test that @deprecation.apply works correctly."""
    from mypackage._deprecations import OLD_FUNCTION_DEPRECATION

    @OLD_FUNCTION_DEPRECATION.apply
    def decorated_function():
        return "result"

    # Function should still work but emit warning
    with pytest.warns(type(OLD_FUNCTION_DEPRECATION)):
        result = decorated_function()

    assert result == "result"
```

## Testing Stack Levels

Ensure warnings point to the correct location:

```python
def test_warning_stacklevel():
    """Test that warnings have correct stack level."""
    with pytest.warns(DeprecationWarning) as warning_info:
        # This line should be reported as the warning location
        old_api()

    # Check that the warning points to this test file, not internal code
    assert __file__ in str(warning_info[0].filename)
```

## Integration with pytest Plugin

The deprecator pytest plugin provides additional functionality:

```python
# Run tests with deprecation checking
# pytest --deprecator-error  # Fail on expired deprecations
# pytest --deprecator-github-annotations  # GitHub CI annotations

def test_with_plugin(pytester):
    """Test using deprecator pytest plugin."""
    pytester.makepyfile("""
        from deprecator import for_package

        def test_expired():
            deprecator = for_package("test", "3.0.0")
            warning = deprecator.define(
                "Expired", warn_in="1.0.0", gone_in="2.0.0"
            )
            warning.warn()  # This is expired at version 3.0.0
    """)

    # Should fail with --deprecator-error
    result = pytester.runpytest("--deprecator-error")
    result.assert_outcomes(failed=1)
```

## Testing CLI Commands

Test the deprecator CLI tools:

```python
import subprocess

def test_cli_validate():
    """Test deprecator CLI validation."""
    result = subprocess.run(
        ["deprecator", "validate-package", "mypackage"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "validation passed" in result.stdout.lower()

def test_cli_show_registry():
    """Test showing deprecation registry."""
    result = subprocess.run(
        ["deprecator", "show-registry"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    # Check that your deprecations appear in output
```

## Continuous Integration Testing

### GitHub Actions Example

```yaml
name: Test Deprecations

on: [push, pull_request]

jobs:
  test-deprecations:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -e .[test,cli]

      - name: Run deprecation tests
        run: |
          # Run with deprecation error checking
          pytest tests/ --deprecator-error

      - name: Validate package deprecations
        run: |
          deprecator validate-package mypackage

      - name: Check for expired deprecations
        run: |
          deprecator show-registry
          # Fail if expired deprecations exist
          ! deprecator show-registry | grep -q "expired"
```

## Best Practices

1. **Test both paths**: Always test both deprecated and new code paths
2. **Check messages**: Verify deprecation messages are clear and helpful
3. **Test categories**: Ensure warnings have correct categories for your version
4. **Use fixtures**: Create reusable test fixtures for common deprecations
5. **Test migration**: Verify old and new APIs produce equivalent results
6. **CI integration**: Run deprecation tests in your CI pipeline
7. **Test removal**: Have tests ready to verify code removal at `gone_in` version

## Common Testing Patterns

### Pattern: Version-Specific Tests

```python
import pytest
from packaging.version import Version
from mypackage import __version__

@pytest.mark.skipif(
    Version(__version__) >= Version("2.0.0"),
    reason="Old API removed in 2.0.0"
)
def test_old_api_still_works():
    """Test old API while it still exists."""
    with pytest.warns(DeprecationWarning):
        result = old_api()
    assert result is not None

@pytest.mark.skipif(
    Version(__version__) < Version("2.0.0"),
    reason="Old API not yet removed"
)
def test_old_api_removed():
    """Test that old API is properly removed."""
    with pytest.raises(AttributeError):
        from mypackage import old_api
```

### Pattern: Parametrized Warning Tests

```python
@pytest.mark.parametrize("func,should_warn", [
    (old_api, True),
    (new_api, False),
    (legacy_function, True),
    (modern_function, False),
])
def test_deprecation_warnings(func, should_warn):
    """Test that only deprecated functions emit warnings."""
    if should_warn:
        with pytest.warns(DeprecationWarning):
            func()
    else:
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            func()  # Should not raise
```
