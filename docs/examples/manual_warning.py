"""Example of manual warning emission."""

from package_setup import OLD_FEATURE_DEPRECATION


def complex_deprecation(use_old_logic: bool = False) -> str:
    """Function with conditional deprecation."""
    if use_old_logic:
        OLD_FEATURE_DEPRECATION.warn()
        # Old implementation path
        return "old result"
    # New implementation path
    return "new result"
