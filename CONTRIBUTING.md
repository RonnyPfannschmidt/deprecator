# Contributing to Deprecator

## Development Setup

This project uses uv for dependency management and running commands.

### Prerequisites

- Python 3.8+
- uv (install from https://docs.astral.sh/uv/)

### Installation

```bash
# Install dependencies and dev environment
uv sync
```

## Development Workflow

### Running Tests

```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=deprecator

# Run specific test file
uv run pytest tests/test_deprecator.py
```

### Code Quality

This project uses pre-commit hooks to maintain code quality:

```bash
# Install pre-commit hooks (one-time setup)
uv run pre-commit install

# Run all checks manually
uv run pre-commit run --all-files

# Run specific checks
uv run pre-commit run black
uv run pre-commit run ruff
```

### Code Style

- Follow PEP 8 style guidelines
- Use black for code formatting
- Use ruff for linting
- Maintain consistent docstring format
- Add type hints where appropriate



## CI Pipeline

The project uses GitHub Actions with two main jobs using **uv** for fast dependency management:

1. **Build and Inspect** (`build-and-inspect`): Runs first using [hynek/build-and-inspect-python-package](https://github.com/hynek/build-and-inspect-python-package)
   - Builds wheel and source distribution with setuptools_scm versioning
   - Lints package contents and metadata
   - Creates detailed job summaries
   - Uploads artifacts for testing and potential PyPI upload

2. **Testing** (`test`): Tests against built artifacts on Python 3.8-3.12
   - Downloads and installs the built wheel (testing what users get!)
   - Code quality checks with uv (ruff, mypy)
   - Test execution with coverage against installed package
   - Coverage reporting via Codecov

**Optional PyPI Upload**: Ready-to-use jobs for Test PyPI and PyPI (commented out by default)


## Making Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `uv run pytest`
6. Run code quality checks: `uv run pre-commit run --all-files`
7. Commit your changes with a clear message
8. Push to your fork and create a pull request

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
