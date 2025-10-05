"""Pytest plugin for deprecator to convert expired deprecations to errors."""

from __future__ import annotations

import warnings
from dataclasses import dataclass, field

import pytest

from ._warnings import (
    DeprecatorWarningMixing,
    PerPackageExpiredDeprecationWarning,
)


@dataclass(frozen=True)
class GithubAnnotation:
    """Represents a GitHub Actions annotation."""

    type: str  # "error" or "warning"
    file: str
    line: str
    message: str


@dataclass(eq=False)
class DeprecatorPlugin:
    """Plugin that handles expired deprecation warnings."""

    show_github_annotations: bool
    expired_warnings_count: int = field(default_factory=int, init=False)
    github_annotations: list[GithubAnnotation] = field(default_factory=list, init=False)  # pyright: ignore[reportUnknownVariableType]

    def pytest_warning_recorded(
        self,
        warning_message: warnings.WarningMessage,
    ) -> None:
        """Track expired deprecation warnings and collect for GitHub annotations."""
        # Only process deprecator warnings
        if not isinstance(warning_message.message, DeprecatorWarningMixing):
            return

        if isinstance(warning_message.message, PerPackageExpiredDeprecationWarning):
            self.expired_warnings_count += 1

        warning_type = warning_message.message.github_warning_kind
        self.github_annotations.append(
            GithubAnnotation(
                type=warning_type,
                file=warning_message.filename,
                line=str(warning_message.lineno),
                message=str(warning_message.message),
            )
        )

    def pytest_sessionfinish(self, session: pytest.Session) -> None:
        """Mark session as failed if expired deprecations were encountered"""
        if self.expired_warnings_count > 0:
            # Mark the session as failed
            session.exitstatus = pytest.ExitCode.TESTS_FAILED

    def pytest_terminal_summary(
        self, terminalreporter: pytest.TerminalReporter, config: pytest.Config
    ) -> None:
        if self.show_github_annotations:
            self._output_github_annotations(terminalreporter)

    def _output_github_annotations(
        self, terminalreporter: pytest.TerminalReporter
    ) -> None:
        """Output GitHub annotations to stdout."""

        for annotation in self.github_annotations:
            # GitHub Actions annotation format
            terminalreporter.write_line(
                f"::{annotation.type} file={annotation.file},line={annotation.line},"
                f"title=deprecation::{annotation.message}"
            )


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add deprecator-specific command line options."""
    group = parser.getgroup("deprecator")
    group.addoption(
        "--deprecator-error",
        action="store_true",
        default=False,
        help="Convert expired deprecation warnings to errors",
    )
    group.addoption(
        "--deprecator-github-annotations",
        action="store_true",
        default=False,
        help="Output deprecation warnings as GitHub Actions annotations",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Register the deprecator plugin and configure warning handling."""
    plugin = DeprecatorPlugin(
        show_github_annotations=config.getoption("--deprecator-github-annotations"),
    )
    config.pluginmanager.register(plugin, "deprecator-instance")


def pytest_runtest_setup(item: pytest.Item) -> None:
    """Apply warning filters before each test if --deprecator-error is set."""
    if item.config.getoption("--deprecator-error"):
        import warnings

        warnings.filterwarnings(
            "error",
            category=PerPackageExpiredDeprecationWarning,
        )


def pytest_unconfigure(config: pytest.Config) -> None:
    """Unregister the deprecator plugin."""
    plugin = config.pluginmanager.getplugin("deprecator-instance")
    if plugin:
        config.pluginmanager.unregister(plugin)
