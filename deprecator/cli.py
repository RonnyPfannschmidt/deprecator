"""Command line interface for deprecator."""

from __future__ import annotations

import argparse

from rich.console import Console

from ._registry import default_registry
from .ux import print_deprecations


def print_deprecator(package_name: str, console: Console | None = None) -> None:
    """Print deprecations table for a specific package.

    Args:
        package_name: Name of the package to print deprecations for
    """
    deprecator = default_registry.for_package(package_name)
    print_deprecations(deprecator, console=console)


def print_all_deprecators(console: Console | None = None) -> None:
    """Print deprecations tables for all deprecators in the default registry."""
    for deprecator in default_registry._deprecators.values():
        print_deprecations(deprecator, console=console)
        print()  # Add blank line between tables


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="deprecator", description="Print deprecation tables"
    )

    parser.add_argument(
        "package_name",
        nargs="?",
        help=(
            "Package name to show deprecations for. "
            "If not provided, shows all packages."
        ),
    )

    return parser


def main(args: list[str] | None = None, console: Console | None = None) -> None:
    """Main CLI entry point."""
    console = console or Console()
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    if parsed_args.package_name:
        print_deprecator(parsed_args.package_name, console=console)
    else:
        print_all_deprecators(console=console)


if __name__ == "__main__":
    main()
