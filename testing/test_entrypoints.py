"""Tests for entrypoint functionality."""

from __future__ import annotations

from packaging.version import Version

from deprecator._entrypoints import (
    validate_known_validators,
    validate_package_entrypoints,
)
from deprecator._registry import DeprecatorRegistry
from deprecator._types import PackageName


def test_validate_known_validators() -> None:
    """Test that validate_known_validators works correctly."""
    errors = validate_known_validators()

    assert errors == []


def test_validate_package_entrypoints_with_colon_prefix() -> None:
    """Test that packages starting with colon are handled correctly."""
    # Test packages starting with colon should not cause errors
    results = validate_package_entrypoints(":test-package")

    assert "deprecator" in results
    assert "registry" in results
    assert isinstance(results["deprecator"], dict)
    assert isinstance(results["registry"], dict)


def test_validate_package_entrypoints_nonexistent_package() -> None:
    """Test validation with nonexistent package."""
    results = validate_package_entrypoints("nonexistent-package-12345")

    assert "deprecator" in results
    assert "registry" in results
    # Should return empty dicts for nonexistent packages
    assert results["deprecator"] == {}
    assert results["registry"] == {}


def test_colon_prefix_skips_import_validation() -> None:
    """Test that colon-prefixed packages skip import validation."""
    # Create a registry with a colon-prefixed package
    registry = DeprecatorRegistry(framework=PackageName("test"))
    deprecator = registry.for_package(":test-package", _version=Version("1.0.0"))

    # Add a deprecation that would normally fail import validation
    deprecation = deprecator.define(
        "Test deprecation with non-importable module", gone_in="2.0.0", warn_in="1.5.0"
    )

    # This should work because colon-prefixed packages skip import validation
    assert deprecation is not None
    assert str(deprecator.name).startswith(":")
