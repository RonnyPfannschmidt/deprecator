"""Tests for warning emission functionality."""

from __future__ import annotations

from conftest import TestVersions, assert_warnings
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
