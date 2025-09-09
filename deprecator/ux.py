"""User experience utilities for deprecator."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console

from ._rich_display import (
    print_deprecations_table,
)
from ._warnings import (
    WARNING_TYPES,
    get_warning_types,
)

if TYPE_CHECKING:
    from ._deprecator import Deprecator


def print_deprecations(
    deprecator: Deprecator,
    *,
    console: Console | None = None,
    pending: bool = False,
    active: bool = True,
    expired: bool = True,
) -> None:
    """Print a rich table showing registered deprecations for a Deprecator instance.


    :param deprecator: The Deprecator instance to display deprecations for
    :param console: Optional Rich Console instance to use for printing.
    :param pending: Whether to include pending deprecations
    :param active: Whether to include active deprecations
    :param expired: Whether to include expired deprecations
    """
    # Build warning types set based on flags
    warning_types: WARNING_TYPES = get_warning_types(
        pending=pending, active=active, expired=expired
    )

    # Use the implementation from _rich_display
    print_deprecations_table(
        deprecator,
        warning_types=warning_types,
        console=console,
    )
