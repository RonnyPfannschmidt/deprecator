"""Command line interface for deprecator.

Exit codes:
- 0: Success, no issues
- 1: Expired deprecations or validation failures found
- 2: Configuration or usage errors
"""

from __future__ import annotations

import argparse
import inspect
import sys

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
    for deprecator in registry._deprecators.values():
        print_deprecations(deprecator, console=console)
        print()  # Add blank line between tables


def print_package_deprecators(package_name: str, console: Console) -> None:
    """Print all deprecators defined by a specific package.

    Args:
        package_name: Name of the package to show deprecators for
        console: Console for output
    """
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


def validate_package(package_name: str, console: Console) -> None:
    """Validate all entrypoints defined by a specific package.

    Args:
        package_name: Name of the package to validate
        console: Console for output
    """
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
            console.print(RED_CROSS, "deprecator:{name}: {'; '.join(errors)}")
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
    console.print(f"[bold]Summary:[/bold] {valid_count} valid, {invalid_count} invalid")

    if invalid_count > 0:
        raise ValueError(f"Validation failed: {invalid_count} invalid entrypoints")


def validate_validators(console: Console) -> None:
    """Validate that all known validators have corresponding entrypoints.

    Args:
        console: Console for output
    """
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


def list_packages_with_entrypoints(console: Console) -> None:
    """List all packages that define deprecator or registry entrypoints.

    Args:
        console: Console for output
    """
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


def _handle_show_command(
    console: Console,
    package_name: str | None = None,
    registry: DeprecatorRegistry | None = None,
    **kwargs: object,
) -> None:
    """Handle the show command with conditional logic for package_name."""
    if package_name:
        print_deprecator(
            package_name=package_name, console=console, registry=registry, **kwargs
        )
    else:
        print_all_deprecators(console=console, registry=registry, **kwargs)


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
        "show-registry", help="Show deprecations for a package from default registry"
    )
    show_parser.add_argument(
        "package_name",
        nargs="?",
        help=(
            "Package name to show deprecations for. "
            "If not provided, shows all packages from default registry."
        ),
    )
    show_parser.set_defaults(func=_handle_show_command)

    # Show all deprecators from a package
    package_parser = subparsers.add_parser(
        "show-package", help="Show all deprecators defined by a specific package"
    )
    package_parser.add_argument("package_name", help="Name of the package")
    package_parser.set_defaults(func=print_package_deprecators)

    # Validate package entrypoints
    validate_parser = subparsers.add_parser(
        "validate-package",
        help="Validate all entrypoints defined by a specific package",
    )
    validate_parser.add_argument("package_name", help="Name of the package to validate")
    validate_parser.set_defaults(func=validate_package)

    # List packages command
    list_parser = subparsers.add_parser(
        "list-packages",
        help="List all packages that define deprecator or registry entrypoints",
    )
    list_parser.set_defaults(func=list_packages_with_entrypoints)

    # Validate validators command
    validate_validators_parser = subparsers.add_parser(
        "validate-validators",
        help="Validate that all known validators have corresponding entrypoints",
    )
    validate_validators_parser.set_defaults(func=validate_validators)

    # Init command
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize deprecator for the current project",
    )
    init_parser.set_defaults(func=init_deprecator)

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

    # Get the handler function
    handler_func = parsed_args.func

    # Build kwargs with all available parameters
    all_kwargs = {**vars(parsed_args), "console": console, "registry": registry}
    # Remove argparse-specific fields that aren't function parameters
    all_kwargs.pop("func", None)
    all_kwargs.pop("command", None)

    # Filter kwargs to only include parameters the function accepts
    sig = inspect.signature(handler_func)
    handler_kwargs = {
        key: value for key, value in all_kwargs.items() if key in sig.parameters
    }

    # Dispatch to the appropriate handler with error handling
    try:
        handler_func(**handler_kwargs)
    except ValueError as e:
        # Validation failures or expired deprecations
        console.print(RED_CROSS, f"Error: {e}")
        sys.exit(1)
    except (SystemExit, KeyboardInterrupt):
        # Pass through system exits and keyboard interrupts
        raise
    except Exception as e:
        # Configuration or other errors
        console.print(RED_CROSS, f"Error: {e}")
        sys.exit(2)


if __name__ == "__main__":
    main()
