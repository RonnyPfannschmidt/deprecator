from __future__ import annotations

import importlib.metadata
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


class Deprecator:
    package_name: str
    current_version: Version

    PendingDeprecationWarning: type[PerPackagePendingDeprecationWarning]
    DeprecationWarning: type[PerPackageDeprecationWarning]
    DeprecationError: type[PerPackageExpiredDeprecationWarning]

    def __init__(
        self,
        package_name: str,
        current_version: Version,
        *,
        pending: type[PerPackagePendingDeprecationWarning],
        deprecation: type[PerPackageDeprecationWarning],
        deprecation_error: type[PerPackageExpiredDeprecationWarning],
    ) -> None:
        self.package_name = package_name
        self.current_version = current_version
        self.PendingDeprecationWarning = pending
        self.DeprecationWarning = deprecation
        self.DeprecationError = deprecation_error

    @classmethod
    def _define_categories(
        cls, package_name: str
    ) -> tuple[
        type[PerPackagePendingDeprecationWarning],
        type[PerPackageDeprecationWarning],
        type[PerPackageExpiredDeprecationWarning],
    ]:
        class PendingDeprecationWarning(
            PerPackagePendingDeprecationWarning, package_name=package_name
        ):
            pass

        class DeprecationWarning(
            PerPackageDeprecationWarning, package_name=package_name
        ):
            pass

        class DeprecationError(
            PerPackageExpiredDeprecationWarning, package_name=package_name
        ):
            pass

        return PendingDeprecationWarning, DeprecationWarning, DeprecationError

    @classmethod
    def for_package(cls, package_name: str) -> Deprecator:
        package_version = Version(importlib.metadata.version(package_name))

        PendingDeprecationWarning, DeprecationWarning, DeprecationError = (
            cls._define_categories(package_name)
        )

        return Deprecator(
            package_name,
            package_version,
            pending=PendingDeprecationWarning,
            deprecation=DeprecationWarning,
            deprecation_error=DeprecationError,
        )

    def _get_category(
        self, gone_in: Version, warn_in: Version
    ) -> type[
        PerPackageDeprecationWarning
        | PerPackageExpiredDeprecationWarning
        | PerPackagePendingDeprecationWarning
    ]:
        if gone_in <= self.current_version:
            return self.DeprecationError
        if warn_in <= self.current_version:
            return self.DeprecationWarning
        return self.PendingDeprecationWarning

    def _parse_version(self, version: Version | str | None) -> Version:
        if version is None:
            return self.current_version
        if isinstance(version, Version):
            return version
        return Version(version)

    def define(
        self,
        message: str,
        gone_in: Version | str | None = None,
        warn_in: Version | str | None = None,
        replace_with: object | None = None,
    ) -> (
        PerPackageDeprecationWarning
        | PerPackageExpiredDeprecationWarning
        | PerPackagePendingDeprecationWarning
    ):
        gone_in = self._parse_version(gone_in)
        warn_in = self._parse_version(warn_in)

        if replace_with is not None:
            message = f"{message}\n\na replacement might be: {replace_with}"

        if gone_in < warn_in:
            raise ValueError("gone_in must be greater than or equal to warn_in")

        category = self._get_category(gone_in, warn_in)
        return category(message, gone_in, warn_in, self.current_version)
