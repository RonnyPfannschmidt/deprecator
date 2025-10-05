# Contributing to Deprecator

We welcome contributions to deprecator! This guide will help you get started.

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/RonnyPfannschmidt/deprecator.git
   cd deprecator
   ```

2. **Set up pre-commit hooks**:
   ```bash
   uv run pre-commit install
   ```

## Running Tests

Run the test suite:

```bash
uv run pytest
```

With coverage:

```bash
uv run pytest --cov=deprecator --cov-report=term-missing
```

## Code Style

We use ruff for code formatting and linting:

```bash
# Format code
uv run ruff format

# Check linting
uv run ruff check

# Fix auto-fixable issues
uv run ruff check --fix
```

## Type Checking

Run mypy for type checking:

```bash
uv run mypy deprecator
```

## Working with Documentation

The documentation uses MkDocs with the Material theme.

### Common Documentation Tasks

```bash
# Serve docs locally at http://127.0.0.1:8000
uv run mkdocs serve

# Watch source code changes too
uv run mkdocs serve --watch deprecator

# Build documentation to ./site/
uv run mkdocs build

# Build with strict mode (fails on warnings)
uv run mkdocs build --strict

# Check for broken links and references
uv run mkdocs build --strict --verbose
```

### Documentation Structure

- `docs/` - Documentation source files in Markdown
- `mkdocs.yml` - MkDocs configuration
- API docs use `mkdocstrings` to extract docstrings from code

When adding new features, please update:
- Relevant guides in `docs/guides/`
- API documentation if public APIs change
- Examples in the cookbook if applicable

## Making Changes

1. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and ensure:
   - Tests pass
   - Code is properly formatted
   - Type hints are added where appropriate
   - Documentation is updated if needed

3. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add your descriptive commit message"
   ```

4. **Push and create a pull request**:
   ```bash
   git push origin feature/your-feature-name
   ```

## Pull Request Guidelines

- **Description**: Clearly describe what your PR does
- **Tests**: Include tests for new functionality
- **Documentation**: Update docs for API changes
- **Changelog**: Add entry to CHANGELOG.md for notable changes
- **Type hints**: Add type annotations to new code
- **One feature per PR**: Keep PRs focused on a single change

## Testing Guidelines

### Writing Tests

- Place tests in the `testing/` directory
- Follow the existing test structure
- Use descriptive test names
- Include both positive and negative test cases

Example test:

```python
def test_deprecation_warning_emitted():
    """Test that deprecation warning is properly emitted."""
    deprecator = for_package("test-package", Version("2.0.0"))
    warning = deprecator.define(
        "Test deprecation",
        warn_in="2.0.0",
        gone_in="3.0.0"
    )

    with pytest.warns(DeprecationWarning) as record:
        warning.warn()

    assert len(record) == 1
    assert "Test deprecation" in str(record[0].message)
```

## Documentation Guidelines

- Use clear, concise language
- Include code examples
- Keep examples realistic and runnable
- Update both API docs and guides when adding features

## Release Process

Releases are automated via GitHub Actions when a tag is pushed:

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Commit changes
4. Tag the release:
   ```bash
   git tag -a v1.2.3 -m "Release version 1.2.3"
   git push origin v1.2.3
   ```

## Getting Help

- **Issues**: Report bugs or request features on [GitHub Issues](https://github.com/RonnyPfannschmidt/deprecator/issues)
- **Discussions**: Ask questions in [GitHub Discussions](https://github.com/RonnyPfannschmidt/deprecator/discussions)

## Code of Conduct

Please be respectful and constructive in all interactions. We aim to maintain a welcoming environment for all contributors.
