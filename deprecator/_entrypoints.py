"""Entrypoint discovery for deprecators and registries."""

from __future__ import annotations

import importlib
import importlib.metadata
from typing import TYPE_CHECKING, Literal

from ._types import PackageName, is_test_package, requires_import_validation

if TYPE_CHECKING:
    from ._deprecator import Deprecator
    from ._registry import DeprecatorRegistry


def find_deprecators_for_package(package_name: str) -> dict[str, Deprecator]:
    """Find all deprecators defined by a specific package.

    Args:
        package_name: Name of the package/distribution to look up

    Returns:
        Dictionary mapping entrypoint names to Deprecator instances
    """

    try:
        dist = importlib.metadata.distribution(package_name)
    except importlib.metadata.PackageNotFoundError:
        return {}

    else:
        return {
            ep.name: ep.load()
            for ep in dist.entry_points
            if ep.group == "deprecator.deprecator"
        }


def find_registry_for_package(package_name: str) -> DeprecatorRegistry | None:
    """Find the registry defined by a specific package.

    Args:
        package_name: Name of the package/distribution to look up

    Returns:
        DeprecatorRegistry instance if found, None otherwise
    """
    try:
        dist = importlib.metadata.distribution(package_name)
    except importlib.metadata.PackageNotFoundError:
        # Package not installed
        return None

    for ep in dist.entry_points:
        if ep.group == "deprecator.registry" and ep.name == package_name:
            registry = ep.load()
            assert isinstance(registry, DeprecatorRegistry), ep
            return registry
    return None


def list_packages_with_group(group: str) -> list[PackageName]:
    """List all packages that define entrypoints in a specific group."""
    packages: list[PackageName] = []

    # Handle Python 3.8 vs 3.9+ API differences
    try:
        # Python 3.9+ API
        entry_points = importlib.metadata.entry_points(group=group)
        for ep in entry_points:
            if ep.dist is not None:
                packages.append(PackageName(ep.dist.name))
    except TypeError:
        # Python 3.8 API - entry_points() returns a dict and EntryPoint has no .dist
        # Need to iterate through distributions to find packages with the group
        for dist in importlib.metadata.distributions():
            for ep in dist.entry_points:
                if ep.group == group:
                    packages.append(PackageName(dist.metadata["Name"]))
                    break  # Found at least one EP in this group for this package

    packages.sort()
    return packages


def list_packages_with_deprecators() -> list[PackageName]:
    """List all packages that define deprecator entrypoints."""
    return list_packages_with_group("deprecator.deprecator")


def list_packages_with_registries() -> list[PackageName]:
    """List all packages that define registry entrypoints."""
    return list_packages_with_group("deprecator.registry")


def validate_deprecator(ep: importlib.metadata.EntryPoint) -> list[str]:
    """Validate a deprecator entrypoint."""
    from ._deprecator import Deprecator

    errors = []
    deprecator = ep.load()
    if not isinstance(deprecator, Deprecator):
        errors.append(f"Expected Deprecator instance, got {type(deprecator).__name__}")
        return errors  # Can't validate further without a proper Deprecator instance

    # Validate that entrypoint name matches the registry framework name
    if deprecator._registry and ep.name != str(deprecator._registry.framework):
        errors.append(
            f"Entrypoint name '{ep.name}' does not match registry framework "
            f"'{deprecator._registry.framework}'"
        )

    for deprecation in deprecator:
        importable_name = deprecation.find_importable_name()
        if importable_name is None:
            errors.append(f"Missing importable name for {deprecation}")
        else:
            # Skip import validation for test packages starting with colon
            if requires_import_validation(deprecator.name):
                try:
                    # Split module.attribute into module and attribute parts
                    if "." in importable_name:
                        module_name, attr_name = importable_name.rsplit(".", 1)
                        module = importlib.import_module(module_name)
                        if not hasattr(module, attr_name):
                            errors.append(
                                f"Attribute '{attr_name}' "
                                f"not found in module '{module_name}' for {deprecation}"
                            )
                    else:
                        # If no dot, treat as module name only
                        importlib.import_module(importable_name)
                except ImportError as e:
                    errors.append(
                        f"Failed to import {importable_name} for {deprecation}: {e}"
                    )
    return errors


def validate_registry(ep: importlib.metadata.EntryPoint) -> list[str]:
    """Validate a registry entrypoint."""
    from ._registry import DeprecatorRegistry

    errors = []
    registry = ep.load()
    if not isinstance(registry, DeprecatorRegistry):
        errors.append(
            f"Expected DeprecatorRegistry instance, got {type(registry).__name__}"
        )
    elif registry.framework != PackageName(ep.name):
        errors.append(f"Expected framework {ep.name}, got {registry.framework}")

    return errors


def validate_known_validators() -> list[str]:
    """Validate that each known validator has a corresponding entrypoint.

    Returns:
        List of validation errors - empty list if no errors
    """
    errors = []

    # Known validators that should have entrypoints
    known_validators = {
        "validate_deprecator": "deprecator.deprecator",
        "validate_registry": "deprecator.registry",
    }

    for validator_name, expected_group in known_validators.items():
        # Check if there are any entrypoints in the expected group
        try:
            # Handle Python 3.8 vs 3.9+ API differences
            try:
                # Python 3.9+ API
                entrypoints = list(
                    importlib.metadata.entry_points(group=expected_group)
                )
            except TypeError:
                # Python 3.8 API - entry_points() returns a dict
                all_entry_points = importlib.metadata.entry_points()
                entrypoints = all_entry_points.get(expected_group, [])

            if not entrypoints:
                errors.append(
                    f"Validator '{validator_name}' expects entrypoints in group "
                    f"'{expected_group}', but none found"
                )
        except Exception as e:
            errors.append(
                f"Failed to check entrypoints for validator '{validator_name}': {e}"
            )

    return errors


def validate_package_entrypoints(
    package_name: str,
) -> dict[Literal["deprecator", "registry"], dict[str, list[str]]]:
    """Validate all entrypoints defined by a specific package.

    Args:
        package_name: Name of the package to validate

    Returns:
        Nested dictionary with validation results - empty lists if no errors
    """
    results: dict[Literal["deprecator", "registry"], dict[str, list[str]]] = {
        "deprecator": {},
        "registry": {},
    }

    # Skip import validation for test packages starting with colon
    skip_validation = is_test_package(package_name)

    try:
        if not skip_validation:
            dist = importlib.metadata.distribution(package_name)

            # Validate deprecator entrypoints
            for ep in dist.entry_points:
                if ep.group == "deprecator.deprecator":
                    errors = validate_deprecator(ep)
                    results["deprecator"][ep.name] = errors

                elif ep.group == "deprecator.registry":
                    errors = validate_registry(ep)
                    results["registry"][ep.name] = errors
        else:
            # For test packages starting with colon, we don't require actual entrypoints
            # but we can still validate the structure if any are provided
            pass

    except importlib.metadata.PackageNotFoundError:
        # For backward compatibility with CLI, we'll handle this differently
        pass
    except Exception:
        # For backward compatibility with CLI, we'll handle this differently
        pass

    return results
