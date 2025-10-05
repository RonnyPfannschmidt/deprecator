# Registry Management

::: deprecator.DeprecatorRegistry
    options:
      show_source: true
      show_root_heading: true
      members:
        - __init__
        - for_package

::: deprecator.registry_for
    options:
      show_source: true

## Overview

The registry system allows frameworks to group and manage deprecations from multiple contributing packages. A framework declares a registry, and packages that contribute to that framework use the registry to group their related deprecations together.

## Core Concept

Registries solve the problem of tracking deprecations across an ecosystem:

- **Framework declares a registry**: The main framework creates a registry for its ecosystem
- **Contributing packages use the registry**: Packages that extend the framework register their deprecations with the framework's registry
- **Centralized tracking**: All deprecations related to the framework can be tracked and managed together

## Usage Examples

### Hypothetical Web Framework Example

Imagine a web framework called "WebKit" with various extension packages:

```python
# webkit/_deprecations.py - Main framework declares the registry
from deprecator import registry_for

# Create the WebKit ecosystem registry
webkit_registry = registry_for(framework="webkit")
webkit_deprecator = webkit_registry.for_package("webkit")

# WebKit's own deprecations
OLD_ROUTER_DEPRECATION = webkit_deprecator.define(
    "Router.add_route() is deprecated, use Router.route()",
    warn_in="2.0.0",
    gone_in="3.0.0"
)
```

```python
# webkit_orm/_deprecations.py - ORM extension uses WebKit's registry
from deprecator import registry_for

# Join the WebKit ecosystem
webkit_registry = registry_for(framework="webkit")
orm_deprecator = webkit_registry.for_package("webkit-orm")

# This deprecation is grouped with WebKit's ecosystem
OLD_QUERY_DEPRECATION = orm_deprecator.define(
    "Query.filter_by() is deprecated, use Query.where()",
    warn_in="1.5.0",
    gone_in="2.0.0"
)
```

```python
# webkit_auth/_deprecations.py - Auth extension
webkit_registry = registry_for(framework="webkit")
auth_deprecator = webkit_registry.for_package("webkit-auth")

LEGACY_LOGIN_DEPRECATION = auth_deprecator.define(
    "login_user() is deprecated, use authenticate()",
    warn_in="0.8.0",
    gone_in="1.0.0"
)
```

### Hypothetical Data Science Library Example

```python
# datasci/_deprecations.py - Core data science library
from deprecator import registry_for

datasci_registry = registry_for(framework="datasci")
datasci_deprecator = datasci_registry.for_package("datasci")
```

```python
# datasci_viz/_deprecations.py - Visualization plugin
datasci_registry = registry_for(framework="datasci")
viz_deprecator = datasci_registry.for_package("datasci-viz")

OLD_PLOT_DEPRECATION = viz_deprecator.define(
    "plot_histogram() is deprecated, use hist()",
    warn_in="2.0.0",
    gone_in="3.0.0"
)
```

```python
# datasci_ml/_deprecations.py - Machine learning plugin
datasci_registry = registry_for(framework="datasci")
ml_deprecator = datasci_registry.for_package("datasci-ml")

OLD_MODEL_DEPRECATION = ml_deprecator.define(
    "LinearModel is deprecated, use LinearRegressor",
    warn_in="1.0.0",
    gone_in="2.0.0"
)
```

## Benefits of Using Registries

### 1. Ecosystem Coordination

All packages in an ecosystem can coordinate their deprecation timelines:

```python
# Hypothetical: Check all WebKit ecosystem deprecations
webkit_registry = registry_for(framework="webkit")

# Framework maintainers can track deprecations across the ecosystem
# (Implementation details depend on the actual API)
```

### 2. Consistent User Experience

Users of the framework see consistent deprecation patterns across all related packages.

### 3. Framework-Wide Migration Planning

Framework maintainers can plan major releases considering all ecosystem deprecations.

## Registry vs Direct Package Access

There are two ways to get a deprecator:

```python
from deprecator import for_package, registry_for

# Direct access (uses default registry internally)
deprecator = for_package("mypackage")

# Via a specific registry (for framework ecosystems)
myframework_registry = registry_for(framework="myframework")
deprecator = myframework_registry.for_package("mypackage")
```

**Use registries when:**
- Your package is part of a framework ecosystem
- You want to group related deprecations together
- You need centralized deprecation management

**Use direct access when:**
- Your package is standalone
- You don't need ecosystem-wide coordination

## Entry Point Integration

Frameworks can expose their registry via entry points for discovery:

```toml
# Hypothetical framework's pyproject.toml
[project.entry-points."deprecator.registry"]
myframework = "myframework._deprecations:framework_registry"
```

This allows automatic discovery:

```python
from importlib.metadata import entry_points

# Find available registries
eps = entry_points(group="deprecator.registry")
for ep in eps:
    registry = ep.load()
    # Use the registry for framework-specific deprecations
```

## Default Registry

For packages not part of a specific framework:

```python
from deprecator._registry import default_registry

# Standalone package uses the default registry
my_deprecator = default_registry.for_package("mypackage")
```

The `for_package()` function uses the default registry internally:

```python
from deprecator import for_package

# This is equivalent to using default_registry.for_package()
deprecator = for_package("mypackage")
```

## Best Practices

1. **Frameworks declare registries**: Only frameworks should create new registries
2. **Extensions use framework registries**: Contributing packages should use their framework's registry
3. **Consistent naming**: Use the framework's canonical name for the registry
4. **Document registry usage**: Framework docs should explain how extensions should use their registry
5. **Standalone packages**: Use `for_package()` directly if not part of a framework

## Caching Behavior

The registry system provides caching at multiple levels:

```python
# Registry instances are created per framework
registry1 = registry_for(framework="myframework")
registry2 = registry_for(framework="myframework")
# Note: These may not be the same instance depending on implementation

# Deprecator instances are cached per registry
dep1 = registry1.for_package("mypackage")
dep2 = registry1.for_package("mypackage")
assert dep1 is dep2  # Same instance
```

## Thread Safety

Registry operations are thread-safe through functools.lru_cache, allowing concurrent access from multiple packages during import.
