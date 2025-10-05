"""Basic deprecation example."""

from packaging.version import Version

from deprecator import for_package

# Get a deprecator for your package
# For testing, we provide an explicit version since "mypackage" isn't installed
deprecator = for_package("mypackage", _version=Version("2.0.0"))

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
