"""Tests for the CLI module."""

from __future__ import annotations

import pytest
from packaging.version import Version
from pytest import CaptureFixture

from deprecator import for_package
from deprecator.cli import create_parser, main, print_all_deprecators, print_deprecator


class TestPrintDeprecator:
    """Tests for print_deprecator function."""

    def test_print_deprecator_with_deprecations(
        self, capsys: CaptureFixture[str]
    ) -> None:
        """Test printing deprecations for a package with deprecations."""
        # Create a deprecator with some deprecations
        deprecator = for_package(
            "test_print_package", _package_version=Version("1.7.0")
        )
        deprecator.define("This is deprecated", gone_in="2.0.0", warn_in="1.5.0")

        print_deprecator("test_print_package")

        captured = capsys.readouterr()
        assert "Deprecations for test_print_package" in captured.out
        assert "This is deprecated" in captured.out

    def test_print_deprecator_nonexistent_package(self) -> None:
        """Test printing deprecations for a non-existent package."""
        # Should raise an exception (not defensive)
        with pytest.raises((ImportError, ValueError)):
            print_deprecator("nonexistent_package_12345")


class TestPrintAllDeprecators:
    """Tests for print_all_deprecators function."""

    def test_print_all_deprecators_with_multiple_packages(
        self, capsys: CaptureFixture[str]
    ) -> None:
        """Test printing all deprecators when multiple packages exist."""
        # Create multiple deprecators with deprecations
        dep1 = for_package("all_test_package1", _package_version=Version("1.0.0"))
        dep1.define("Deprecation 1", gone_in="2.0.0")

        dep2 = for_package("all_test_package2", _package_version=Version("1.0.0"))
        dep2.define("Deprecation 2", gone_in="3.0.0")

        print_all_deprecators()

        captured = capsys.readouterr()
        assert "Deprecations for all_test_package1" in captured.out
        assert "Deprecations for all_test_package2" in captured.out
        assert "Deprecation 1" in captured.out
        assert "Deprecation 2" in captured.out

    def test_print_all_deprecators_empty_registry(
        self, capsys: CaptureFixture[str]
    ) -> None:
        """Test printing all deprecators when registry is empty."""
        # Clear the registry
        from deprecator._registry import default_registry

        default_registry._deprecators.clear()

        print_all_deprecators()

        captured = capsys.readouterr()
        # Should just print nothing (no output expected)
        assert captured.out == ""


class TestCreateParser:
    """Tests for create_parser function."""

    def test_create_parser_structure(self) -> None:
        """Test that parser has the expected structure."""
        parser = create_parser()

        assert parser.prog == "deprecator"
        assert parser.description == "Print deprecation tables"

    def test_parser_with_package_name(self) -> None:
        """Test parser with package name argument."""
        parser = create_parser()

        args = parser.parse_args(["test_package"])
        assert args.package_name == "test_package"

    def test_parser_without_package_name(self) -> None:
        """Test parser without package name argument."""
        parser = create_parser()

        args = parser.parse_args([])
        assert args.package_name is None


class TestMainFunction:
    """Tests for the main function."""

    def test_main_with_package_name(self, capsys: CaptureFixture[str]) -> None:
        """Test main function with package name."""
        # Create a test package with deprecations
        deprecator = for_package("main_test_package", _package_version=Version("1.0.0"))
        deprecator.define("Test main deprecation", gone_in="2.0.0")

        main(["main_test_package"])

        captured = capsys.readouterr()
        assert "Deprecations for main_test_package" in captured.out
        assert "Test main deprecation" in captured.out

    def test_main_without_package_name(self, capsys: CaptureFixture[str]) -> None:
        """Test main function without package name (print all)."""
        # Create test packages
        dep1 = for_package("main_all_test1", _package_version=Version("1.0.0"))
        dep1.define("Test deprecation 1", gone_in="2.0.0")

        dep2 = for_package("main_all_test2", _package_version=Version("1.0.0"))
        dep2.define("Test deprecation 2", gone_in="3.0.0")

        main([])

        captured = capsys.readouterr()
        assert "Deprecations for main_all_test1" in captured.out
        assert "Deprecations for main_all_test2" in captured.out
        assert "Test deprecation 1" in captured.out
        assert "Test deprecation 2" in captured.out

    def test_main_with_nonexistent_package(self) -> None:
        """Test main function with non-existent package."""
        with pytest.raises((ImportError, ValueError)):
            main(["nonexistent_package"])
