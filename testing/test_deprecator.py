from __future__ import annotations

import pytest
from conftest import TestVersions, get_test_deprecator
from packaging.version import InvalidVersion, Version

from deprecator._deprecator import Deprecator
from deprecator._warnings import (
    DeprecatorWarningMixing,
    PerPackageDeprecationWarning,
    PerPackageExpiredDeprecationWarning,
    PerPackagePendingDeprecationWarning,
)


@pytest.fixture
def deprecator() -> Deprecator:
    package_name = "deprecator_test"
    return get_test_deprecator(package_name, TestVersions.CURRENT)


def test_deprecator_make_definitions(deprecator: Deprecator) -> None:
    warning = deprecator.define(
        "test",
        gone_in=TestVersions.FUTURE,
        warn_in=TestVersions.PAST,
        replace_with="replacement",
    )
    assert isinstance(warning, DeprecationWarning)
    text = str(warning)
    # TODO: reassert
    assert "test" in text
    assert "replacement" in text
    assert "a replacement might be" in text

    warning = deprecator.define(
        "test", gone_in=TestVersions.FUTURE, warn_in=TestVersions.PAST
    )
    assert isinstance(warning, DeprecationWarning)
    text = str(warning)
    assert "test" in text
    assert "a replacement might be" not in text


def test_deprecator_define_error(deprecator: Deprecator) -> None:
    with pytest.raises(
        ValueError, match="gone_in must be greater than or equal to warn_in"
    ):
        deprecator.define(
            "test", gone_in=TestVersions.PAST, warn_in=TestVersions.FUTURE
        )


def test_deprecator_define_only_gone_in() -> None:
    """Test that defining with only gone_in works even when current_version > gone_in.

    When warn_in is not specified, it should default to min(current_version, gone_in).
    This ensures warn_in <= gone_in always holds.
    """
    # Create a deprecator with version higher than the gone_in we'll use
    deprecator = get_test_deprecator("test-package", "5.0.0")

    # This should NOT raise - warn_in defaults to min(5.0.0, 2.0.0) = 2.0.0
    warning = deprecator.define("test deprecation", gone_in="2.0.0")

    # Should be an expired warning since current_version (5.0.0) > gone_in (2.0.0)
    assert isinstance(warning, PerPackageExpiredDeprecationWarning)
    # warn_in should be gone_in (the minimum)
    assert warning.warn_in == Version("2.0.0")


def test_deprecator_define_only_gone_in_future() -> None:
    """Test warn_in defaults to current_version when gone_in is in the future."""
    deprecator = get_test_deprecator("test-package", "1.0.0")

    # gone_in is in the future, so warn_in defaults to current_version
    warning = deprecator.define("test deprecation", gone_in="3.0.0")

    # Should be a deprecation warning (not pending) since warn_in = current_version
    assert isinstance(warning, PerPackageDeprecationWarning)
    # warn_in should be current_version (the minimum)
    assert warning.warn_in == Version("1.0.0")


def test_deprecator_define_only_warn_in() -> None:
    """Test that defining with only warn_in works.

    When gone_in is not specified, it should default to current_version.
    """
    deprecator = get_test_deprecator("test-package", "2.0.0")

    # This should NOT raise - gone_in defaults to current_version
    warning = deprecator.define("test deprecation", warn_in="1.0.0")

    # Should be an expired warning since current_version == gone_in
    assert isinstance(warning, PerPackageExpiredDeprecationWarning)


@pytest.mark.parametrize(
    ("gone_in", "warn_in", "expected_category"),
    [
        (TestVersions.FUTURE, TestVersions.PAST, PerPackageDeprecationWarning),
        (TestVersions.FUTURE, TestVersions.FUTURE, PerPackagePendingDeprecationWarning),
        (TestVersions.PAST, TestVersions.CURRENT, PerPackageExpiredDeprecationWarning),
        (
            TestVersions.CURRENT,
            TestVersions.CURRENT,
            PerPackageExpiredDeprecationWarning,
        ),
    ],
)
def test_deprecator_category_specification(
    deprecator: Deprecator,
    gone_in: Version,
    warn_in: Version,
    expected_category: type[DeprecationWarning],
) -> None:
    category = deprecator._get_warning_class(gone_in, warn_in)
    assert issubclass(category, expected_category)


@pytest.mark.parametrize(
    ("version", "fallback", "expected_version"),
    [
        (None, TestVersions.CURRENT, TestVersions.CURRENT),
        (None, TestVersions.PAST, TestVersions.PAST),
        (TestVersions.FUTURE, TestVersions.CURRENT, TestVersions.FUTURE),
        (TestVersions.PAST, TestVersions.CURRENT, TestVersions.PAST),
        (str(TestVersions.PAST), TestVersions.CURRENT, TestVersions.PAST),
        (str(TestVersions.FUTURE), TestVersions.CURRENT, TestVersions.FUTURE),
    ],
)
def test_deprecator_parse_version(
    deprecator: Deprecator,
    version: Version | str | None,
    fallback: Version,
    expected_version: Version,
) -> None:
    assert deprecator._parse_version(version, fallback=fallback) == expected_version


def test_deprecator_repr() -> None:
    """Test that Deprecator has a useful __repr__ showing package and version."""
    deprecator = get_test_deprecator(":test_package", TestVersions.CURRENT)
    repr_str = repr(deprecator)

    # Should show package name and version
    assert ":test_package" in repr_str
    assert str(TestVersions.CURRENT) in repr_str
    # Should be in a standard format
    assert repr_str.startswith("<Deprecator")
    assert repr_str.endswith(">")


# Version validation tests from test_improvements.py
def test_define_invalid_version_format(deprecator: Deprecator) -> None:
    """Test that define() raises clear error on invalid version format."""
    # Specifically expect InvalidVersion from packaging
    with pytest.raises(InvalidVersion) as exc_info:
        deprecator.define(
            "Test deprecation",
            gone_in="not.a.valid.version",
            warn_in="1.0.0",
        )
    # Should have helpful error message about the invalid version
    error_msg = str(exc_info.value).lower()
    assert "not.a.valid.version" in error_msg or "invalid" in error_msg


def test_define_invalid_warn_in_format(deprecator: Deprecator) -> None:
    """Test that define() validates warn_in version format."""
    # Specifically expect InvalidVersion from packaging
    with pytest.raises(InvalidVersion) as exc_info:
        deprecator.define(
            "Test deprecation",
            gone_in="2.0.0",
            warn_in="invalid!version",
        )
    assert "version" in str(exc_info.value).lower()


def test_define_version_string_variations(deprecator: Deprecator) -> None:
    """Test that define() handles various valid version formats."""
    # Should handle different valid version formats
    test_cases = [
        ("2.0.0", "1.5.0"),  # Simple versions
        ("2.0.0rc1", "1.5.0b1"),  # Pre-release versions
        ("2.0.0.post1", "1.5.0"),  # Post-release versions
        ("2.0.0+local", "1.5.0"),  # Local versions
    ]

    for gone_in, warn_in in test_cases:
        warning = deprecator.define(
            f"Test with {gone_in}/{warn_in}",
            gone_in=gone_in,
            warn_in=warn_in,
        )
        assert warning is not None
        assert isinstance(warning, DeprecatorWarningMixing)


# Edge case tests from test_improvements.py
def test_define_with_current_version_as_gone_in() -> None:
    """Test define() behavior when gone_in equals current version."""
    current = Version("1.5.0")
    deprecator = get_test_deprecator(":test_package", current)

    warning = deprecator.define(
        "Test deprecation",
        gone_in=str(current),  # Same as current
        warn_in="1.0.0",
    )

    # Should be ExpiredDeprecationWarning since gone_in <= current
    base_classes = [c.__name__ for c in type(warning).__mro__]
    assert "PerPackageExpiredDeprecationWarning" in base_classes


def test_define_with_none_versions(deprecator: Deprecator) -> None:
    """Test that define() handles None versions correctly."""
    # None should default to current version
    warning = deprecator.define(
        "Test deprecation",
        gone_in=None,  # Should become current
        warn_in=None,  # Should become current
    )

    # Both at current version means expired
    base_classes = [c.__name__ for c in type(warning).__mro__]
    assert "PerPackageExpiredDeprecationWarning" in base_classes


# Tracking structure test from test_improvements.py
def test_deprecation_tracking_structure(deprecator: Deprecator) -> None:
    """Test that _tracked_deprecations maintains expected structure."""
    # Initially empty
    assert len(deprecator._tracked_deprecations) == 0

    # Add a deprecation with explicit importable_name
    warning1 = deprecator.define(
        "First deprecation",
        gone_in=TestVersions.FUTURE,
        warn_in=TestVersions.PAST,
        importable_name="test.first",
    )

    # Check structure - now we store warnings directly
    assert len(deprecator._tracked_deprecations) == 1
    tracked = deprecator._tracked_deprecations[0]
    assert tracked is warning1
    # The importable_name should be set directly on the warning
    assert warning1.importable_name == "test.first"

    # Add another without explicit importable_name
    warning2 = deprecator.define(
        "Second deprecation",
        gone_in=TestVersions.FUTURE,
        warn_in=TestVersions.CURRENT,
    )

    assert len(deprecator._tracked_deprecations) == 2
    assert deprecator._tracked_deprecations[1] is warning2
    # This one doesn't have an explicit name, so it would be None or dynamically found
    # The property will search for it when accessed
