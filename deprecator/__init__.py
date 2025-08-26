from __future__ import annotations

from typing import TYPE_CHECKING

from ._legacy import deprecate

__all__ = ["deprecate"]


if TYPE_CHECKING:  # pragma: no cover
    from ._deprecator import Deprecator


def for_package(package_name: str) -> Deprecator:
    """return a deprecator bound to a specific package name and its current version"""
    from ._deprecator import Deprecator

    return Deprecator.for_package(package_name)
