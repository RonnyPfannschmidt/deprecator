# CLI Tool Reference

The deprecator CLI provides commands for initializing and inspecting deprecations in your projects.

## Installation

```bash
pip install 'deprecator[cli]'
```

## Command Reference

::: mkdocs-click
    :module: deprecator.cli
    :command: cli
    :prog_name: deprecator
    :depth: 2
    :style: table

## Usage Examples

### Initialize Deprecator

Initialize deprecator in your current project:

```bash
deprecator init
```

This creates a `_deprecations.py` file in your package with a basic setup.

### Show Registry Deprecations

Display deprecations from the default registry:

```bash
# Show all deprecations from all packages
deprecator show-registry

# Show deprecations for a specific package
deprecator show-registry mypackage
```

Example output:
```
Package     | Message                  | Warn In | Gone In | Status
------------|--------------------------|---------|---------|--------
mypackage   | old_api deprecated      | 2.0.0   | 3.0.0   | Active
```

### Show Package Deprecators

Display all deprecators defined by a specific package:

```bash
deprecator show-package mypackage
```

This shows all deprecator instances that a package has defined through entry points.

### Validate Package

Check if a package's deprecation setup is valid:

```bash
deprecator validate-package mypackage
```

This validates:
- All deprecator entry points are correctly configured
- All registry entry points are correctly configured
- The referenced objects can be imported

### List Packages

List all packages that have deprecator or registry entry points:

```bash
deprecator list-packages
```

## pytest Integration

The deprecator pytest plugin provides GitHub annotations and strict mode:

```bash
# Add annotations to GitHub PRs (recommended for CI)
pytest --deprecator-github-annotations

# Strict mode - treat deprecations as errors (use sparingly)
pytest --deprecator-error
```

## Exit Codes

The CLI uses the following exit codes:

| Code | Meaning |
|------|---------|
| 0 | Success, no issues found |
| 1 | Validation failures or expired deprecations found |
| 2 | Configuration or usage errors |

## Common Issues

| Issue | Solution |
|-------|----------|
| "Package not found" | Make sure the package is installed in your environment |
| "No entry point configured" | Run `deprecator init` to set up your package |
| "Import error" | Check that your deprecator module is correctly structured |

## Environment Variables

You can control deprecation warnings using standard Python environment variables:

```bash
# Show all warnings
PYTHONWARNINGS=always deprecator show-registry

# Treat warnings as errors
PYTHONWARNINGS=error::DeprecationWarning deprecator show-registry
```

## For Framework Authors

If you're creating a framework that needs a registry, see the [Registry Management](registry.md) documentation for details on creating and managing framework-specific registries.
