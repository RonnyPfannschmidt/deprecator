from __future__ import annotations

import warnings
from typing import ClassVar

from packaging.version import Version


class DeprecatorWarningMixing(Warning):
    package_name: ClassVar[str]
    gone_in: ClassVar[Version]
    warn_in: ClassVar[Version]
    current_version: ClassVar[Version]

    def __init_subclass__(cls, *, package_name: str | None = None) -> None:
        if package_name is not None:
            cls.package_name = package_name

    def __init__(self, msg: str) -> None:
        """Initialize warning with message only, like stdlib warnings."""
        super().__init__(msg)

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


class PerPackagePendingDeprecationWarning(
    DeprecatorWarningMixing, PendingDeprecationWarning
):
    """
    category for deprecations that are pending and we want to warn about in tests
    """


class PerPackageDeprecationWarning(DeprecatorWarningMixing, DeprecationWarning):
    """
    category for deprecations we want to warn about
    """


class PerPackageExpiredDeprecationWarning(DeprecatorWarningMixing, DeprecationWarning):
    """
    category for deprecations to trigger errors for unless explicitly suppressed
    """
