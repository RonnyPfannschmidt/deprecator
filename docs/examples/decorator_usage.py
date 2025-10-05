"""Example of using deprecation decorators."""

from package_setup import PROCESS_DATA_DEPRECATION


@PROCESS_DATA_DEPRECATION.apply
def process_data(data: str) -> str:
    """Old data processing function."""
    return transform_data(data)


def transform_data(data: str) -> str:
    """New data transformation function."""
    return data.upper()
