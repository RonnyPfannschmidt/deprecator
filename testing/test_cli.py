"""Tests for the CLI module."""

from __future__ import annotations

import pytest
from packaging.version import Version
from pytest import CaptureFixture

from deprecator._registry import DeprecatorRegistry
from deprecator._types import PackageName
from deprecator.cli import create_parser, main, print_all_deprecators, print_deprecator


@pytest.fixture
def test_registry() -> DeprecatorRegistry:
    """Create a test registry with sample deprecators."""
    registry = DeprecatorRegistry(framework=PackageName("test"))

    # Add a deprecator with active deprecations
    dep1 = registry.for_package("test_package", _version=Version("2.0.0"))
    dep1.define("Test deprecation message", gone_in="3.0.0", warn_in="1.5.0")

    # Add another deprecator with active deprecation
    dep2 = registry.for_package("another_package", _version=Version("1.5.0"))
    dep2.define("Another deprecation", gone_in="2.0.0", warn_in="1.0.0")

    return registry


@pytest.fixture
def empty_registry() -> DeprecatorRegistry:
    """Create an empty test registry."""
    return DeprecatorRegistry(framework=PackageName("test"))


class TestPrintDeprecator:
    """Tests for print_deprecator function."""

    def test_with_registry(
        self, capsys: CaptureFixture[str], test_registry: DeprecatorRegistry
    ) -> None:
        """Test printing deprecations using test registry."""
        print_deprecator("test_package", registry=test_registry)

        captured = capsys.readouterr()
        assert "Deprecations for test_package" in captured.out
        assert "Test deprecation message" in captured.out

    def test_nonexistent_package(self, empty_registry: DeprecatorRegistry) -> None:
        """Test printing deprecations for non-existent package."""
        with pytest.raises(SystemExit):
            print_deprecator("nonexistent_package", registry=empty_registry)


class TestPrintAllDeprecators:
    """Tests for print_all_deprecators function."""

    def test_with_multiple_packages(
        self, capsys: CaptureFixture[str], test_registry: DeprecatorRegistry
    ) -> None:
        """Test printing all deprecators from test registry."""
        print_all_deprecators(registry=test_registry)

        captured = capsys.readouterr()
        assert "Deprecations for test_package" in captured.out
        assert "Deprecations for another_package" in captured.out
        assert "Test deprecation message" in captured.out
        assert "Another deprecation" in captured.out

    def test_empty_registry(
        self, capsys: CaptureFixture[str], empty_registry: DeprecatorRegistry
    ) -> None:
        """Test printing all deprecators when registry is empty."""
        print_all_deprecators(registry=empty_registry)

        captured = capsys.readouterr()
        assert captured.out == ""


class TestCreateParser:
    """Tests for create_parser function."""

    def test_create_parser_structure(self) -> None:
        """Test that parser has the expected structure."""
        parser = create_parser()

        assert parser.prog == "deprecator"
        assert parser.description == "Print deprecation tables and manage entrypoints"

    def test_parser_with_package_name(self) -> None:
        """Test parser with package name argument using show subcommand."""
        parser = create_parser()

        args = parser.parse_args(["show", "test_package"])
        assert args.command == "show"
        assert args.package_name == "test_package"

    def test_parser_without_package_name(self) -> None:
        """Test parser without package name argument using show subcommand."""
        parser = create_parser()

        args = parser.parse_args(["show"])
        assert args.command == "show"
        assert args.package_name is None


class TestMainFunction:
    """Tests for the main function."""

    def test_show_specific_package(
        self, capsys: CaptureFixture[str], test_registry: DeprecatorRegistry
    ) -> None:
        """Test main function with specific package."""
        main(["show", "test_package"], registry=test_registry)

        captured = capsys.readouterr()
        assert "Deprecations for test_package" in captured.out
        assert "Test deprecation message" in captured.out

    def test_show_all_packages(
        self, capsys: CaptureFixture[str], test_registry: DeprecatorRegistry
    ) -> None:
        """Test main function showing all packages."""
        main(["show"], registry=test_registry)

        captured = capsys.readouterr()
        assert "Deprecations for test_package" in captured.out
        assert "Deprecations for another_package" in captured.out

    def test_nonexistent_package(self, empty_registry: DeprecatorRegistry) -> None:
        """Test main function with non-existent package."""
        with pytest.raises(SystemExit):
            main(["show", "nonexistent_package"], registry=empty_registry)

    def test_validate_validators_command(self, capsys: CaptureFixture[str]) -> None:
        """Test validate-validators command."""
        main(["validate-validators"])

        captured = capsys.readouterr()
        # Should pass since the deprecator package has the required entrypoints
        assert "✓" in captured.out
        assert "All known validators have corresponding entrypoints" in captured.out
