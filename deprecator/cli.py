"""Command line interface for deprecator."""

from __future__ import annotations

import argparse
import sys

from rich.console import Console

from ._entrypoints import (
    find_deprecators_for_package,
    list_packages_with_deprecators,
    list_packages_with_registries,
    validate_known_validators,
    validate_package_entrypoints,
)
from ._registry import DeprecatorRegistry, default_registry
from .ux import print_deprecations


def print_deprecator(
    package_name: str,
    console: Console | None = None,
    registry: DeprecatorRegistry | None = None,
) -> None:
    """Print deprecations table for a specific package.

    Args:
        package_name: Name of the package to print deprecations for
        console: Optional console for output
        registry: Optional registry to use (defaults to default_registry)
    """
    registry = registry or default_registry
    try:
        deprecator = registry.for_package(package_name)
        print_deprecations(deprecator, console=console)
    except Exception as e:
        console = console or Console(stderr=True)
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


def print_all_deprecators(
    console: Console | None = None, registry: DeprecatorRegistry | None = None
) -> None:
    """Print deprecations tables for all deprecators in a registry.

    Args:
        console: Optional console for output
        registry: Optional registry to use (defaults to default_registry)
    """
    registry = registry or default_registry
    for deprecator in registry._deprecators.values():
        print_deprecations(deprecator, console=console)
        print()  # Add blank line between tables


def print_package_deprecators(
    package_name: str, console: Console | None = None
) -> None:
    """Print all deprecators defined by a specific package.

    Args:
        package_name: Name of the package to show deprecators for
    """
    console = console or Console()

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


def validate_package(package_name: str, console: Console | None = None) -> None:
    """Validate all entrypoints defined by a specific package.

    Args:
        package_name: Name of the package to validate
    """
    console = console or Console()

    try:
        import importlib.metadata

        importlib.metadata.distribution(package_name)
    except importlib.metadata.PackageNotFoundError:
        console.print(f"[red]Package '{package_name}' not found[/red]")
        sys.exit(1)

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
            console.print(f"[green]✓[/green] deprecator:{name}")
            valid_count += 1
        else:
            console.print(f"[red]✗[/red] deprecator:{name}: {'; '.join(errors)}")
            invalid_count += 1

    # Check registry entrypoints
    for name, errors in sorted(results["registry"].items()):
        if not errors:
            console.print(f"[green]✓[/green] registry:{name}")
            valid_count += 1
        else:
            console.print(f"[red]✗[/red] registry:{name}: {'; '.join(errors)}")
            invalid_count += 1

    console.print()
    console.print(f"[bold]Summary:[/bold] {valid_count} valid, {invalid_count} invalid")

    if invalid_count > 0:
        sys.exit(1)


def validate_validators(console: Console | None = None) -> None:
    """Validate that all known validators have corresponding entrypoints."""
    console = console or Console()

    errors = validate_known_validators()

    if not errors:
        console.print(
            "[green]✓[/green] All known validators have corresponding entrypoints"
        )
    else:
        console.print("[red]Validator validation errors:[/red]")
        for error in errors:
            console.print(f"  [red]✗[/red] {error}")
        sys.exit(1)


def list_packages_with_entrypoints(console: Console | None = None) -> None:
    """List all packages that define deprecator or registry entrypoints."""
    console = console or Console()

    deprecator_packages = list_packages_with_deprecators()
    registry_packages = list_packages_with_registries()

    if deprecator_packages:
        console.print("[bold]Packages with Deprecator Entrypoints:[/bold]")
        for name in deprecator_packages:
            console.print(f"  - {name}")
        console.print()
    else:
        console.print("[yellow]No packages with deprecator entrypoints found[/yellow]")

    if registry_packages:
        console.print("[bold]Packages with Registry Entrypoints:[/bold]")
        for name in registry_packages:
            console.print(f"  - {name}")
        console.print()
    else:
        console.print("[yellow]No packages with registry entrypoints found[/yellow]")


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="deprecator", description="Print deprecation tables and manage entrypoints"
    )

    subparsers = parser.add_subparsers(
        dest="command", help="Available commands", required=True
    )

    # Show deprecations from default registry
    show_parser = subparsers.add_parser(
        "show", help="Show deprecations for a package from default registry"
    )
    show_parser.add_argument(
        "package_name",
        nargs="?",
        help=(
            "Package name to show deprecations for. "
            "If not provided, shows all packages from default registry."
        ),
    )

    # Show all deprecators from a package
    package_parser = subparsers.add_parser(
        "show-package", help="Show all deprecators defined by a specific package"
    )
    package_parser.add_argument("package_name", help="Name of the package")

    # Validate package entrypoints
    validate_parser = subparsers.add_parser(
        "validate-package",
        help="Validate all entrypoints defined by a specific package",
    )
    validate_parser.add_argument("package_name", help="Name of the package to validate")

    # List packages command
    subparsers.add_parser(
        "list-packages",
        help="List all packages that define deprecator or registry entrypoints",
    )

    # Validate validators command
    subparsers.add_parser(
        "validate-validators",
        help="Validate that all known validators have corresponding entrypoints",
    )

    return parser


def main(
    args: list[str] | None = None,
    console: Console | None = None,
    registry: DeprecatorRegistry | None = None,
) -> None:
    """Main CLI entry point.

    Args:
        args: Command line arguments
        console: Optional console for output
        registry: Optional registry to use (defaults to default_registry)
    """
    console = console or Console()
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Handle subcommands
    if parsed_args.command == "show":
        if parsed_args.package_name:
            print_deprecator(
                parsed_args.package_name, console=console, registry=registry
            )
        else:
            print_all_deprecators(console=console, registry=registry)
    elif parsed_args.command == "show-package":
        print_package_deprecators(parsed_args.package_name, console=console)
    elif parsed_args.command == "validate-package":
        validate_package(parsed_args.package_name, console=console)
    elif parsed_args.command == "list-packages":
        list_packages_with_entrypoints(console=console)
    elif parsed_args.command == "validate-validators":
        validate_validators(console=console)


if __name__ == "__main__":
    main()
