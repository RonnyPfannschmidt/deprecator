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
    ("version", "expected_version"),
    [
        (None, TestVersions.CURRENT),
        (TestVersions.FUTURE, TestVersions.FUTURE),
        (TestVersions.PAST, TestVersions.PAST),
        (str(TestVersions.PAST), TestVersions.PAST),
        (str(TestVersions.FUTURE), TestVersions.FUTURE),
    ],
)
def test_deprecator_parse_version(
    deprecator: Deprecator, version: Version | str | None, expected_version: Version
) -> None:
    assert deprecator._parse_version(version) == expected_version


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
    with pytest.raises((InvalidVersion, ValueError)) as exc_info:
        deprecator.define(
            "Test deprecation",
            gone_in="not.a.valid.version",
            warn_in="1.0.0",
        )
    # Should have helpful error message
    assert "version" in str(exc_info.value).lower()


def test_define_invalid_warn_in_format(deprecator: Deprecator) -> None:
    """Test that define() validates warn_in version format."""
    with pytest.raises((InvalidVersion, ValueError)) as exc_info:
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
