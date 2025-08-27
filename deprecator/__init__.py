from __future__ import annotations

from typing import TYPE_CHECKING

from ._legacy import deprecate
from ._registry import DeprecatorRegistry, default_registry

__all__ = ["DeprecatorRegistry", "default_registry", "deprecate"]


if TYPE_CHECKING:  # pragma: no cover
    from ._deprecator import Deprecator


def for_package(package_name: str) -> Deprecator:
    """return a deprecator bound to a specific package name and its current version"""
    from ._registry import default_registry

    return default_registry.for_package(package_name)


def registry_for_framework(framework_name: str) -> DeprecatorRegistry:
    """return a registry bound to a specific framework name"""
    from ._registry import DeprecatorRegistry

    return DeprecatorRegistry(framework_name=framework_name)
