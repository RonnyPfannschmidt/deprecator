# Core Deprecator API

::: deprecator.Deprecator
    options:
      show_source: true
      show_root_heading: true
      members:
        - __init__
        - define
        - __iter__
        - __len__

## Usage Examples

### Basic Usage

```python
from deprecator import for_package

# Create a deprecator for your package
deprecator = for_package("mypackage")

# Define a deprecation
OLD_FEATURE = deprecator.define(
    "old_feature is deprecated, use new_feature instead",
    warn_in="2.0.0",
    gone_in="3.0.0"
)
```

### With Custom Version

```python
from packaging.version import Version
from deprecator import for_package

# Use a specific version for testing
deprecator = for_package("mypackage", Version("1.5.0"))

# Define deprecations based on that version
warning = deprecator.define(
    "This will be deprecated",
    warn_in="2.0.0",
    gone_in="3.0.0"
)
# This will be a PendingDeprecationWarning at version 1.5.0
```

### Accessing Deprecation Details

```python
# Iterate over all defined deprecations (Deprecator is iterable)
for deprecation in deprecator:
    print(f"Message: {deprecation.message}")
    print(f"Warning type: {type(deprecation).__name__}")

# Get the count of defined deprecations
print(f"Total deprecations: {len(deprecator)}")
```

## Version-Based Behavior

The Deprecator automatically determines the warning category based on version comparison:

| Condition | Warning Type | Description |
|-----------|--------------|-------------|
| `current < warn_in` | `PendingDeprecationWarning` | Future deprecation (usually hidden) |
| `warn_in <= current < gone_in` | `DeprecationWarning` | Active deprecation |
| `gone_in <= current` | `ExpiredDeprecationWarning` | Should be removed |

## Integration with Package Metadata

The Deprecator can automatically detect your package version:

```python
# Automatically uses the installed version of 'mypackage'
deprecator = for_package("mypackage")
print(f"Package version: {deprecator.current_version}")
```

## Custom Warning Classes

Deprecator creates package-specific warning classes that inherit from the standard Python warning hierarchy:

- `PerPackagePendingDeprecationWarning`
- `PerPackageDeprecationWarning`
- `PerPackageExpiredDeprecationWarning`

These classes include the package name in their structure for better filtering and identification.
