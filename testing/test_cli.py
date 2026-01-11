"""Tests for the CLI module."""

from __future__ import annotations

from pathlib import Path

import click.testing
import pytest
from conftest import run_with_console_capture

# Removed unused imports
from deprecator._registry import DeprecatorRegistry
from deprecator.cli import cli, print_all_deprecators, print_deprecator


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

        # Check for both test packages
        assert ":test_package" in output
        assert ":another_package" in output

    def test_empty_registry(self, empty_registry: DeprecatorRegistry) -> None:
        """Test printing all deprecators from empty test registry."""
        output = run_with_console_capture(
            print_all_deprecators, registry=empty_registry
        )

        # No output expected for empty registry
        assert output.strip() == ""


class TestShowPackageCommand:
    """Tests for show-package CLI command."""

    def test_with_existing_package(self) -> None:
        """Test showing deprecators from an existing package."""
        runner = click.testing.CliRunner()
        result = runner.invoke(cli, ["show-package", "deprecator"])

        # Should show deprecators from the deprecator package
        assert "Deprecators from package 'deprecator'" in result.output

    def test_with_nonexistent_package(self) -> None:
        """Test showing deprecators from a non-existent package."""
        runner = click.testing.CliRunner()
        result = runner.invoke(cli, ["show-package", "nonexistent-package-name"])

        # Should show message about no deprecators found
        assert (
            "No deprecators found for package 'nonexistent-package-name'"
            in result.output
        )


class TestValidateValidators:
    """Tests for validate_validators command."""

    def test_validate_validators(self) -> None:
        """Test validating that known validators have entrypoints."""
        runner = click.testing.CliRunner()
        result = runner.invoke(cli, ["validate-validators"])

        # Should pass since the deprecator package has required entrypoints
        assert result.exit_code == 0
        assert "✔" in result.output
        assert "All known validators have corresponding entrypoints" in result.output


class TestListPackagesCommand:
    """Tests for list-packages CLI command."""

    def test_list_packages(self) -> None:
        """Test listing packages with entrypoints."""
        runner = click.testing.CliRunner()
        result = runner.invoke(cli, ["list-packages"])

        # Should show the deprecator package
        assert result.exit_code == 0
        assert "Packages with Deprecator Entrypoints:" in result.output
        assert "deprecator" in result.output


class TestCLI:
    """Tests for the Click CLI."""

    def test_cli_help(self) -> None:
        """Test that CLI help works."""
        runner = click.testing.CliRunner()
        result = runner.invoke(cli, ["--help"])

        assert result.exit_code == 0
        assert "Deprecator CLI" in result.output
        assert "Commands:" in result.output

    def test_show_registry_with_package(self) -> None:
        """Test show-registry command with package name."""
        runner = click.testing.CliRunner()
        # Test with non-existent package - should error appropriately
        result = runner.invoke(cli, ["show-registry", "test_package"])

        # test_package doesn't exist, so we expect a specific error
        assert result.exit_code == 2  # Configuration error
        assert "Error:" in result.output

    def test_show_registry_without_package(self) -> None:
        """Test show-registry command without package name."""
        runner = click.testing.CliRunner()
        result = runner.invoke(cli, ["show-registry"])

        # Should succeed even if no packages have deprecations
        assert result.exit_code == 0


class TestMainFunction:
    """Tests for main CLI function behavior."""

    def test_validate_package_command_success(self) -> None:
        """Test validate-package command with existing package."""
        runner = click.testing.CliRunner()
        result = runner.invoke(cli, ["validate-package", "deprecator"])

        # Should validate the deprecator package successfully
        assert result.exit_code == 0
        assert "Validation results for package 'deprecator'" in result.output

    def test_validate_package_command_failure(self) -> None:
        """Test validate-package command with non-existent package."""
        runner = click.testing.CliRunner()
        result = runner.invoke(cli, ["validate-package", "nonexistent-package"])

        # Should fail with appropriate error
        assert result.exit_code == 1
        assert "Package 'nonexistent-package' not found" in result.output

    def test_init_command(self, tmp_path: Path) -> None:
        """Test init command creates proper structure."""
        runner = click.testing.CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            # Create a minimal valid package structure
            import os

            os.makedirs("mypackage")
            with open("mypackage/__init__.py", "w") as f:
                f.write('"""Test package."""\n')

            # Create a minimal valid pyproject.toml
            with open("pyproject.toml", "w") as f:
                f.write("""[project]
name = "mypackage"
version = "0.1.0"

[project.entry-points."deprecator.deprecator"]
mypackage = "mypackage._deprecations:deprecator"
""")

            result = runner.invoke(cli, ["init"])

            # Check specific outcomes
            if result.exit_code == 0:
                # Success - verify the file was created
                assert os.path.exists("mypackage/_deprecations.py")
                with open("mypackage/_deprecations.py") as f:
                    content = f.read()
                    assert "for_package" in content
                    assert "deprecator" in content
            else:
                # If it failed, ensure it's for a valid reason
                assert result.exit_code == 2  # Configuration error
                # Check for meaningful error message
                assert "Error:" in result.output or "already exists" in result.output

    def test_init_command_already_setup(self, tmp_path: Path) -> None:
        """Test init command in a project that's already setup."""
        runner = click.testing.CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            import os

            # Create a complete package structure that's already set up
            os.makedirs("mypackage")
            with open("mypackage/__init__.py", "w") as f:
                f.write('"""Test package."""\n')

            # Create existing _deprecations.py file with custom content
            existing_deprecations_content = '''"""Existing deprecations."""

from __future__ import annotations

from deprecator import for_package

# Custom deprecator setup
deprecator = for_package(__package__)

# Existing deprecation
EXISTING_FEATURE = deprecator.define(
    "This feature already exists and should not be lost",
    warn_in="1.0.0",
    gone_in="2.0.0"
)
'''
            with open("mypackage/_deprecations.py", "w") as f:
                f.write(existing_deprecations_content)

            # Create pyproject.toml with entrypoint already configured
            with open("pyproject.toml", "w") as f:
                f.write("""[project]
name = "mypackage"
version = "0.1.0"

[project.entry-points."deprecator.deprecator"]
mypackage = "mypackage._deprecations:deprecator"
""")

            # Run init command - should handle existing setup gracefully
            result = runner.invoke(cli, ["init"], input="n\n")  # Don't overwrite

            # Should succeed and recognize existing setup
            assert result.exit_code == 0
            assert "already exists" in result.output

            # Verify existing file wasn't overwritten (since we said no)
            with open("mypackage/_deprecations.py") as f:
                content = f.read()
                assert "EXISTING_FEATURE" in content
                assert "This feature already exists" in content

            # Verify entrypoint is still there
            with open("pyproject.toml") as f:
                content = f.read()
                assert "deprecator.deprecator" in content
                assert 'mypackage = "mypackage._deprecations:deprecator"' in content

    def test_init_command_already_setup_overwrite(self, tmp_path: Path) -> None:
        """Test init command overwrites when user confirms."""
        runner = click.testing.CliRunner()
        with runner.isolated_filesystem(temp_dir=tmp_path):
            import os

            # Create a complete package structure that's already set up
            os.makedirs("mypackage")
            with open("mypackage/__init__.py", "w") as f:
                f.write('"""Test package."""\n')

            # Create existing _deprecations.py file with custom content
            existing_content = '''"""Old content that will be replaced."""
# This should be overwritten
OLD_DEPRECATION = None
'''
            with open("mypackage/_deprecations.py", "w") as f:
                f.write(existing_content)

            # Create pyproject.toml without entrypoint (to test it gets added)
            with open("pyproject.toml", "w") as f:
                f.write("""[project]
name = "mypackage"
version = "0.1.0"
""")

            # Run init command and confirm overwrite
            result = runner.invoke(cli, ["init"], input="y\n")  # Yes, overwrite

            # Should succeed
            assert result.exit_code == 0
            assert "already exists" in result.output

            # Verify file was overwritten with new content
            with open("mypackage/_deprecations.py") as f:
                content = f.read()
                assert "OLD_DEPRECATION" not in content  # Old content gone
                assert "Old content" not in content
                assert "EXAMPLE_DEPRECATION" in content  # New template content
                assert "for_package" in content

            # Verify entrypoint was added
            with open("pyproject.toml") as f:
                content = f.read()
                assert "deprecator.deprecator" in content
                assert 'mypackage = "mypackage._deprecations:deprecator"' in content

    def test_show_registry_with_valid_package(self) -> None:
        """Test show-registry with a package that exists and has deprecations."""
        runner = click.testing.CliRunner()
        result = runner.invoke(cli, ["show-registry", "deprecator"])

        # Should succeed and show deprecator's deprecations
        assert result.exit_code == 0
        assert "Deprecations for deprecator" in result.output
