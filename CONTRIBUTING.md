# Contributing to Deprecator

# testing
```bash

# preparing the venv
uv sync

# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=deprecator

# Run specific test file
uv run pytest tests/test_deprecator.py
```

## pre-commit and linting

- code style is enforced by the linters

```bash
# Install pre-commit hooks (one-time setup)
uv run pre-commit install

# Run all checks manually
uv run pre-commit run --all-files
```

## Making Changes

- work in your own fork
- write tests first
- ensure full coverage
- create pull requests from clearly named branches


## Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions and classes
- Include usage examples for new features
- Keep CLAUDE.md updated for development guidance

## Release Process

1. Ensure all tests pass
2. Update version via git tag (setuptools_scm handles versioning)
3. Build package: `python -m build`
4. Upload to PyPI: Use GitHub release or uncomment PyPI upload jobs in CI
