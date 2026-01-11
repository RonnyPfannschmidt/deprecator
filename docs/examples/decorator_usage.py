"""Example of using deprecation decorators.

The @deprecation.apply decorator automatically emits the warning
when the decorated function or class is called.
"""

from package_setup import PROCESS_DATA_DEPRECATION


@PROCESS_DATA_DEPRECATION.apply
def process_data(data: str) -> str:
    """Old data processing function - deprecated."""
    return transform_data(data)


def transform_data(data: str) -> str:
    """New data transformation function - use this instead."""
    return data.upper()
