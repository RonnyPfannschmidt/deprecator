import pytest
from packaging.version import Version

from deprecator._deprecator import Deprecator
from deprecator._warnings import (
    PerPackageDeprecationWarning,
    PerPackageExpiredDeprecationWarning,
    PerPackagePendingDeprecationWarning,
)

CURRENT_VERSION = Version("0.1.0")

PAST_VERSION = Version("0.0.1")

FUTURE_VERSION = Version("0.2.0")


@pytest.fixture
def deprecator() -> Deprecator:
    PendingDeprecationWarning, DeprecationWarning, DeprecationError = (
        Deprecator._define_categories("deprecator_test")
    )
    return Deprecator(
        "deprecator_test",
        CURRENT_VERSION,
        pending=PendingDeprecationWarning,
        deprecation=DeprecationWarning,
        deprecation_error=DeprecationError,
    )


def test_deprecator_make_definitions(deprecator: Deprecator) -> None:
    warning = deprecator.define(
        "test", gone_in=FUTURE_VERSION, warn_in=PAST_VERSION, replace_with="replacement"
    )
    assert isinstance(warning, DeprecationWarning)
    text = str(warning)
    # TODO: reassert
    assert "test" in text
    assert "replacement" in text
    assert "a replacement might be" in text

    warning = deprecator.define("test", gone_in=FUTURE_VERSION, warn_in=PAST_VERSION)
    assert isinstance(warning, DeprecationWarning)
    text = str(warning)
    assert "test" in text
    assert "a replacement might be" not in text


def test_deprecator_define_error(deprecator: Deprecator) -> None:
    with pytest.raises(
        ValueError, match="gone_in must be greater than or equal to warn_in"
    ):
        deprecator.define("test", gone_in=PAST_VERSION, warn_in=FUTURE_VERSION)


@pytest.mark.parametrize(
    ("gone_in", "warn_in", "expected_category"),
    [
        (FUTURE_VERSION, PAST_VERSION, PerPackageDeprecationWarning),
        (FUTURE_VERSION, FUTURE_VERSION, PerPackagePendingDeprecationWarning),
        (PAST_VERSION, CURRENT_VERSION, PerPackageExpiredDeprecationWarning),
        (CURRENT_VERSION, CURRENT_VERSION, PerPackageExpiredDeprecationWarning),
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
        (None, CURRENT_VERSION),
        (FUTURE_VERSION, FUTURE_VERSION),
        (PAST_VERSION, PAST_VERSION),
        (str(PAST_VERSION), PAST_VERSION),
        (str(FUTURE_VERSION), FUTURE_VERSION),
    ],
)
def test_deprecator_parse_version(
    deprecator: Deprecator, version: Version | str | None, expected_version: Version
) -> None:
    assert deprecator._parse_version(version) == expected_version
