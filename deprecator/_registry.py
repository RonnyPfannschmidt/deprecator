"""Registry for managing deprecator instances."""

from __future__ import annotations

import warnings
from collections.abc import Iterator

from packaging.version import Version

from ._deprecator import Deprecator
from ._types import PackageName


class DeprecatorRegistry:
    """collection of deprecators bound to a specific framework

    we use deprecator as "framework" for unbound deprecators"""

    framework: PackageName
    _deprecators: dict[PackageName, Deprecator]

    def __init__(self, *, framework: PackageName) -> None:
        self.framework = framework
        # Cache deprecators by (package_name, version) tuple
        self._deprecators = {}

    def __iter__(self) -> Iterator[Deprecator]:
        return iter(self._deprecators.values())

    def for_package(
        self, package_name: PackageName | str, *, _version: Version | None = None
    ) -> Deprecator:
        """Get or create a deprecator for the given package and version.

        :param package_name: Name of the package to create deprecator for
        :param _version:
            NOTE: This is private/internal. User code should NOT provide this argument.
            This is Version of the package. If None, will be looked up automatically.
        :returns: Deprecator instance for the package
        """

        pkg_name = PackageName(package_name)
        if pkg_name not in self._deprecators:
            self._deprecators[pkg_name] = Deprecator.for_package(
                pkg_name, _package_version=_version
            )

        res = self._deprecators[pkg_name]

        if _version is not None and res.current_version != _version:
            warnings.warn(
                f"Deprecator for {package_name}"
                f" is being requested with a new explicit version,"
                f" but the cached one is for {res.current_version}",
                stacklevel=2,
            )

        return res


# Global default registry instance
default_registry = DeprecatorRegistry(framework=PackageName("deprecator"))
