"""Example of package-level deprecation setup."""

from packaging.version import Version

from deprecator import for_package

# Create a deprecator instance for your package
# For testing, we provide an explicit version since this isn't a real package
deprecator = for_package(__package__ or "mypackage", _version=Version("1.8.0"))

# Define package-wide deprecations
OLD_FEATURE_DEPRECATION = deprecator.define(
    "old_feature is deprecated, use new_feature instead",
    warn_in="2.0.0",
    gone_in="3.0.0",
)

PROCESS_DATA_DEPRECATION = deprecator.define(
    "process_data() is deprecated, use transform_data() instead",
    warn_in="1.5.0",
    gone_in="2.0.0",
)
