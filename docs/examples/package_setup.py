"""Example of package-level deprecation setup.

This is how you'd typically set up deprecator in your package's
_deprecations.py file. All deprecations are defined in one place.
"""

from packaging.version import Version

from deprecator import for_package

# Create a deprecator instance for your package
# NOTE: In real code, just use: deprecator = for_package(__package__)
# The _version parameter is only used here because this isn't a real package.
deprecator = for_package(__package__ or "mypackage", _version=Version("1.8.0"))

# Define package-wide deprecations as module-level constants
OLD_FEATURE_DEPRECATION = deprecator.define(
    "old_feature is deprecated, use new_feature instead",
    warn_in="1.5.0",
    gone_in="2.0.0",
)

PROCESS_DATA_DEPRECATION = deprecator.define(
    "process_data() is deprecated, use transform_data() instead",
    warn_in="1.5.0",
    gone_in="2.0.0",
)
