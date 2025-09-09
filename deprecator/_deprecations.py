from __future__ import annotations

from ._registry import default_registry

deprecator = default_registry.for_package("deprecator")

LEGACY_DEPRECATE = deprecator.define(
    "deprecator.deprecate is deprecated",
    replace_with="MY_WARNING_DEFINITION.apply",
    gone_in="2.0.0",
)
