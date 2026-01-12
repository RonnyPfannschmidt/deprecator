# Changelog

All notable changes to deprecator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- `warn_in` now defaults to `min(gone_in, current_version)` when not specified,
  fixing ValueError when defining deprecations with only `gone_in` and
  `current_version > gone_in` ([#5](https://github.com/RonnyPfannschmidt/deprecator/pull/5))

## [26.1.0] - 2026-01-12

Major rewrite introducing the modern deprecator API.

### Added
- **New Deprecator API**: `for_package()` function to get version-aware deprecators
- **Automatic warning transitions**: Warnings automatically change type based on package version
  - `PendingDeprecationWarning` before `warn_in` version
  - `DeprecationWarning` between `warn_in` and `gone_in`
  - `ExpiredDeprecationWarning` after `gone_in` version
- **Registry system**: `registry_for()` for framework ecosystems with multiple packages
- **CLI tools**: `deprecator init`, `show-registry`, `show-package`, `validate-package`, `list-packages`
- **pytest plugin**: `--deprecator-github-annotations` for CI visibility, `--deprecator-error` for strict mode
- **Entry point discovery**: Automatic discovery of deprecators and registries via `deprecator.deprecator` and `deprecator.registry` entry points
- **Type annotations**: Full mypy support with `py.typed` marker
- **Rich display**: Optional rich-based terminal output for CLI
- MkDocs-based documentation with Material theme and GitHub Pages deployment
- Comprehensive user guide with cookbook, migration, and testing guides
- "Why deprecator?" section explaining lifecycle management benefits
- Framework Developer section for registry documentation

### Changed
- Minimum Python version raised to 3.10
- CLI migrated from argparse to Click
- Deprecated legacy `deprecate()` decorator (still available for compatibility)
- Documentation restructured for better end-user navigation

### Architecture
- `Deprecator` class: Main deprecation management with version-aware warning categorization
- `DeprecatorRegistry`: Manages multiple deprecators for framework ecosystems
- Per-package warning classes: Dynamic warning class creation for better filtering

## [0.1.0] - 2024

Initial release with basic deprecation decorator.

### Added
- `deprecate()` decorator for simple deprecation warnings
- Basic warning emission with customizable message and category

---

For the full commit history, see the [GitHub repository](https://github.com/RonnyPfannschmidt/deprecator).
