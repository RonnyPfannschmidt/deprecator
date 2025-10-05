"""Tests for warning emission functionality."""

from __future__ import annotations

import sys
from types import ModuleType

import pytest
from conftest import TestVersions, assert_warnings, get_test_deprecator
from packaging.version import Version

from deprecator._deprecator import Deprecator
from deprecator._registry import default_registry
from deprecator._warnings import create_package_warning_classes


def test_warn_default_stacklevel(test_deprecator: Deprecator) -> None:
    """Test that warn() works with default stacklevel."""
    warning = test_deprecator.define(
        "test warning", warn_in=TestVersions.PAST, gone_in=TestVersions.FUTURE
    )

    with assert_warnings(1, type(warning)) as warning_list:
        warning.warn()

    caught_warning = warning_list[0]
    assert isinstance(caught_warning.message, type(warning))
    assert str(caught_warning.message) == "test warning"


def test_warn_custom_stacklevel(test_deprecator: Deprecator) -> None:
    """Test that warn() works with custom stacklevel."""
    warning = test_deprecator.define(
        "test warning", warn_in=TestVersions.PAST, gone_in=TestVersions.FUTURE
    )

    def wrapper_function() -> None:
        warning.warn(stacklevel=3)  # Skip this wrapper

    with assert_warnings(1, type(warning)) as warning_list:
        wrapper_function()

    caught_warning = warning_list[0]
    assert isinstance(caught_warning.message, type(warning))
    assert str(caught_warning.message) == "test warning"


def test_warn_explicit_with_filename_lineno(test_deprecator: Deprecator) -> None:
    """Test that warn_explicit() works with filename and lineno."""
    warning = test_deprecator.define(
        "explicit test warning", warn_in=TestVersions.PAST, gone_in=TestVersions.FUTURE
    )

    with assert_warnings(1, DeprecationWarning) as warning_list:
        warning.warn_explicit("test_file.py", 42)

    caught_warning = warning_list[0]
    assert str(caught_warning.message) == "explicit test warning"
    assert caught_warning.filename == "test_file.py"
    assert caught_warning.lineno == 42
    assert caught_warning.category is DeprecationWarning  # Should use stdlib category


def test_warn_explicit_with_module(test_deprecator: Deprecator) -> None:
    """Test that warn_explicit() works with module name."""
    warning = test_deprecator.define(
        "module test warning", warn_in=TestVersions.PAST, gone_in=TestVersions.FUTURE
    )

    with assert_warnings(1, DeprecationWarning) as warning_list:
        warning.warn_explicit("test_file.py", 100, module="test_module")

    caught_warning = warning_list[0]
    assert str(caught_warning.message) == "module test warning"
    assert caught_warning.filename == "test_file.py"
    assert caught_warning.lineno == 100
    assert caught_warning.category is DeprecationWarning


def test_different_warning_categories(test_deprecator: Deprecator) -> None:
    """Test that different warning categories are emitted correctly."""
    # Pending (future warning)
    pending_warning = test_deprecator.define(
        "pending warning", warn_in="1.5.0", gone_in=TestVersions.FUTURE
    )

    # Active (current warning)
    active_warning = test_deprecator.define(
        "active warning", warn_in=TestVersions.PAST, gone_in=TestVersions.FUTURE
    )

    with assert_warnings(2, Warning) as warning_list:
        pending_warning.warn()
        active_warning.warn()

    # Check pending warning
    pending_caught = warning_list[0]
    assert "PendingDeprecationWarning" in str(type(pending_caught.message))
    assert str(pending_caught.message) == "pending warning"

    # Check active warning
    active_caught = warning_list[1]
    assert "DeprecationWarning" in str(type(active_caught.message))
    assert str(active_caught.message) == "active warning"


def test_warn_methods_are_instance_methods() -> None:
    """Test that warn methods are available on warning instances."""
    pending, deprecation, expired_warning = create_package_warning_classes(
        "test_instance", Version("1.0.0")
    )
    deprecator = Deprecator(
        "test_instance",
        Version("1.0.0"),
        pending=pending,
        deprecation=deprecation,
        expired_warning=expired_warning,
        registry=default_registry,
    )
    warning = deprecator.define(
        "instance test", warn_in=TestVersions.PAST, gone_in=TestVersions.FUTURE
    )

    # Check that methods exist and are callable
    assert hasattr(warning, "warn")
    assert callable(warning.warn)
    assert hasattr(warning, "warn_explicit")
    assert callable(warning.warn_explicit)


def test_warn_explicit_pending_warning(test_deprecator: Deprecator) -> None:
    """Test that warn_explicit() works with PendingDeprecationWarning."""
    # Create a pending warning (warn_in is in the future)
    pending_warning = test_deprecator.define(
        "pending test warning", warn_in="1.5.0", gone_in=TestVersions.FUTURE
    )

    with assert_warnings(1, PendingDeprecationWarning) as warning_list:
        pending_warning.warn_explicit("test_file.py", 42)

    caught_warning = warning_list[0]
    assert str(caught_warning.message) == "pending test warning"
    assert caught_warning.category is PendingDeprecationWarning


def test_warning_with_replacement_message() -> None:
    """Test that warnings with replacement show proper message."""
    from conftest import get_test_deprecator

    deprecator = get_test_deprecator("test_replace", "1.0.0")
    warning = deprecator.define(
        "old function is deprecated",
        warn_in="0.5.0",
        gone_in="2.0.0",
        replace_with="new_function()",
    )

    with assert_warnings(1, type(warning)) as warning_list:
        warning.warn()

    caught_warning = warning_list[0]
    message = str(caught_warning.message)
    assert "old function is deprecated" in message
    assert "a replacement might be: new_function()" in message


# Tests for warning __repr__ from test_improvements.py
def test_warning_instance_repr() -> None:
    """Test that warning instances have useful __repr__ showing version info."""
    deprecator = get_test_deprecator(":test_package", TestVersions.CURRENT)
    warning = deprecator.define(
        "Test deprecation",
        gone_in=TestVersions.FUTURE,
        warn_in=TestVersions.PAST,
    )
    repr_str = repr(warning)

    # Should show version information
    assert "gone_in" in repr_str or str(TestVersions.FUTURE) in repr_str
    assert "warn_in" in repr_str or str(TestVersions.PAST) in repr_str


def test_warning_class_repr() -> None:
    """Test that warning classes show their categorization info."""
    deprecator = get_test_deprecator(":test_package", TestVersions.CURRENT)
    warning = deprecator.define(
        "Test deprecation",
        gone_in=TestVersions.FUTURE,
        warn_in=TestVersions.PAST,
    )
    class_repr = repr(type(warning))

    # Class repr should indicate it's a deprecation warning type
    assert "DeprecationWarning" in class_repr


# Performance and caching tests from test_improvements.py
def test_find_warning_in_modules_function() -> None:
    """Test the standalone find_warning_in_modules function."""
    from deprecator._warnings import find_warning_in_modules

    deprecator = get_test_deprecator(":test_package", TestVersions.CURRENT)
    warning = deprecator.define(
        "Test deprecation",
        gone_in=TestVersions.FUTURE,
        warn_in=TestVersions.PAST,
    )

    # Create a mock module dict
    mock_module = ModuleType("test_module")
    mock_module.test_warning = warning  # type: ignore[attr-defined]
    test_modules: dict[str, ModuleType | None] = {"test_module": mock_module}

    # Test with custom modules dict
    name = find_warning_in_modules(warning, test_modules)
    assert name == "test_module.test_warning"

    # Test with empty modules dict
    assert find_warning_in_modules(warning, {}) is None

    # Test with None modules (uses sys.modules)
    sys.modules[__name__].__dict__["test_warning_in_sys"] = warning
    name = find_warning_in_modules(warning)
    assert name is not None
    assert "test_warning_in_sys" in name


# These tests have been replaced by test_importable_name_cached_property
# which tests the new cached property implementation


def test_importable_name_cached_property() -> None:
    """Test the importable_name cached property."""
    deprecator = get_test_deprecator(":test_package", TestVersions.CURRENT)
    warning = deprecator.define(
        "Test deprecation",
        gone_in=TestVersions.FUTURE,
        warn_in=TestVersions.PAST,
    )

    # Add to module for finding
    sys.modules[__name__].__dict__["test_cached_prop"] = warning

    # First access should find and cache
    name1 = warning.importable_name
    assert name1 is not None
    assert "test_cached_prop" in name1

    # Remove from module
    del sys.modules[__name__].__dict__["test_cached_prop"]

    # Second access should return cached value
    name2 = warning.importable_name
    assert name2 == name1

    # Verify it's a cached_property instance
    from functools import cached_property

    assert isinstance(type(warning).importable_name, cached_property)


# Edge case test for warn_explicit
def test_warning_warn_explicit_with_edge_cases() -> None:
    """Test the warn_explicit method with various inputs."""
    deprecator = get_test_deprecator(":test_package", TestVersions.CURRENT)
    warning = deprecator.define(
        "Test deprecation",
        gone_in=TestVersions.FUTURE,
        warn_in=TestVersions.PAST,
    )

    # Should handle warn_explicit without errors
    with pytest.warns(DeprecationWarning):
        warning.warn_explicit(filename="test_file.py", lineno=42, module="test_module")

    # Should handle None module
    with pytest.warns(DeprecationWarning):
        warning.warn_explicit(filename="test_file.py", lineno=42, module=None)


# ClassVar initialization test from test_improvements.py
def test_class_var_initialization() -> None:
    """Test that ClassVars are properly initialized on warning classes."""
    deprecator = get_test_deprecator(":test_package", TestVersions.CURRENT)
    warning = deprecator.define(
        "Test deprecation",
        gone_in=TestVersions.FUTURE,
        warn_in=TestVersions.PAST,
    )

    # Check ClassVars are set
    assert hasattr(type(warning), "gone_in")
    assert hasattr(type(warning), "warn_in")
    assert hasattr(type(warning), "current_version")
    assert hasattr(type(warning), "package_name")

    # Check values
    assert type(warning).gone_in == TestVersions.FUTURE
    assert type(warning).warn_in == TestVersions.PAST
    assert type(warning).current_version == TestVersions.CURRENT
