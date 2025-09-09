"""Rich table display utilities for deprecations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from packaging.version import Version
from rich.console import Console
from rich.table import Table

from ._warnings import (
    WARNING_TYPES,
    DeprecatorWarningMixing,
    PerPackageDeprecationWarning,
    PerPackageExpiredDeprecationWarning,
    PerPackagePendingDeprecationWarning,
    get_warning_types,
)

if TYPE_CHECKING:
    from ._deprecator import Deprecator


@dataclass(frozen=True)
class DeprecationInfo:
    """Information about a tracked deprecation."""

    warning_type: str
    message: str
    importable_name: str | None
    warn_in: Version
    gone_in: Version


def filtered_deprecations(
    deprecator: Deprecator, warning_types: WARNING_TYPES
) -> list[DeprecationInfo]:
    """Get filtered deprecations for a Deprecator instance."""
    return [
        DeprecationInfo(
            warning_type=_get_warning_type_display_name(warning),
            message=str(warning),
            importable_name=warning.find_importable_name(),
            warn_in=warning.warn_in,
            gone_in=warning.gone_in,
        )
        for warning in deprecator
        if isinstance(warning, warning_types)
    ]


def create_deprecations_table(
    deprecator: Deprecator,
    *,
    warning_types: WARNING_TYPES = get_warning_types(),  # NOQA: B008
    title: str | None = None,
) -> Table:
    """Create a rich table showing registered deprecations for a Deprecator instance.

    Args:
        deprecator: The Deprecator instance to display deprecations for
        warning_types: Set of warning types to filter by. If None, shows all types.
        title: Custom title for the table. If None, uses a default title.

    Returns:
        A Rich Table object containing the deprecation information
    """
    # Default title
    if title is None:
        title = f"Deprecations for {deprecator.name} (v{deprecator.current_version})"

    deprecations = filtered_deprecations(deprecator, warning_types)

    # Create the table
    table = Table(title=title, show_header=True, header_style="bold magenta")

    # Add columns
    table.add_column("Type", style="cyan", no_wrap=True)
    table.add_column("Message", style="white", max_width=60)
    table.add_column("Warn In", style="yellow", justify="center")
    table.add_column("Gone In", style="red", justify="center")
    table.add_column("Importable Name", style="green", no_wrap=True)

    # Add rows to the table
    for dep_info in deprecations:
        table.add_row(
            dep_info.warning_type,
            dep_info.message,
            str(dep_info.warn_in),
            str(dep_info.gone_in),
            dep_info.importable_name or "N/A",
        )

    return table


def print_deprecations_table(
    deprecator: Deprecator,
    *,
    warning_types: WARNING_TYPES = get_warning_types(),  # NOQA: B008
    title: str | None = None,
    console: Console | None = None,
) -> None:
    """Print a rich table showing registered deprecations for a Deprecator instance.

    Args:
        deprecator: The Deprecator instance to display deprecations for
        warning_types: Set of warning types to filter by. If None, shows all types.
        title: Custom title for the table. If None, uses a default title.
        console: Rich Console instance to use for printing. If None, creates a new one.
    """
    if console is None:
        console = Console()

    table = create_deprecations_table(
        deprecator, warning_types=warning_types, title=title
    )
    console.print(table)


def _get_warning_type_display_name(warning: DeprecatorWarningMixing) -> str:
    """Get a display-friendly name for the warning type."""
    if isinstance(warning, PerPackageExpiredDeprecationWarning):
        return "Error"
    elif isinstance(warning, PerPackageDeprecationWarning):
        return "Warning"
    elif isinstance(warning, PerPackagePendingDeprecationWarning):
        return "Pending"
    else:
        # Fallback to class name
        return warning.__class__.__name__
