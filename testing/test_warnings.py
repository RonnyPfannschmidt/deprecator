"""Tests for warning emission functionality."""

from __future__ import annotations

import warnings

import pytest
from packaging.version import Version

from deprecator._deprecator import Deprecator


@pytest.fixture
def deprecator() -> Deprecator:
    """Fixture providing a test deprecator."""
    return Deprecator.for_package("test_warnings", _package_version=Version("1.0.0"))


def test_warn_default_stacklevel(deprecator: Deprecator) -> None:
    """Test that warn() works with default stacklevel."""
    warning = deprecator.define("test warning", warn_in="0.5.0", gone_in="2.0.0")

    with warnings.catch_warnings(record=True) as warning_list:
        warnings.simplefilter("always")
        warning.warn()

    assert len(warning_list) == 1
    caught_warning = warning_list[0]
    assert isinstance(caught_warning.message, type(warning))
    assert str(caught_warning.message) == "test warning"
    assert issubclass(caught_warning.category, type(warning))


def test_warn_custom_stacklevel(deprecator: Deprecator) -> None:
    """Test that warn() works with custom stacklevel."""
    warning = deprecator.define("test warning", warn_in="0.5.0", gone_in="2.0.0")

    def wrapper_function() -> None:
        warning.warn(stacklevel=3)  # Skip this wrapper

    with warnings.catch_warnings(record=True) as warning_list:
        warnings.simplefilter("always")
        wrapper_function()

    assert len(warning_list) == 1
    caught_warning = warning_list[0]
    assert isinstance(caught_warning.message, type(warning))
    assert str(caught_warning.message) == "test warning"


def test_warn_explicit_with_filename_lineno(deprecator: Deprecator) -> None:
    """Test that warn_explicit() works with filename and lineno."""
    warning = deprecator.define(
        "explicit test warning", warn_in="0.5.0", gone_in="2.0.0"
    )

    with warnings.catch_warnings(record=True) as warning_list:
        warnings.simplefilter("always")
        warning.warn_explicit("test_file.py", 42)

    assert len(warning_list) == 1
    caught_warning = warning_list[0]
    assert str(caught_warning.message) == "explicit test warning"
    assert caught_warning.filename == "test_file.py"
    assert caught_warning.lineno == 42
    assert caught_warning.category is DeprecationWarning  # Should use stdlib category


def test_warn_explicit_with_module(deprecator: Deprecator) -> None:
    """Test that warn_explicit() works with module name."""
    warning = deprecator.define("module test warning", warn_in="0.5.0", gone_in="2.0.0")

    with warnings.catch_warnings(record=True) as warning_list:
        warnings.simplefilter("always")
        warning.warn_explicit("test_file.py", 100, module="test_module")

    assert len(warning_list) == 1
    caught_warning = warning_list[0]
    assert str(caught_warning.message) == "module test warning"
    assert caught_warning.filename == "test_file.py"
    assert caught_warning.lineno == 100
    assert caught_warning.category is DeprecationWarning


def test_different_warning_categories(deprecator: Deprecator) -> None:
    """Test that different warning categories are emitted correctly."""
    # Pending (future warning)
    pending_warning = deprecator.define(
        "pending warning", warn_in="1.5.0", gone_in="2.0.0"
    )

    # Active (current warning)
    active_warning = deprecator.define(
        "active warning", warn_in="0.5.0", gone_in="2.0.0"
    )

    with warnings.catch_warnings(record=True) as warning_list:
        warnings.simplefilter("always")
        pending_warning.warn()
        active_warning.warn()

    assert len(warning_list) == 2

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
    deprecator = Deprecator.for_package(
        "test_instance", _package_version=Version("1.0.0")
    )
    warning = deprecator.define("instance test", warn_in="0.5.0", gone_in="2.0.0")

    # Check that methods exist and are callable
    assert hasattr(warning, "warn")
    assert callable(warning.warn)
    assert hasattr(warning, "warn_explicit")
    assert callable(warning.warn_explicit)


def test_warn_explicit_pending_warning(deprecator: Deprecator) -> None:
    """Test that warn_explicit() works with PendingDeprecationWarning."""
    # Create a pending warning (warn_in is in the future)
    pending_warning = deprecator.define(
        "pending test warning", warn_in="1.5.0", gone_in="2.0.0"
    )

    with warnings.catch_warnings(record=True) as warning_list:
        warnings.simplefilter("always")
        pending_warning.warn_explicit("test_file.py", 42)

    assert len(warning_list) == 1
    caught_warning = warning_list[0]
    assert str(caught_warning.message) == "pending test warning"
    assert caught_warning.category is PendingDeprecationWarning


def test_warning_with_replacement_message() -> None:
    """Test that warnings with replacement show proper message."""
    deprecator = Deprecator.for_package(
        "test_replace", _package_version=Version("1.0.0")
    )
    warning = deprecator.define(
        "old function is deprecated",
        warn_in="0.5.0",
        gone_in="2.0.0",
        replace_with="new_function()",
    )

    with warnings.catch_warnings(record=True) as warning_list:
        warnings.simplefilter("always")
        warning.warn()

    assert len(warning_list) == 1
    caught_warning = warning_list[0]
    message = str(caught_warning.message)
    assert "old function is deprecated" in message
    assert "a replacement might be: new_function()" in message
