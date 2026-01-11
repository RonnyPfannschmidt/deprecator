# Migration Guide

This guide helps you migrate deprecated code smoothly and communicate changes effectively to your users.

## Planning a Deprecation

### 1. Choose Your Timeline

Follow semantic versioning principles:

- **Major versions** (X.0.0): Can remove deprecated features
- **Minor versions** (x.Y.0): Can add deprecation warnings
- **Patch versions** (x.y.Z): Should not introduce new deprecations

Example timeline:
```python
# In version 1.5.0: Introduce deprecation warning
OLD_API_DEPRECATION = deprecator.define(
    "old_api will be removed in 2.0.0",
    warn_in="1.5.0",  # Start warning
    gone_in="2.0.0"   # Remove completely
)
```

### 2. Provide Clear Messages

Include what, why, and how in your deprecation messages:

```python
DETAILED_DEPRECATION = deprecator.define(
    "DataFrame.append() is deprecated due to poor performance. "
    "Use pd.concat() instead. "
    "See https://docs.example.com/migration/append-to-concat for details.",
    warn_in="1.8.0",
    gone_in="2.0.0"
)
```

## Migration Patterns

### Pattern 1: Simple Function Replacement

When replacing a function with a new one:

```python
# _deprecations.py
OLD_FUNCTION_DEPRECATION = deprecator.define(
    "process() is deprecated, use process_data() instead",
    warn_in="1.5.0",
    gone_in="2.0.0"
)

# api.py
@OLD_FUNCTION_DEPRECATION.apply
def process(data):
    """Old function - wraps the new one for compatibility."""
    return process_data(data)

def process_data(data):
    """New function with improved implementation."""
    # New implementation
    return enhanced_processing(data)
```

### Pattern 2: Parameter Changes

When changing function parameters:

```python
# Support both old and new parameter names
def configure(*, new_param=None, old_param=None):
    """Configure with updated parameter name."""
    if old_param is not None:
        PARAM_RENAME_DEPRECATION.warn()
        if new_param is None:
            new_param = old_param
        else:
            raise ValueError("Cannot specify both new_param and old_param")

    if new_param is None:
        raise ValueError("new_param is required")

    # Use new_param
    return do_configuration(new_param)
```

### Pattern 3: Class Migration

When replacing entire classes:

```python
@OLD_CLASS_DEPRECATION.apply
class OldProcessor:
    """Deprecated: Use NewProcessor instead."""

    def __init__(self, *args, **kwargs):
        # Optionally create the new class internally
        self._new_processor = NewProcessor(*args, **kwargs)

    def process(self, data):
        # Delegate to new implementation
        return self._new_processor.process(data)

class NewProcessor:
    """Modern replacement for OldProcessor."""

    def process(self, data):
        # New implementation
        return improved_processing(data)
```

### Pattern 4: Module Reorganization

When moving code to new modules:

```python
# old_module.py - maintains backward compatibility
from ._deprecations import MODULE_MOVE_DEPRECATION

# Emit warning when module is imported
MODULE_MOVE_DEPRECATION.warn()

# Re-export from new location
from new_module import (
    FunctionA,
    FunctionB,
    ClassC,
)

__all__ = ["FunctionA", "FunctionB", "ClassC"]
```

## Automatic Version-Based Migration

The beauty of deprecator is that it **automatically handles warning escalation based on your package version**. You define the deprecation once, and it evolves automatically:

### Phase 1: Define Once (e.g., in Version 1.3.0)

```python
# _deprecations.py - Define ONCE and never change
OLD_API_DEPRECATION = deprecator.define(
    "old_api is deprecated, use new_api instead",
    warn_in="1.5.0",
    gone_in="2.0.0"
)

# api.py - Apply the deprecation
@OLD_API_DEPRECATION.apply
def old_api():
    return new_api()

# Keep both APIs available
__all__ = ["old_api", "new_api"]
```

**Automatic behavior based on your package version:**
- **Version 1.3.0 - 1.4.x**: `PendingDeprecationWarning` (silent by default, for early testing)
- **Version 1.5.0 - 1.9.x**: `DeprecationWarning` (visible warnings to users)
- **Version 2.0.0+**: `ExpiredDeprecationWarning` (signals code should be removed)

No need to update messages or change warning types - deprecator does it all!

### Phase 2: Removal (Version 2.0.0)

When you reach the `gone_in` version, simply remove the deprecated code:

```python
# Remove old function entirely
# def old_api():  # REMOVED

# Update __all__ to exclude old API
__all__ = ["new_api"]

# Optionally, provide helpful error
def __getattr__(name):
    if name == "old_api":
        raise AttributeError(
            "old_api was removed in 2.0.0. Use new_api instead. "
            "See migration guide: https://..."
        )
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
```

## Communication Best Practices

### 1. Release Notes

Include deprecation notices in release notes:

```markdown
## Version 1.5.0

### Deprecations
- `old_api()` is deprecated and will be removed in 2.0.0.
  Use `new_api()` instead. (#123)
- Parameter `old_param` in `configure()` is deprecated.
  Use `new_param` instead. (#124)
```

### 2. Documentation Updates

Update documentation immediately when adding deprecations:

```python
def old_api():
    """Process data using the old API.

    .. deprecated:: 1.5.0
        Use :func:`new_api` instead.
        Will be removed in version 2.0.0.
    """
    pass
```

### 3. Migration Guides

Provide detailed migration documentation:

```markdown
# Migrating from old_api to new_api

## What Changed
- `old_api()` accepted positional arguments
- `new_api()` requires keyword arguments
- Return type changed from tuple to dataclass

## Before (old_api)
```python
result, status = old_api(data, "json")
```

## After (new_api)
```python
result = new_api(data, format="json")
status = result.status
```
```

## Testing Migration Paths

### Test Both Old and New APIs

```python
import pytest
from packaging.version import Version

class TestMigration:
    def test_old_api_warns(self):
        """Ensure old API emits deprecation warning."""
        with pytest.warns(DeprecationWarning):
            result = old_api(data)
        assert result == expected

    def test_new_api_no_warning(self):
        """Ensure new API doesn't emit warnings."""
        with pytest.warns(None) as warnings:
            result = new_api(data)
        assert len(warnings) == 0
        assert result == expected

    def test_migration_equivalence(self):
        """Ensure old and new APIs produce same results."""
        with pytest.warns(DeprecationWarning):
            old_result = old_api(data)

        new_result = new_api(data)
        assert old_result == new_result
```

### Test Version Transitions

```python
def test_version_based_warnings():
    """Test that warnings change based on version."""
    # Simulate different versions
    v1_5 = for_package("mypackage", Version("1.5.0"))
    v2_0 = for_package("mypackage", Version("2.0.0"))

    warning_v1_5 = v1_5.define("test", warn_in="1.5.0", gone_in="2.0.0")
    warning_v2_0 = v2_0.define("test", warn_in="1.5.0", gone_in="2.0.0")

    assert "DeprecationWarning" in str(type(warning_v1_5))
    assert "ExpiredDeprecationWarning" in str(type(warning_v2_0))
```

## Automation Tools

### Pre-commit Hook

Ensure deprecations are documented:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: check-deprecations
        name: Check deprecation documentation
        entry: python scripts/check_deprecations.py
        language: python
        files: \.py$
```

### CI Pipeline

Add deprecation checks to CI:

```yaml
# .github/workflows/deprecations.yml
name: Check Deprecations

on: [push, pull_request]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
      - name: Install dependencies
        run: pip install -e .[cli]
      - name: Validate deprecations
        run: |
          deprecator validate-package mypackage
          deprecator show-registry
```

## Common Pitfalls to Avoid

1. **Too Short Timeline**: Give users at least one minor version to migrate
2. **Unclear Messages**: Always explain what to use instead
3. **Breaking Changes in Minor Versions**: Only remove in major versions
4. **No Migration Path**: Always provide a way to achieve the same result
5. **Forgetting Documentation**: Update docs when adding deprecations
6. **Inconsistent Versioning**: Use the same version scheme throughout
