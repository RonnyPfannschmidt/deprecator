"""Example tests for deprecations."""

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
        warnings.simplefilter("error")
        result = new_api()  # Should not raise if no warnings
    assert result == "new implementation"
