# CLI Tool Reference

The deprecator CLI provides basic commands for initializing and inspecting deprecations.

## Installation

```bash
pip install 'deprecator[cli]'
```

## Main Commands

### `deprecator init`

Initialize deprecator in your project:

```bash
deprecator init
```

This creates a `_deprecations.py` file in your package with a basic setup.

### `deprecator show-registry`

Display deprecations in a readable format:

```bash
# Show all deprecations
deprecator show-registry

# Show as JSON
deprecator show-registry --format json
```

Example output:
```
Package     | Message                  | Warn In | Gone In | Status
------------|--------------------------|---------|---------|--------
mypackage   | old_api deprecated      | 2.0.0   | 3.0.0   | Active
```

### `deprecator validate-package`

Check if a package's deprecation setup is valid:

```bash
deprecator validate-package mypackage
```

## pytest Integration

The main pytest feature is GitHub annotations:

```bash
# Add annotations to GitHub PRs (recommended)
pytest --deprecator-github-annotations

# Strict mode (use sparingly)
pytest --deprecator-error
```

## That's It!

Deprecator is designed to be simple. You don't need:

- Complex validation scripts
- Custom report generators
- Pre-commit hooks for deprecations
- Programmatic CLI usage

The commands above cover 99% of use cases. The version-based system handles everything else automatically.

## Common Issues

| Issue | Solution |
|-------|----------|
| "Package not found" | Make sure the package is installed |
| "No entry point configured" | Run `deprecator init` |

## For Framework Authors

If you're creating a framework that needs a registry, see the [Registry Management](registry.md) documentation.
