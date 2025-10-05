"""Example of package-level deprecation setup."""

from deprecator import for_package

# Create a deprecator instance for your package
deprecator = for_package(__package__)

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
