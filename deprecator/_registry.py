"""Registry for managing deprecator instances."""

from __future__ import annotations

import warnings

from packaging.version import Version

from ._deprecator import Deprecator


class DeprecatorRegistry:
    """Registry that manages deprecator instances for packages."""

    def __init__(self, *, framework_name: str | None = None) -> None:
        self.framework_name = framework_name
        # Cache deprecators by (package_name, version) tuple
        self._deprecators: dict[str, Deprecator] = {}

    def for_package(
        self, package_name: str, *, _version: Version | None = None
    ) -> Deprecator:
        """Get or create a deprecator for the given package and version.

        :param package_name: Name of the package
        :param _version:
            NOTE: This is private/internal. User code should NOT provide this argument.
            This is Version of the package. If None, will be looked up automatically.
        :returns: Deprecator instance for the package
        """

        if package_name not in self._deprecators:
            self._deprecators[package_name] = Deprecator.for_package(
                package_name, _package_version=_version
            )

        res = self._deprecators[package_name]

        if _version is not None and res.current_version != _version:
            warnings.warn(
                f"Deprecator for {package_name}"
                f" is being requested with a new explicit version,"
                f" but the cached one is for {res.current_version}",
                stacklevel=2,
            )

        return res


# Global default registry instance
default_registry = DeprecatorRegistry()
