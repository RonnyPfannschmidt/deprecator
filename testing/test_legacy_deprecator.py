#!/usr/bin/env python
"""Tests for the deprecator module."""

from __future__ import annotations

import warnings

import pytest

from deprecator import deprecate


class TestDeprecate:
    """Test the deprecate decorator."""

    def test_deprecate_function_without_replacement(self) -> None:
        """Test that a deprecated function without replacement shows warning."""

        @deprecate()
        def old_function() -> str:
            return "hello"

        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")
            result = old_function()

        assert result == "hello"
        assert len(warning_list) == 1
        assert issubclass(warning_list[0].category, DeprecationWarning)
        assert "old_function is deprecated" in str(warning_list[0].message)

    def test_deprecate_function_with_replacement(self) -> None:
        """Test that a deprecated function with replacement shows proper warning."""

        def new_function() -> str:
            return "new hello"

        @deprecate(replacement=new_function)
        def old_function() -> str:
            return "old hello"

        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")
            result = old_function()

        assert result == "old hello"
        assert len(warning_list) == 1
        assert issubclass(warning_list[0].category, DeprecationWarning)
        warning_msg = str(warning_list[0].message)
        assert "old_function is deprecated" in warning_msg
        assert "use new_function instead" in warning_msg

    def test_deprecate_function_with_args_and_kwargs(self) -> None:
        """Test that deprecated function correctly passes args and kwargs."""

        @deprecate()
        def old_function(a: int, b: str, c: bool = True) -> tuple[int, str, bool]:
            return a, b, c

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = old_function(42, "test", c=False)

        assert result == (42, "test", False)

    def test_deprecate_preserves_function_name(self) -> None:
        """Test that the decorated function preserves its name."""

        @deprecate()
        def original_name() -> None:
            pass

        assert original_name.__name__ == "original_name"

    def test_deprecate_adds_docstring_when_none_exists(self) -> None:
        """Test that deprecation message is added as docstring when none exists."""

        @deprecate()
        def function_without_docstring() -> None:
            pass

        assert function_without_docstring.__doc__ is not None
        assert (
            "function_without_docstring is deprecated"
            in function_without_docstring.__doc__
        )

    def test_deprecate_preserves_existing_docstring(self) -> None:
        """Test that existing docstring is preserved."""

        @deprecate()
        def function_with_docstring() -> None:
            """Original docstring."""
            pass

        assert function_with_docstring.__doc__ == "Original docstring."

    def test_deprecate_function_with_return_value(self) -> None:
        """Test that return values are properly passed through."""

        @deprecate()
        def returns_value() -> int:
            return 123

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = returns_value()

        assert result == 123

    def test_deprecate_function_with_exception(self) -> None:
        """Test that exceptions are properly propagated."""

        @deprecate()
        def raises_exception() -> None:
            raise ValueError("test error")

        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            with pytest.raises(ValueError, match="test error"):
                raises_exception()

    def test_multiple_calls_show_multiple_warnings(self) -> None:
        """Test that each call to deprecated function shows a warning."""

        @deprecate()
        def old_function() -> None:
            pass

        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")
            old_function()
            old_function()

        assert len(warning_list) == 2
        for warning in warning_list:
            assert issubclass(warning.category, DeprecationWarning)

    def test_deprecate_class_method(self) -> None:
        """Test deprecating a class method."""

        class TestClass:
            @deprecate()
            def old_method(self) -> str:
                return "method result"

        instance = TestClass()

        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")
            result = instance.old_method()

        assert result == "method result"
        assert len(warning_list) == 1
        assert "old_method is deprecated" in str(warning_list[0].message)

    def test_deprecate_static_method(self) -> None:
        """Test deprecating a static method."""

        class TestClass:
            @staticmethod
            @deprecate()
            def old_static_method() -> str:
                return "static result"

        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")
            result = TestClass.old_static_method()

        assert result == "static result"
        assert len(warning_list) == 1
        assert "old_static_method is deprecated" in str(warning_list[0].message)

    def test_replacement_object_must_have_name_attribute(self) -> None:
        """Test that replacement objects must have a __name__ attribute."""

        class ReplacementWithName:
            __name__ = "replacement_name"

        replacement = ReplacementWithName()

        @deprecate(replacement=replacement)
        def old_function() -> None:
            pass

        with warnings.catch_warnings(record=True) as warning_list:
            warnings.simplefilter("always")
            old_function()

        assert "use replacement_name instead" in str(warning_list[0].message)


if __name__ == "__main__":
    pytest.main([__file__])
