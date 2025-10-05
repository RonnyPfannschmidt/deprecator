"""Basic deprecation example."""

from deprecator import for_package

# Get a deprecator for your package
deprecator = for_package("mypackage")

# Define a deprecation
OLD_API_DEPRECATION = deprecator.define(
    "old_api is deprecated, use new_api instead", warn_in="1.0.0", gone_in="3.0.0"
)


def old_api() -> str:
    """Deprecated API function."""
    OLD_API_DEPRECATION.warn()
    return new_api()


def new_api() -> str:
    """New API function that replaces old_api."""
    return "new implementation"
