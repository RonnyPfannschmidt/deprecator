from __future__ import annotations

from typing import TYPE_CHECKING

from ._legacy import deprecate
from ._types import PackageName

__all__ = ["PackageName", "deprecate", "for_package", "registry_for"]


if TYPE_CHECKING:  # pragma: no cover
    from packaging.version import Version

    from ._deprecator import Deprecator
    from ._registry import DeprecatorRegistry


def for_package(
    package_name: PackageName | str, _version: Version | None = None
) -> Deprecator:
    """return a deprecator bound to a specific package name and its current version"""
    from ._registry import default_registry

    return default_registry.for_package(package_name, _version=_version)


def registry_for(*, framework: PackageName | str) -> DeprecatorRegistry:
    """return a registry bound to a specific package name"""
    from ._registry import DeprecatorRegistry

    return DeprecatorRegistry(framework=PackageName(framework))
