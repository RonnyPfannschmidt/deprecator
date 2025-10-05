"""Example of deprecating a class."""

from package_setup import OLD_FEATURE_DEPRECATION

# Assuming we have a deprecation for legacy classes
LEGACY_CLASS_DEPRECATION = OLD_FEATURE_DEPRECATION  # Using same deprecation for example


@LEGACY_CLASS_DEPRECATION.apply
class LegacyProcessor:
    """This class is deprecated."""

    pass


class ModernProcessor:
    """The replacement for LegacyProcessor."""

    pass
