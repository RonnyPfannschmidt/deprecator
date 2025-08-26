# Contributing to Deprecator

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/antlong/deprecator.git
   cd deprecator
   ```

2. Install development dependencies:
   ```bash
   uv sync
   ```

3. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Development Workflow

### Running Tests
```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=deprecator
```

### Code Quality
```bash
# Run all pre-commit checks
uv run pre-commit run --all-files
```



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

## Project Structure

```
deprecator/
├── deprecator/           # Main package
│   ├── __init__.py
│   └── _deprecator.py   # Core deprecation functionality
├── test_deprecator.py   # Test suite
├── pyproject.toml       # Project configuration
├── .pre-commit-config.yaml
└── .github/workflows/ci.yml
```

## Making Changes

1. Create a feature branch
2. Make your changes
3. Add/update tests as needed
4. Run quality checks: `pre-commit run --all-files`
5. Commit (pre-commit hooks will run)
6. Push and create a pull request

## Release Process

1. Ensure all tests pass
2. Update version via git tag (setuptools_scm handles versioning)
3. Build package: `python -m build`
4. Upload to PyPI: Use GitHub release or uncomment PyPI upload jobs in CI
