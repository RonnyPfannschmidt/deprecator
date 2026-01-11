"""Basic deprecation example.

This example demonstrates the core deprecator workflow:
1. Get a deprecator for your package
2. Define a deprecation with version boundaries
3. Use it in your code
"""

from packaging.version import Version

from deprecator import for_package

# Get a deprecator for your package
# NOTE: In real code, just use: deprecator = for_package("mypackage")
# The _version parameter is only used here because "mypackage" isn't installed.
deprecator = for_package("mypackage", _version=Version("2.0.0"))

# Define a deprecation with version boundaries
OLD_API_DEPRECATION = deprecator.define(
    "old_api is deprecated, use new_api instead",
    warn_in="1.0.0",  # Start warning at this version
    gone_in="3.0.0",  # Should be removed at this version
)


def old_api() -> str:
    """Deprecated API function."""
    OLD_API_DEPRECATION.warn()
    return new_api()


def new_api() -> str:
    """New API function that replaces old_api."""
    return "new implementation"
