from __future__ import annotations

import importlib.metadata
from collections.abc import Iterator
from typing import TYPE_CHECKING, cast

from packaging.version import Version

from ._types import PackageName
from ._warnings import (
    DeprecatorWarningMixing,
    PerPackageDeprecationWarning,
    PerPackageExpiredDeprecationWarning,
    PerPackagePendingDeprecationWarning,
    WarningClass,
    WarningInstance,
    create_package_warning_classes,
)

if TYPE_CHECKING:
    from ._registry import DeprecatorRegistry


class Deprecator:
    name: PackageName
    current_version: Version

    PendingDeprecationWarning: type[PerPackagePendingDeprecationWarning]
    DeprecationWarning: type[PerPackageDeprecationWarning]
    ExpiredDeprecationWarning: type[PerPackageExpiredDeprecationWarning]

    def __repr__(self) -> str:
        """Return a string representation of the Deprecator for debugging."""
        return f"<Deprecator '{self.name}' v{self.current_version}>"

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
        self._tracked_deprecations: list[DeprecatorWarningMixing] = []

    @classmethod
    def for_package(
        cls, package_name: PackageName | str, _version: Version | None = None
    ) -> Deprecator:
        pkg_name = PackageName(package_name)
        package_version = _version or Version(importlib.metadata.version(pkg_name))

        PendingDeprecationWarning, DeprecationWarning, DeprecationError = (
            create_package_warning_classes(pkg_name, package_version)
        )

        return Deprecator(
            pkg_name,
            package_version,
            pending=PendingDeprecationWarning,
            deprecation=DeprecationWarning,
            expired_warning=DeprecationError,
        )

    def _get_warning_class(self, gone_in: Version, warn_in: Version) -> WarningClass:
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
    ) -> WarningInstance:
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

        tracked_warning = SpecificWarning(message)
        assert isinstance(tracked_warning, DeprecatorWarningMixing)

        # If an explicit importable name was provided, set it directly
        if importable_name is not None:
            tracked_warning.importable_name = importable_name

        # Track the deprecation locally
        self._tracked_deprecations.append(tracked_warning)

        return cast(WarningInstance, tracked_warning)

    def __iter__(self) -> Iterator[DeprecatorWarningMixing]:
        """Iterate over the tracked deprecation warnings."""
        return iter(self._tracked_deprecations)

    def __len__(self) -> int:
        """Get the number of tracked deprecations."""
        return len(self._tracked_deprecations)
