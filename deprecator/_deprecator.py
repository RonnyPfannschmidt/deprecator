from __future__ import annotations

import importlib.metadata
from collections.abc import Iterator
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
    ExpiredDeprecationWarning: type[PerPackageExpiredDeprecationWarning]

    def __init__(
        self,
        name: PackageName | str,
        current_version: Version,
        *,
        pending: type[PerPackagePendingDeprecationWarning],
        deprecation: type[PerPackageDeprecationWarning],
        expired_warning: type[PerPackageExpiredDeprecationWarning],
        registry: DeprecatorRegistry | None = None,
    ) -> None:
        self.name = PackageName(name)
        self.current_version = current_version
        self.PendingDeprecationWarning = pending
        self.DeprecationWarning = deprecation
        self.ExpiredDeprecationWarning = expired_warning
        self._registry = registry
        # Track deprecations in the deprecator itself
        self._tracked_deprecations: list[DeprecationInfo] = []

    @classmethod
    def _create_warning_classes(
        cls, package_name: PackageName | str, current_version: Version
    ) -> tuple[
        type[PerPackagePendingDeprecationWarning],
        type[PerPackageDeprecationWarning],
        type[PerPackageExpiredDeprecationWarning],
    ]:
        pkg_name = PackageName(package_name)

        # Create the warning classes with ClassVars set
        PendingDeprecationWarning = type(
            "PendingDeprecationWarning",
            (PerPackagePendingDeprecationWarning,),
            {
                "package_name": pkg_name,
                "current_version": current_version,
            },
        )

        DeprecationWarning = type(
            "DeprecationWarning",
            (PerPackageDeprecationWarning,),
            {
                "package_name": pkg_name,
                "current_version": current_version,
            },
        )

        DeprecationError = type(
            "DeprecationError",
            (PerPackageExpiredDeprecationWarning,),
            {
                "package_name": pkg_name,
                "current_version": current_version,
            },
        )

        return PendingDeprecationWarning, DeprecationWarning, DeprecationError

    @classmethod
    def for_package(
        cls, package_name: PackageName | str, _package_version: Version | None = None
    ) -> Deprecator:
        pkg_name = PackageName(package_name)
        package_version = _package_version or Version(
            importlib.metadata.version(pkg_name)
        )

        PendingDeprecationWarning, DeprecationWarning, DeprecationError = (
            cls._create_warning_classes(pkg_name, package_version)
        )

        return Deprecator(
            pkg_name,
            package_version,
            pending=PendingDeprecationWarning,
            deprecation=DeprecationWarning,
            expired_warning=DeprecationError,
        )

    def _get_warning_class(
        self, gone_in: Version, warn_in: Version
    ) -> type[
        PerPackageDeprecationWarning
        | PerPackageExpiredDeprecationWarning
        | PerPackagePendingDeprecationWarning
    ]:
        if gone_in <= self.current_version:
            return self.ExpiredDeprecationWarning
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

        base_category = self._get_warning_class(gone_in, warn_in)

        # Create a specific warning class for this deprecation with its own ClassVars
        # Use the base category name to maintain expected class names
        class_name = base_category.__name__
        SpecificWarning = type(
            class_name,
            (base_category,),
            {
                "gone_in": gone_in,
                "warn_in": warn_in,
                # current_version is already set by the base class
            },
        )

        warning = SpecificWarning(message)

        # Track the deprecation locally
        self._tracked_deprecations.append(
            DeprecationInfo(warning=warning, importable_name=importable_name)
        )

        return warning  # type: ignore[no-any-return]

    def get_tracked_deprecations(self) -> list[DeprecationInfo]:
        """Get all tracked deprecations for this deprecator.

        Returns:
            List of deprecation information for this deprecator
        """
        return self._tracked_deprecations.copy()

    def __iter__(self) -> Iterator[DeprecatorWarningMixing]:
        """Iterate over the tracked deprecation warnings."""
        return (info["warning"] for info in self._tracked_deprecations)
