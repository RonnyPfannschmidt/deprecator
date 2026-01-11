"""Example tests for deprecations.

These tests demonstrate how to verify that:
1. Deprecated functions emit the correct warnings
2. New replacement functions don't emit warnings
"""

import pytest
from basic_deprecation import new_api, old_api


def test_deprecation_warning() -> None:
    """Test that deprecated functions emit warnings."""
    with pytest.warns(DeprecationWarning, match="old_api is deprecated"):
        result = old_api()
    assert result == "new implementation"


def test_new_api_no_warning() -> None:
    """Test that new API doesn't emit warnings."""
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("error")  # Turn warnings into errors
        result = new_api()  # Should not raise
    assert result == "new implementation"
