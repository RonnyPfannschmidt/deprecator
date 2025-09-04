from __future__ import annotations

import importlib.metadata
from typing import TYPE_CHECKING, TypedDict

from packaging.version import Version

from ._types import PackageName
from ._warnings import (
    DeprecatorWarningMixing,
    PerPackageDeprecationWarning,
    PerPackageExpiredDeprecationWarning,
    PerPackagePendingDeprecationWarning,
)

if TYPE_CHECKING:
    from ._registry import DeprecatorRegistry


class DeprecationInfo(TypedDict):
    """Information about a tracked deprecation."""

    warning: DeprecatorWarningMixing
    importable_name: str | None


class Deprecator:
    name: PackageName
    current_version: Version

    PendingDeprecationWarning: type[PerPackagePendingDeprecationWarning]
    DeprecationWarning: type[PerPackageDeprecationWarning]
    DeprecationError: type[PerPackageExpiredDeprecationWarning]

    def __init__(
        self,
        name: PackageName,
        current_version: Version,
        *,
        pending: type[PerPackagePendingDeprecationWarning],
        deprecation: type[PerPackageDeprecationWarning],
        deprecation_error: type[PerPackageExpiredDeprecationWarning],
        registry: DeprecatorRegistry | None = None,
    ) -> None:
        self.name = name
        self.current_version = current_version
        self.PendingDeprecationWarning = pending
        self.DeprecationWarning = deprecation
        self.DeprecationError = deprecation_error
        self._registry = registry
        # Track deprecations in the deprecator itself
        self._tracked_deprecations: list[DeprecationInfo] = []

    @classmethod
    def _define_categories(
        cls, package_name: PackageName
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
    def for_package(
        cls, package_name: PackageName, _package_version: Version | None = None
    ) -> Deprecator:
        package_version = _package_version or Version(
            importlib.metadata.version(package_name)
        )

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
        *,
        importable_name: str | None = None,
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
        warning = category(message, gone_in, warn_in, self.current_version)

        # Track the deprecation locally
        self._tracked_deprecations.append(
            DeprecationInfo(warning=warning, importable_name=importable_name)
        )

        return warning

    def get_tracked_deprecations(self) -> list[DeprecationInfo]:
        """Get all tracked deprecations for this deprecator.

        Returns:
            List of deprecation information for this deprecator
        """
        return self._tracked_deprecations.copy()
