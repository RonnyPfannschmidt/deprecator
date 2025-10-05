"""Tests for the CLI module."""

from __future__ import annotations

import pytest
from conftest import run_with_console_capture
from pytest import CaptureFixture

from deprecator._registry import DeprecatorRegistry
from deprecator.cli import (
    create_parser,
    list_packages_with_entrypoints,
    main,
    print_all_deprecators,
    print_deprecator,
    print_package_deprecators,
    validate_validators,
)


class TestPrintDeprecator:
    """Tests for print_deprecator function."""

    def test_with_registry(self, populated_test_registry: DeprecatorRegistry) -> None:
        """Test printing deprecations using test registry."""
        output = run_with_console_capture(
            print_deprecator, ":test_package", registry=populated_test_registry
        )

        assert "Deprecations for :test_package" in output
        assert "Test deprecation message" in output

    def test_nonexistent_package(self, empty_registry: DeprecatorRegistry) -> None:
        """Test printing deprecations for non-existent package."""
        # The underlying error should be a PackageNotFoundError from the registry lookup
        import importlib.metadata

        with pytest.raises(importlib.metadata.PackageNotFoundError):
            run_with_console_capture(
                print_deprecator, "nonexistent_package", registry=empty_registry
            )


class TestPrintAllDeprecators:
    """Tests for print_all_deprecators function."""

    def test_with_multiple_packages(
        self, populated_test_registry: DeprecatorRegistry
    ) -> None:
        """Test printing all deprecators from test registry."""
        output = run_with_console_capture(
            print_all_deprecators, registry=populated_test_registry
        )

        assert "Deprecations for :test_package" in output
        assert "Deprecations for :another_package" in output
        assert "Test deprecation message" in output
        assert "Another deprecation" in output

    def test_empty_registry(self, empty_registry: DeprecatorRegistry) -> None:
        """Test printing all deprecators when registry is empty."""
        output = run_with_console_capture(
            print_all_deprecators, registry=empty_registry
        )

        # Should print nothing for empty registry
        assert output == ""


class TestPrintPackageDeprecators:
    """Tests for print_package_deprecators function."""

    def test_with_existing_package(self) -> None:
        """Test printing deprecators from an existing package."""
        output = run_with_console_capture(print_package_deprecators, "deprecator")

        # Should show deprecators from the deprecator package
        assert "Deprecators from package 'deprecator'" in output

    def test_with_nonexistent_package(self) -> None:
        """Test printing deprecators from a non-existent package."""
        output = run_with_console_capture(
            print_package_deprecators, "nonexistent-package-name"
        )

        # Should show message about no deprecators found
        assert "No deprecators found for package 'nonexistent-package-name'" in output


class TestValidateValidators:
    """Tests for validate_validators function."""

    def test_validate_validators(self) -> None:
        """Test validating that known validators have entrypoints."""
        output = run_with_console_capture(validate_validators)

        # Should pass since the deprecator package has required entrypoints
        assert "✔" in output
        assert "All known validators have corresponding entrypoints" in output


class TestListPackagesWithEntrypoints:
    """Tests for list_packages_with_entrypoints function."""

    def test_list_packages(self) -> None:
        """Test listing packages with entrypoints."""
        output = run_with_console_capture(list_packages_with_entrypoints)

        # Should show the deprecator package
        assert "Packages with Deprecator Entrypoints:" in output
        assert "deprecator" in output


class TestCreateParser:
    """Tests for create_parser function."""

    def test_create_parser_structure(self) -> None:
        """Test that parser has the expected structure."""
        parser = create_parser()

        assert parser.prog == "deprecator"
        assert parser.description == "Print deprecation tables and manage entrypoints"

    def test_parser_with_package_name(self) -> None:
        """Test parser with package name argument using show-registry subcommand."""
        parser = create_parser()

        args = parser.parse_args(["show-registry", "test_package"])
        assert args.command == "show-registry"
        assert args.package_name == "test_package"

    def test_parser_without_package_name(self) -> None:
        """Test parser without package name argument using show-registry subcommand."""
        parser = create_parser()

        args = parser.parse_args(["show-registry"])
        assert args.command == "show-registry"
        assert args.package_name is None


class TestMainFunction:
    """Tests for the main function."""

    def test_show_specific_package(
        self, capsys: CaptureFixture[str], populated_test_registry: DeprecatorRegistry
    ) -> None:
        """Test main function with specific package."""
        main(["show-registry", ":test_package"], registry=populated_test_registry)

        captured = capsys.readouterr()
        assert "Deprecations for :test_package" in captured.out
        assert "Test deprecation message" in captured.out

    def test_show_all_packages(
        self, capsys: CaptureFixture[str], populated_test_registry: DeprecatorRegistry
    ) -> None:
        """Test main function showing all packages."""
        main(["show-registry"], registry=populated_test_registry)

        captured = capsys.readouterr()
        assert "Deprecations for :test_package" in captured.out
        assert "Deprecations for :another_package" in captured.out

    def test_nonexistent_package(self, empty_registry: DeprecatorRegistry) -> None:
        """Test main function with non-existent package."""
        with pytest.raises(SystemExit):
            main(["show-registry", ":nonexistent_package"], registry=empty_registry)

    def test_validate_validators_command(self, capsys: CaptureFixture[str]) -> None:
        """Test validate-validators command."""
        main(["validate-validators"])

        captured = capsys.readouterr()
        # Should pass since the deprecator package has the required entrypoints
        assert "✔" in captured.out
        assert "All known validators have corresponding entrypoints" in captured.out
