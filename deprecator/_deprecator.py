from __future__ import annotations

import importlib.metadata
from collections.abc import Iterator
from typing import TYPE_CHECKING

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


def define_categories(
    for_deprecator: Deprecator,
) -> tuple[
    type[PerPackagePendingDeprecationWarning],
    type[PerPackageDeprecationWarning],
    type[PerPackageExpiredDeprecationWarning],
]:
    # Create the warning classes with ClassVars set
    class PendingDeprecationWarning(PerPackagePendingDeprecationWarning):
        package_name = for_deprecator.name
        current_version = for_deprecator.current_version
        deprecator = for_deprecator

    class DeprecationWarning(PerPackageDeprecationWarning):
        package_name = for_deprecator.name
        current_version = for_deprecator.current_version
        deprecator = for_deprecator

    class DeprecationError(PerPackageExpiredDeprecationWarning):
        package_name = for_deprecator.name
        current_version = for_deprecator.current_version
        deprecator = for_deprecator

    return PendingDeprecationWarning, DeprecationWarning, DeprecationError


class Deprecator:
    name: PackageName
    current_version: Version

    PendingDeprecationWarning: type[PerPackagePendingDeprecationWarning]
    DeprecationWarning: type[PerPackageDeprecationWarning]
    DeprecationError: type[PerPackageExpiredDeprecationWarning]

    def __init__(
        self,
        name: PackageName | str,
        current_version: Version,
        *,
        registry: DeprecatorRegistry | None = None,
        definition_module: str | None = None,
    ) -> None:
        self.name = PackageName(name)
        self.current_version = current_version
        self._registry = registry
        # Track deprecations in the deprecator itself
        self._tracked_deprecations: list[DeprecatorWarningMixing] = []
        (
            self.PendingDeprecationWarning,
            self.DeprecationWarning,
            self.DeprecationError,
        ) = define_categories(self)

    @classmethod
    def for_package(
        cls, package_name: PackageName | str, _package_version: Version | None = None
    ) -> Deprecator:
        pkg_name = PackageName(package_name)
        package_version = _package_version or Version(
            importlib.metadata.version(pkg_name)
        )

        return Deprecator(
            pkg_name,
            package_version,
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
        *,
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

        base_category = self._get_category(gone_in, warn_in)

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
        self._tracked_deprecations.append(warning)

        return warning  # type: ignore[no-any-return]

    def __iter__(self) -> Iterator[DeprecatorWarningMixing]:
        """
        Return an iterator over the tracked deprecations.
        """
        return iter(self._tracked_deprecations)
