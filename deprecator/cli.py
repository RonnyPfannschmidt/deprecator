"""Command line interface for deprecator.

Exit codes:
- 0: Success, no issues
- 1: Expired deprecations or validation failures found
- 2: Configuration or usage errors
"""

from __future__ import annotations

import sys

import click
from rich.console import Console
from rich.text import Text

from ._entrypoints import (
    find_deprecators_for_package,
    list_packages_with_deprecators,
    list_packages_with_registries,
    validate_known_validators,
    validate_package_entrypoints,
)
from ._init_command import init_deprecator
from ._registry import DeprecatorRegistry, default_registry
from .ux import print_deprecations

RED_CROSS = Text.from_markup("[red bold]:cross_mark:")
GREEN_CHECK_MARK = Text.from_markup("[green bold]:heavy_check_mark:")


def print_deprecator(
    package_name: str,
    console: Console,
    registry: DeprecatorRegistry | None = None,
) -> None:
    """Print deprecations table for a specific package.

    Args:
        package_name: Name of the package to print deprecations for
        console: Console for output
        registry: Optional registry to use (defaults to default_registry)
    """
    registry = registry or default_registry
    deprecator = registry.for_package(package_name)
    print_deprecations(deprecator, console=console)


def print_all_deprecators(
    console: Console, registry: DeprecatorRegistry | None = None
) -> None:
    """Print deprecations tables for all deprecators in a registry.

    Args:
        console: Console for output
        registry: Optional registry to use (defaults to default_registry)
    """
    registry = registry or default_registry
    for deprecator in registry:
        print_deprecations(deprecator, console=console)
        console.print()  # Add blank line between tables


@click.group()
@click.version_option()
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Deprecator CLI - Manage deprecation warnings in Python packages."""
    ctx.ensure_object(Console)


@cli.command()
@click.pass_obj
def init(console: Console) -> None:
    """Initialize deprecator for the current project.

    This creates a _deprecations.py file in your package with a basic setup
    and configures the necessary entry points in pyproject.toml.
    """
    try:
        init_deprecator(console)
    except (SystemExit, KeyboardInterrupt):
        raise
    except Exception as e:
        console.print(RED_CROSS, f"Error: {e}")
        sys.exit(2)


@cli.command(name="show-registry")
@click.argument("package_name", required=False)
@click.pass_obj
def show_registry(console: Console, package_name: str | None) -> None:
    """Show deprecations from the default registry.

    If PACKAGE_NAME is provided, shows deprecations for that specific package.
    Otherwise, shows all deprecations from all packages in the default registry.

    Examples:
        deprecator show-registry          # Show all deprecations
        deprecator show-registry mypackage # Show deprecations for mypackage
    """
    try:
        if package_name:
            print_deprecator(package_name, console)
        else:
            print_all_deprecators(console)
    except ValueError as e:
        console.print(RED_CROSS, f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        console.print(RED_CROSS, f"Error: {e}")
        sys.exit(2)


@cli.command(name="show-package")
@click.argument("package_name")
@click.pass_obj
def show_package(console: Console, package_name: str) -> None:
    """Show all deprecators defined by a specific package.

    This displays all deprecator instances that PACKAGE_NAME has defined
    through entry points, allowing you to see what deprecations a package
    contributes to various frameworks.
    """
    try:
        deprecators = find_deprecators_for_package(package_name)
        if not deprecators:
            console.print(
                f"[yellow]No deprecators found for package '{package_name}'[/yellow]"
            )
            return

        console.print(f"[bold]Deprecators from package '{package_name}':[/bold]")
        console.print()

        for name, deprecator in sorted(deprecators.items()):
            console.print(f"[bold cyan]Deprecator: {name}[/bold cyan]")
            print_deprecations(deprecator, console=console)
            console.print()
    except Exception as e:
        console.print(RED_CROSS, f"Error: {e}")
        sys.exit(2)


@cli.command(name="validate-package")
@click.argument("package_name")
@click.pass_obj
def validate_package(console: Console, package_name: str) -> None:
    """Validate all entrypoints defined by a specific package.

    This checks that:
    - All deprecator entry points are correctly configured
    - All registry entry points are correctly configured
    - The referenced objects can be imported

    Exit code 1 if validation fails, 0 if successful.
    """
    try:
        import importlib.metadata

        try:
            importlib.metadata.distribution(package_name)
        except importlib.metadata.PackageNotFoundError:
            raise ValueError(f"Package '{package_name}' not found") from None

        results = validate_package_entrypoints(package_name)

        total_entrypoints = len(results["deprecator"]) + len(results["registry"])
        if total_entrypoints == 0:
            console.print(
                f"[yellow]No deprecator/registry entrypoints found for package "
                f"'{package_name}'[/yellow]"
            )
            return

        console.print(f"[bold]Validation results for package '{package_name}':[/bold]")
        console.print()

        valid_count = 0
        invalid_count = 0

        # Check deprecator entrypoints
        for name, errors in sorted(results["deprecator"].items()):
            if not errors:
                console.print(GREEN_CHECK_MARK, f"deprecator:{name}")
                valid_count += 1
            else:
                console.print(RED_CROSS, f"deprecator:{name}: {'; '.join(errors)}")
                invalid_count += 1

        # Check registry entrypoints
        for name, errors in sorted(results["registry"].items()):
            if not errors:
                console.print(GREEN_CHECK_MARK, f"registry:{name}")
                valid_count += 1
            else:
                console.print(RED_CROSS, f"registry:{name}: {'; '.join(errors)}")
                invalid_count += 1

        console.print()
        console.print(
            f"[bold]Summary:[/bold] {valid_count} valid, {invalid_count} invalid"
        )

        if invalid_count > 0:
            raise ValueError(f"Validation failed: {invalid_count} invalid entrypoints")
    except ValueError as e:
        console.print(RED_CROSS, f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        console.print(RED_CROSS, f"Error: {e}")
        sys.exit(2)


@cli.command(name="list-packages")
@click.pass_obj
def list_packages(console: Console) -> None:
    """List all packages that define deprecator or registry entrypoints.

    This helps you discover which packages in your environment are using
    deprecator for managing their deprecations.
    """
    try:
        deprecator_packages = list_packages_with_deprecators()
        registry_packages = list_packages_with_registries()

        if deprecator_packages:
            console.print("[bold]Packages with Deprecator Entrypoints:[/bold]")
            for name in sorted(deprecator_packages):
                console.print(f"  - {name}")
            console.print()
        else:
            console.print(
                "[yellow]No packages with deprecator entrypoints found[/yellow]"
            )

        if registry_packages:
            console.print("[bold]Packages with Registry Entrypoints:[/bold]")
            for name in sorted(registry_packages):
                console.print(f"  - {name}")
            console.print()
        else:
            console.print(
                "[yellow]No packages with registry entrypoints found[/yellow]"
            )
    except Exception as e:
        console.print(RED_CROSS, f"Error: {e}")
        sys.exit(2)


@cli.command(name="validate-validators", hidden=True)
@click.pass_obj
def validate_validators(console: Console) -> None:
    """Validate that all known validators have corresponding entrypoints.

    This is an internal command used for testing and validation.
    """
    try:
        errors = validate_known_validators()

        if not errors:
            console.print(
                GREEN_CHECK_MARK, "All known validators have corresponding entrypoints"
            )
        else:
            console.print("[red]Validator validation errors:[/red]")
            for error in errors:
                console.print(RED_CROSS, f"  {error}")
            raise ValueError(f"Validator validation failed: {len(errors)} errors")
    except ValueError as e:
        console.print(RED_CROSS, f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        console.print(RED_CROSS, f"Error: {e}")
        sys.exit(2)


def main(args: list[str] | None = None) -> None:
    """Main CLI entry point.

    Args:
        args: Command line arguments (for testing)
    """
    cli(args or sys.argv[1:], standalone_mode=False)


if __name__ == "__main__":
    main()
