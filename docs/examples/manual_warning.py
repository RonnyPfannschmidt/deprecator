"""Example of manual warning emission.

Use deprecation.warn() when you need conditional deprecation warnings,
such as warning only when specific parameters or code paths are used.
"""

from package_setup import OLD_FEATURE_DEPRECATION


def complex_deprecation(use_old_logic: bool = False) -> str:
    """Function with conditional deprecation.

    Args:
        use_old_logic: If True, uses deprecated code path and emits warning.

    Returns:
        Result from either old or new implementation.
    """
    if use_old_logic:
        # Only warn when the deprecated code path is actually used
        OLD_FEATURE_DEPRECATION.warn()
        return "old result"
    return "new result"
