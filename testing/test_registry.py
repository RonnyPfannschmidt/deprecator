"""Tests for deprecator registry functionality."""

from __future__ import annotations

import pytest
from packaging.version import Version

from deprecator._deprecator import Deprecator
from deprecator._registry import DeprecatorRegistry
from deprecator._types import PackageName


@pytest.fixture
def registry() -> DeprecatorRegistry:
    """Fixture to provide a fresh DeprecatorRegistry instance for each test."""

    return DeprecatorRegistry(framework=":test-example")


def test_deprecator_registry_for_package(registry: DeprecatorRegistry) -> None:
    """Test that registry can get or create deprecators for packages."""
    # Mock package for testing
    package_name = "test_package"

    # First call should create a new deprecator
    deprecator1 = registry.for_package(package_name, _version=Version("1.0.0"))
    assert isinstance(deprecator1, Deprecator)
    assert deprecator1.name == PackageName(package_name)
    assert deprecator1.current_version == Version("1.0.0")

    # Second call with same package should return the same instance
    deprecator2 = registry.for_package(package_name, _version=Version("1.0.0"))
    assert deprecator1 is deprecator2

    # Call with different version should create a new instance
    with pytest.warns(
        UserWarning,
        match=f"Deprecator for {package_name} is being"
        " requested with a new explicit version,",
    ):
        deprecator3 = registry.for_package(package_name, _version=Version("1.1.0"))
    assert deprecator1 is deprecator3
    assert deprecator3.current_version == Version("1.0.0")


def test_default_registry_exists() -> None:
    """Test that a default global registry instance exists."""
    from deprecator._registry import default_registry

    assert hasattr(default_registry, "for_package")


def test_for_package_uses_default_registry() -> None:
    """Test that for_package function uses the default registry."""
    import deprecator
    from deprecator._registry import default_registry

    # Mock the registry to track calls
    original_for_package = default_registry.for_package
    called_with = []

    def mock_for_package(
        package_name: PackageName | str, *, _version: Version | None = None
    ) -> Deprecator:
        called_with.append((package_name, _version))
        return original_for_package(package_name, _version=_version)

    default_registry.for_package = mock_for_package  # type: ignore[method-assign]

    try:
        # Use an existing package to avoid metadata lookup issues in tests
        deprecator.for_package("deprecator")
        assert len(called_with) == 1
        assert called_with[0][0] == "deprecator"
        assert called_with[0][1] is None  # _version should be None when not specified
    finally:
        # Restore original method
        default_registry.for_package = original_for_package  # type: ignore[method-assign]


def test_custom_registry_creation() -> None:
    """Test that frameworks can create their own registry instances."""
    from deprecator._registry import DeprecatorRegistry

    # Create custom registry for a framework
    framework_registry = DeprecatorRegistry(framework="test-framework")

    # Should be different from default registry
    from deprecator._registry import default_registry

    assert framework_registry is not default_registry

    # Should work independently
    dep1 = framework_registry.for_package("my_framework", _version=Version("1.0.0"))
    dep2 = default_registry.for_package("my_framework", _version=Version("1.0.0"))

    # Different registries should create different instances
    assert dep1 is not dep2


def test_registry_with_framework_name() -> None:
    """Test that registries can be created with framework names."""
    from deprecator._registry import DeprecatorRegistry

    # Create registries with different framework names
    django_registry = DeprecatorRegistry(framework="Django")
    flask_registry = DeprecatorRegistry(framework="Flask")
    unnamed_registry = DeprecatorRegistry(framework="unnamed")

    # Check framework names
    assert django_registry.framework == PackageName("Django")
    assert flask_registry.framework == PackageName("Flask")
    assert unnamed_registry.framework == PackageName("unnamed")

    # Different framework registries should be independent
    dep1 = django_registry.for_package("web_framework", _version=Version("1.0.0"))
    dep2 = flask_registry.for_package("web_framework", _version=Version("1.0.0"))

    assert dep1 is not dep2

    # Should be tracked separately by each deprecator
    dep1_tracked = dep1.get_tracked_deprecations()
    dep2_tracked = dep2.get_tracked_deprecations()

    # They should be independent
    assert len(dep1_tracked) == 0
    assert len(dep2_tracked) == 0


def test_deprecation_tracking() -> None:
    """Test that deprecations are tracked by the deprecator itself."""
    from deprecator._registry import DeprecatorRegistry

    registry = DeprecatorRegistry(framework="test-package")
    deprecator_instance = registry.for_package("my_package", _version=Version("1.0.0"))

    # Define some deprecations - these should be tracked by the deprecator
    deprecator_instance.define(
        "Function foo is deprecated", gone_in="2.0.0", warn_in="1.5.0"
    )

    deprecator_instance.define(
        "Class Bar is deprecated", gone_in="3.0.0", warn_in="2.0.0"
    )

    # Deprecator should track these deprecations
    tracked_deprecations = deprecator_instance.get_tracked_deprecations()

    assert len(tracked_deprecations) == 2

    # Each tracked deprecation should be a warning instance
    assert any(d for d in tracked_deprecations if "foo" in str(d))
    assert any(d for d in tracked_deprecations if "Bar" in str(d))
