from __future__ import annotations

from typing import TYPE_CHECKING

from ._legacy import deprecate
from ._types import PackageName

__all__ = ["PackageName", "deprecate", "for_package", "registry_for_package"]


if TYPE_CHECKING:  # pragma: no cover
    from ._deprecator import Deprecator
    from ._registry import DeprecatorRegistry


def for_package(package_name: PackageName) -> Deprecator:
    """return a deprecator bound to a specific package name and its current version"""
    from ._registry import default_registry

    return default_registry.for_package(package_name)


def registry_for_package(package_name: PackageName) -> DeprecatorRegistry:
    """return a registry bound to a specific package name"""
    from ._registry import DeprecatorRegistry

    return DeprecatorRegistry(framework=package_name)
