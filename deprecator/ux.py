"""User experience utilities for deprecator."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console

from ._rich_display import (
    ACTIVE_WARNINGS,
    ERROR_WARNINGS,
    PENDING_WARNINGS,
    print_deprecations_table,
)
from ._warnings import (
    DeprecatorWarningMixing,
)

if TYPE_CHECKING:
    from ._deprecator import Deprecator


def print_deprecations(
    deprecator: Deprecator,
    *,
    console: Console | None = None,
    pending: bool = True,
    active: bool = True,
    expired: bool = True,
) -> None:
    """Print a rich table showing registered deprecations for a Deprecator instance.

    Args:
        deprecator: The Deprecator instance to display deprecations for
        console: Rich Console instance to use for printing. If None, creates a new one.
        pending: Whether to include pending deprecations (warn_in > current_version)
        active: Whether to include active deprecations (warn_in <= current_version < gone_in)
        expired: Whether to include expired deprecations (gone_in <= current_version)
    """
    # Build warning types set based on flags
    warning_types: set[type[DeprecatorWarningMixing]] = set()

    if pending:
        warning_types.update(PENDING_WARNINGS)
    if active:
        warning_types.update(
            ACTIVE_WARNINGS - ERROR_WARNINGS
        )  # Only regular deprecation warnings
    if expired:
        warning_types.update(ERROR_WARNINGS)

    # If no types selected, show nothing
    if not warning_types:
        if console is None:
            console = Console()
        console.print("No deprecation types selected for display.")
        return

    # Use the implementation from _rich_display
    print_deprecations_table(
        deprecator,
        warning_types=warning_types,
        console=console,
    )
