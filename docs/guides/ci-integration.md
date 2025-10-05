# CI/CD Integration

Deprecator provides pytest integration to help track deprecations in your CI pipeline without breaking builds.

## pytest Integration

The deprecator pytest plugin provides GitHub annotations to make deprecation warnings visible in pull requests.

### Basic Usage

```bash
# Add GitHub annotations for deprecation warnings (recommended for CI)
pytest --deprecator-github-annotations
```

This creates annotations in your GitHub pull requests showing where deprecations are used, without failing the build.

### Optional: Strict Mode

Only use `--deprecator-error` if you want to enforce zero expired deprecations:

```bash
# Fail tests if expired deprecations are found (use with caution)
pytest --deprecator-error
```

Most projects should use annotations instead to maintain visibility without blocking development.

## GitHub Actions Example

Simple workflow that makes deprecations visible:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Run tests with deprecation annotations
        run: |
          uv run pytest --deprecator-github-annotations
```

This will annotate your PRs with any deprecation warnings, making them visible without breaking the build.

## Environment Variables

Control Python's warning behavior if needed:

```yaml
env:
  # Show all deprecation warnings in logs
  PYTHONWARNINGS: default::DeprecationWarning
```

## Best Practices

1. **Use annotations, not errors**: `--deprecator-github-annotations` provides visibility without blocking
2. **Review annotations in PRs**: Check the annotations to see what deprecated code is being used
3. **Plan removal**: When you see expired deprecations in annotations, plan their removal for the next major version
4. **Don't block development**: Deprecations are warnings, not errors - they shouldn't break builds

## What You DON'T Need

Deprecator is designed to be simple. You don't need:

- Complex deprecation tracking scripts
- Custom report generators
- Manual version checking in CI
- Separate validation workflows

The annotations provide all the visibility you need. Let the version-based warning system do its job automatically.
