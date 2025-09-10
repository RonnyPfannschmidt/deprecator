"""Shared test fixtures and utilities for the deprecator test suite."""

from __future__ import annotations

import warnings
from collections.abc import Callable, Generator
from contextlib import contextmanager

import pytest
from packaging.version import Version
from rich.console import Console

from deprecator._deprecator import Deprecator
from deprecator._registry import DeprecatorRegistry, default_registry
from deprecator._types import PackageName
from deprecator._warnings import (
    PerPackageDeprecationWarning,
    PerPackageExpiredDeprecationWarning,
    PerPackagePendingDeprecationWarning,
)


# Standard test version constants
class TestVersions:
    """Standard version constants for testing."""

    PAST = Version("0.5.0")
    CURRENT = Version("1.0.0")
    FUTURE = Version("2.0.0")
    FAR_FUTURE = Version("3.0.0")


@pytest.fixture
def test_deprecator() -> Deprecator:
    """Standard test deprecator fixture with current version."""
    return Deprecator("test-package", TestVersions.CURRENT, registry=default_registry)


@pytest.fixture
def test_registry() -> DeprecatorRegistry:
    """Standard test registry fixture."""
    return DeprecatorRegistry(framework=PackageName("test"))


@pytest.fixture
def empty_registry() -> DeprecatorRegistry:
    """Empty test registry fixture."""
    return DeprecatorRegistry(framework=PackageName("test"))


@pytest.fixture
def populated_test_registry() -> DeprecatorRegistry:
    """Test registry with sample deprecators already created."""
    registry = DeprecatorRegistry(framework=PackageName("test"))

    # Add a deprecator with active deprecations
    dep1 = registry.for_package(":test_package", _version=TestVersions.FUTURE)
    dep1.define("Test deprecation message", gone_in="3.0.0", warn_in="1.5.0")

    # Add another deprecator with active deprecation
    dep2 = registry.for_package(":another_package", _version=Version("1.5.0"))
    dep2.define("Another deprecation", gone_in="2.0.0", warn_in="1.0.0")

    return registry


@contextmanager
def assert_warnings(
    expected_count: int = 1,
    expected_category: type[Warning] = DeprecationWarning,
) -> Generator[list[warnings.WarningMessage], None, None]:
    """Context manager for asserting warnings.

    Args:
        expected_count: Expected number of warnings
        expected_category: Expected warning category

    Yields:
        List of captured warnings

    Example:
        with assert_warnings(1, DeprecationWarning) as warnings_list:
            deprecated_function()
        assert "deprecated" in str(warnings_list[0].message)
    """
    with warnings.catch_warnings(record=True) as warning_list:
        warnings.simplefilter("always")
        yield warning_list

    assert len(warning_list) == expected_count
    if expected_count > 0:
        assert issubclass(warning_list[0].category, expected_category)


def run_with_console_capture(
    action_func: Callable[..., None], *args: object, **kwargs: object
) -> str:
    """Run a function with a console in capture mode and return the captured output.

    Convention: Functions should accept console as a keyword argument named 'console'.

    Args:
        action_func: Function that accepts console=Console() and returns None
        *args: Positional arguments to pass to action_func
        **kwargs: Keyword arguments to pass to action_func

    Returns:
        The captured console output as a string

    Example:
        output = run_with_console_capture(
            print_deprecations_table,
            deprecator,
            warning_types=types
        )
    """
    console = Console(width=120)

    with console.capture() as capture:
        kwargs["console"] = console
        action_func(*args, **kwargs)

    return str(capture.get())


class DeprecationTestHelper:
    """Helper class for common deprecation testing patterns."""

    @staticmethod
    def create_pending_deprecation(
        deprecator: Deprecator,
        message: str = "This is pending",
        warn_in: Version | str = TestVersions.FUTURE,
        gone_in: Version | str = TestVersions.FAR_FUTURE,
    ) -> (
        PerPackageDeprecationWarning
        | PerPackageExpiredDeprecationWarning
        | PerPackagePendingDeprecationWarning
    ):
        """Create a pending deprecation warning."""
        return deprecator.define(message, warn_in=warn_in, gone_in=gone_in)

    @staticmethod
    def create_active_deprecation(
        deprecator: Deprecator,
        message: str = "This is active",
        warn_in: Version | str = TestVersions.PAST,
        gone_in: Version | str = TestVersions.FUTURE,
    ) -> (
        PerPackageDeprecationWarning
        | PerPackageExpiredDeprecationWarning
        | PerPackagePendingDeprecationWarning
    ):
        """Create an active deprecation warning."""
        return deprecator.define(message, warn_in=warn_in, gone_in=gone_in)

    @staticmethod
    def create_expired_deprecation(
        deprecator: Deprecator,
        message: str = "This is expired",
        warn_in: Version | str = TestVersions.PAST,
        gone_in: Version | str = TestVersions.CURRENT,
    ) -> (
        PerPackageDeprecationWarning
        | PerPackageExpiredDeprecationWarning
        | PerPackagePendingDeprecationWarning
    ):
        """Create an expired deprecation warning."""
        return deprecator.define(message, warn_in=warn_in, gone_in=gone_in)

    @staticmethod
    def create_deprecation_with_replacement(
        deprecator: Deprecator,
        message: str = "This has replacement",
        replacement: str = "new_function()",
        warn_in: Version | str = TestVersions.PAST,
        gone_in: Version | str = TestVersions.FUTURE,
    ) -> (
        PerPackageDeprecationWarning
        | PerPackageExpiredDeprecationWarning
        | PerPackagePendingDeprecationWarning
    ):
        """Create a deprecation warning with replacement."""
        return deprecator.define(
            message, warn_in=warn_in, gone_in=gone_in, replace_with=replacement
        )


def get_test_deprecator(name: str, version: str | Version) -> Deprecator:
    """Factory function for creating test deprecators with custom names/versions."""
    if isinstance(version, str):
        version = Version(version)
    return Deprecator(name, version, registry=default_registry)


def assert_console_output_contains(
    action_func: Callable[..., None],
    expected_texts: list[str],
    *args: object,
    **kwargs: object,
) -> str:
    """Helper to assert console output contains expected text.

    Convention: Functions should accept console as a keyword argument named 'console'.

    Args:
        action_func: Function that accepts console=Console() and returns None
        expected_texts: List of strings that should appear in output
        *args: Positional arguments to pass to action_func
        **kwargs: Keyword arguments to pass to action_func

    Returns:
        The captured output string

    Example:
        output = assert_console_output_contains(
            print_deprecations_table,
            ["Expected text 1", "Expected text 2"],
            deprecator,
            warning_types=types
        )
    """
    output = run_with_console_capture(action_func, *args, **kwargs)
    for expected_text in expected_texts:
        assert expected_text in output, (
            f"Expected '{expected_text}' not found in output"
        )

    return output


# Pytest plugin configuration for deprecator-specific testing
def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with deprecator-specific markers."""
    config.addinivalue_line(
        "markers", "deprecation: mark test as testing deprecation functionality"
    )
    config.addinivalue_line(
        "markers", "registry: mark test as testing registry functionality"
    )
    config.addinivalue_line(
        "markers", "warnings: mark test as testing warning emission"
    )
