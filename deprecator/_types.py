"""Type definitions for the deprecator package."""

from __future__ import annotations

from typing import NewType

# A package name used throughout the deprecator system
# Used for both framework names in registries and package names in deprecators
PackageName = NewType("PackageName", str)


def is_test_package(package_name: PackageName | str) -> bool:
    """Check if a package name represents a test package.

    Test packages are identified by starting with a colon (:) and are used
    for testing purposes without requiring actual installed packages.

    Args:
        package_name: The package name to check

    Returns:
        True if the package is a test package, False otherwise
    """
    return str(package_name).startswith(":")


def requires_import_validation(package_name: PackageName | str) -> bool:
    """Check if a package requires import validation.

    Test packages (those starting with colon) skip import validation
    since they don't represent real installed packages.

    Args:
        package_name: The package name to check

    Returns:
        True if import validation is required, False for test packages
    """
    return not is_test_package(package_name)
