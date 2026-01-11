"""Example of deprecating a class.

Use @deprecation.apply on classes to warn when they are instantiated.
"""

from package_setup import OLD_FEATURE_DEPRECATION


@OLD_FEATURE_DEPRECATION.apply
class LegacyProcessor:
    """This class is deprecated - use ModernProcessor instead."""

    def process(self, data: str) -> str:
        return data.lower()


class ModernProcessor:
    """The modern replacement for LegacyProcessor."""

    def process(self, data: str) -> str:
        return data.lower()
