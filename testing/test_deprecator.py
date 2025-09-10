from __future__ import annotations

import pytest
from conftest import TestVersions, get_test_deprecator
from packaging.version import Version

from deprecator._deprecator import Deprecator
from deprecator._warnings import (
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
    category = deprecator._get_category(gone_in, warn_in)
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
