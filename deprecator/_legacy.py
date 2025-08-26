#!/usr/bin/env python
"""Helps to deprecate your old code."""

from __future__ import annotations

import warnings
from collections.abc import Callable
from functools import wraps

from typing_extensions import ParamSpec, Protocol, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

warnings.simplefilter("always", DeprecationWarning)


class Decorator(Protocol):
    def __call__(self, fun: Callable[P, R]) -> Callable[P, R]: ...


class HasName(Protocol):
    __name__: str


def deprecate(replacement: HasName | None = None) -> Decorator:
    """Prints a deprecation warning when a function is called.

    Argument:
      replacement (func): The func which replaces the deprecated func.

    Usage:
      >>> from deprecator import deprecate
      >>> def bar(): print("hello")
      >>> @deprecate(replacement=bar)
      >>> def foo(): print("hello")
      >>> foo()
      DeprecationWarning: foo is deprecated; use bar instead.
      hello
    """

    def outer(fun: Callable[P, R]) -> Callable[P, R]:
        msg = f"{fun.__name__} is deprecated"
        if replacement is not None:
            msg += f"; use {replacement.__name__} instead."
        if fun.__doc__ is None:
            fun.__doc__ = msg

        @wraps(fun)
        def inner(*args: P.args, **kwargs: P.kwargs) -> R:
            warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
            return fun(*args, **kwargs)

        return inner

    return outer


if __name__ == "__main__":
    print(deprecate.__doc__)
