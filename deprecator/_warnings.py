from __future__ import annotations

import sys
import warnings
from typing import TYPE_CHECKING, ClassVar, Type, TypeVar, Union

from packaging.version import Version
from typing_extensions import deprecated

__all__ = [
    "DeprecatorWarningMixing",
    "PerPackageDeprecationWarning",
    "PerPackageExpiredDeprecationWarning",
    "PerPackagePendingDeprecationWarning",
    "WarningClass",
    "WarningInstance",
    "get_warning_types",
]

if TYPE_CHECKING:
    from typing import TypeAlias

    from ._deprecator import Deprecator

T = TypeVar("T")

# Type aliases - define outside TYPE_CHECKING so they can be imported
WarningInstance = Union[
    "PerPackagePendingDeprecationWarning",
    "PerPackageDeprecationWarning",
    "PerPackageExpiredDeprecationWarning",
]

WarningClass = Union[
    Type["PerPackagePendingDeprecationWarning"],
    Type["PerPackageDeprecationWarning"],
    Type["PerPackageExpiredDeprecationWarning"],
]

WARNING_TYPES: TypeAlias = "tuple[type[DeprecatorWarningMixing], ...]"


class DeprecatorWarningMixing(Warning):
    package_name: ClassVar[str]
    github_warning_kind: ClassVar[str]
    gone_in: ClassVar[Version]
    warn_in: ClassVar[Version]
    current_version: ClassVar[Version]
    deprecator: ClassVar[Deprecator]

    _cached_importable_name: str | None = None

    def find_importable_name(self) -> str | None:
        if self._cached_importable_name is not None:
            return self._cached_importable_name
        for module in sys.modules.values():
            for attr, value in module.__dict__.items():
                if value is self:
                    self._cached_importable_name = f"{module.__name__}.{attr}"
                    return self._cached_importable_name
        return None

    def warn(self, *, stacklevel: int = 2) -> None:
        """Emit this warning using the standard warnings system.

        Args:
            stacklevel: How many stack frames to go up when reporting the
                       warning location. Defaults to 2 (caller of the method
                       that calls warn()).
        """
        warnings.warn(self, category=type(self), stacklevel=stacklevel)

    def warn_explicit(
        self,
        filename: str,
        lineno: int,
        module: str | None = None,
    ) -> None:
        """Emit this warning with explicit filename and line number.

        Args:
            filename: The source file where the warning is being issued
            lineno: The line number in the source file
            module: The module name (if None, will be inferred)
        """
        # Find the appropriate stdlib warning category from our inheritance chain
        # We traverse the MRO to find the first stdlib warning class
        category = Warning  # Default fallback
        for cls in type(self).__mro__:
            if (
                cls.__module__ == "builtins"
                and issubclass(cls, Warning)
                and cls is not Warning
            ):
                category = cls
                break

        warnings.warn_explicit(
            str(self),
            category=category,
            filename=filename,
            lineno=lineno,
            module=module or "__main__",  # Default to __main__ to avoid filtering
        )

    def apply(self, func_or_class: T) -> T:
        decorator = deprecated(str(self), category=type(self))
        return decorator(func_or_class)


class PerPackagePendingDeprecationWarning(
    DeprecatorWarningMixing, PendingDeprecationWarning
):
    """
    category for deprecations that are pending and we want to warn about in tests
    """

    github_warning_kind = "warning"


class PerPackageDeprecationWarning(DeprecatorWarningMixing, DeprecationWarning):
    """
    category for deprecations we want to warn about
    """

    github_warning_kind = "warning"


class PerPackageExpiredDeprecationWarning(DeprecatorWarningMixing, DeprecationWarning):
    """
    category for deprecations to trigger errors for unless explicitly suppressed
    """

    github_warning_kind = "error"


def get_warning_types(
    *,
    pending: bool = False,
    active: bool = True,
    expired: bool = True,
) -> tuple[type[DeprecatorWarningMixing], ...]:
    warning_types: tuple[type[DeprecatorWarningMixing], ...] = ()

    if pending:
        warning_types += (PerPackagePendingDeprecationWarning,)
    if active:
        warning_types += (PerPackageDeprecationWarning,)
    if expired:
        warning_types += (PerPackageExpiredDeprecationWarning,)
    if not warning_types:
        raise TypeError("At least one warning type must be selected")
    return warning_types
