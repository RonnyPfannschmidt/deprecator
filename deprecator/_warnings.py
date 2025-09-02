from __future__ import annotations

from typing import ClassVar

from packaging.version import Version


class DeprecatorWarningMixing(Warning):
    package_name: ClassVar[str]
    gone_in: Version
    warn_in: Version
    current_version: Version

    def __init_subclass__(cls, *, package_name: str | None = None) -> None:
        if package_name is not None:
            cls.package_name = package_name

    def __init__(
        self,
        msg: str,
        gone_in: Version,
        warn_in: Version,
        current_version: Version,
    ) -> None:
        self.gone_in = gone_in
        self.warn_in = warn_in
        self.current_version = current_version
        super().__init__(msg)


class PerPackagePendingDeprecationWarning(
    DeprecatorWarningMixing, PendingDeprecationWarning
):
    """
    category for deprecations that are pending and we want to warn about in tests
    """


class PerPackageDeprecationWarning(DeprecatorWarningMixing, DeprecationWarning):
    """
    category for deprecations we want to warn about
    """


class PerPackageExpiredDeprecationWarning(DeprecatorWarningMixing, DeprecationWarning):
    """
    category for deprecations to trigger errors for unless explicitly suppressed
    """