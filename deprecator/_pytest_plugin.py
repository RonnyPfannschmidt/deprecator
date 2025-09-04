"""Pytest plugin for deprecator to convert expired deprecations to errors."""

from __future__ import annotations

import warnings
from typing import TYPE_CHECKING

import pytest

from ._warnings import PerPackageExpiredDeprecationWarning

if TYPE_CHECKING:
    pass


class DeprecatorPlugin:
    """Plugin that handles expired deprecation warnings."""

    def __init__(self) -> None:
        self.expired_warnings_count = 0

    def pytest_warning_recorded(
        self,
        warning_message: warnings.WarningMessage,
        when: str,
        nodeid: str,
        location: tuple[str, int, str] | None,
    ) -> None:
        """Track expired deprecation warnings."""
        if isinstance(warning_message.message, PerPackageExpiredDeprecationWarning):
            self.expired_warnings_count += 1

    def pytest_sessionfinish(self, session: pytest.Session) -> None:
        """Mark session as failed if expired deprecations were encountered."""
        if self.expired_warnings_count > 0:
            # Mark the session as failed
            session.exitstatus = pytest.ExitCode.TESTS_FAILED


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add deprecator-specific command line options."""
    group = parser.getgroup("deprecator")
    group.addoption(
        "--deprecator-error",
        action="store_true",
        default=False,
        help="Convert expired deprecation warnings to errors",
    )


def pytest_configure(config: pytest.Config) -> None:
    """Register the deprecator plugin and configure warning handling."""
    plugin = DeprecatorPlugin()
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
