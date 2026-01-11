"""Complete test example for deprecations.

A more comprehensive example showing how to test:
- Decorator-based deprecations
- The deprecation message content
- That new APIs remain warning-free
"""

import warnings

from decorator_usage import process_data, transform_data


def test_process_data_deprecated() -> None:
    """Test that process_data emits deprecation warning."""
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        result = process_data("hello")

        # Check that we got exactly one warning
        assert len(w) == 1
        assert "deprecated" in str(w[0].message).lower()

    assert result == "HELLO"


def test_transform_data_no_warning() -> None:
    """Test that transform_data doesn't emit warnings."""
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        result = transform_data("hello")  # Should not raise
    assert result == "HELLO"
