"""Complete test example for deprecations."""

import pytest
from decorator_usage import process_data, transform_data
from package_setup import PROCESS_DATA_DEPRECATION


def test_process_data_deprecated() -> None:
    """Test that process_data emits deprecation warning."""
    with pytest.warns(
        type(PROCESS_DATA_DEPRECATION), match=str(PROCESS_DATA_DEPRECATION)
    ):
        result = process_data("hello")
    assert result == "HELLO"


def test_transform_data_no_warning() -> None:
    """Test that transform_data doesn't emit warnings."""
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        result = transform_data("hello")  # Should not raise if no warnings
    assert result == "HELLO"
