from __future__ import annotations

import sys
import warnings
from functools import cached_property
from types import ModuleType
from typing import TYPE_CHECKING, ClassVar, Type, TypeVar, Union

from packaging.version import Version
from typing_extensions import deprecated

from ._types import PackageName

__all__ = [
    "DeprecatorWarningMixing",
    "PerPackageDeprecationWarning",
    "PerPackageExpiredDeprecationWarning",
    "PerPackagePendingDeprecationWarning",
    "WarningClass",
    "WarningInstance",
    "create_package_warning_classes",
    "find_warning_in_modules",
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


def find_warning_in_modules(
    warning_instance: object,
    modules: dict[str, ModuleType | None] | None = None,
) -> str | None:
    """Search for a warning instance in modules and return its importable name.

    Args:
        warning_instance: The warning instance to search for
        modules: Dictionary of modules to search in (defaults to sys.modules)

    Returns:
        The importable name (e.g., "module.attribute") or None if not found
    """
    if modules is None:
        modules = sys.modules  # type: ignore[assignment]

    for module in modules.values():  # type: ignore[union-attr]
        if module is None:
            continue
        module_dict = getattr(module, "__dict__", None)
        if module_dict is None:
            continue
        for attr, value in module_dict.items():
            if value is warning_instance:
                return f"{module.__name__}.{attr}"
    return None


class DeprecatorWarningMixing(Warning):
    package_name: ClassVar[str]
    github_warning_kind: ClassVar[str]
    gone_in: ClassVar[Version]
    warn_in: ClassVar[Version]
    current_version: ClassVar[Version]
    deprecator: ClassVar[Deprecator]

    def __repr__(self) -> str:
        """Return a string representation showing version information."""
        # Get version info if available
        gone_in = getattr(type(self), "gone_in", None)
        warn_in = getattr(type(self), "warn_in", None)

        if gone_in is not None and warn_in is not None:
            return f"<{type(self).__name__} gone_in={gone_in} warn_in={warn_in}>"
        return super().__repr__()

    @cached_property
    def importable_name(self) -> str | None:
        """Get the importable name for this warning instance (cached).

        Returns:
            The importable name (e.g., "module.attribute") or None if not found
        """
        return find_warning_in_modules(self)

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


def create_package_warning_classes(
    package_name: PackageName | str, current_version: Version
) -> tuple[
    type[PerPackagePendingDeprecationWarning],
    type[PerPackageDeprecationWarning],
    type[PerPackageExpiredDeprecationWarning],
]:
    """Create package-specific warning classes with ClassVars set.

    Args:
        package_name: Name of the package
        current_version: Current version of the package

    Returns:
        Tuple of (PendingDeprecationWarning, DeprecationWarning,
        ExpiredDeprecationWarning) classes
    """
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
