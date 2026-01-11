# Registry Management

!!! note "For Framework Developers"
    This section is for developers building **frameworks or plugin ecosystems**.
    If you're just adding deprecations to your own package, use `for_package()` directly—see the [Getting Started](../getting-started.md) guide.

## When Do You Need a Registry?

Most packages don't need a registry. Use `for_package()` directly:

```python
from deprecator import for_package

deprecator = for_package("mypackage")
```

You need a **registry** when you're building a framework where:

- Multiple packages contribute to your ecosystem (plugins, extensions)
- You want to track deprecations across all contributing packages together
- You need coordinated deprecation timelines across the ecosystem

## API Reference

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

## Core Concept

Registries solve the problem of tracking deprecations across an ecosystem:

```
┌─────────────────────────────────────────────────────┐
│                 Framework Registry                   │
│                  (e.g., "myframework")              │
├─────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  core pkg   │  │  plugin A   │  │  plugin B   │ │
│  │ deprecator  │  │ deprecator  │  │ deprecator  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────┘
```

- **Framework declares a registry**: The main framework creates a registry for its ecosystem
- **Contributing packages use the registry**: Plugins register their deprecations with the framework's registry
- **Centralized tracking**: All deprecations can be tracked and managed together

## Usage Examples

### Framework: Declare a Registry

```python
# myframework/_deprecations.py - Main framework declares the registry
from deprecator import registry_for

# Create the ecosystem registry
framework_registry = registry_for(framework="myframework")
framework_deprecator = framework_registry.for_package("myframework")

# Framework's own deprecations
OLD_ROUTER = framework_deprecator.define(
    "Router.add_route() is deprecated, use Router.route()",
    warn_in="2.0.0",
    gone_in="3.0.0"
)
```

### Plugin: Join the Ecosystem

```python
# myframework_auth/_deprecations.py - Auth plugin uses framework's registry
from deprecator import registry_for

# Join the framework ecosystem
framework_registry = registry_for(framework="myframework")
auth_deprecator = framework_registry.for_package("myframework-auth")

# This deprecation is grouped with the framework's ecosystem
LEGACY_LOGIN = auth_deprecator.define(
    "login_user() is deprecated, use authenticate()",
    warn_in="0.8.0",
    gone_in="1.0.0"
)
```

## Entry Point Integration

Frameworks can expose their registry via entry points for automatic discovery:

```toml
# Framework's pyproject.toml
[project.entry-points."deprecator.registry"]
myframework = "myframework._deprecations:framework_registry"

# Plugin's pyproject.toml
[project.entry-points."deprecator.deprecator"]
myframework-auth = "myframework_auth._deprecations:auth_deprecator"
```

This enables:

```bash
# Show all deprecations in the framework ecosystem
deprecator show-registry myframework
```

## Benefits

1. **Ecosystem Coordination**: All packages coordinate deprecation timelines
2. **Consistent User Experience**: Users see consistent deprecation patterns
3. **Framework-Wide Planning**: Plan major releases considering all ecosystem deprecations
4. **Centralized CLI**: Use `deprecator show-registry` to inspect all deprecations

## Caching Behavior

Registry operations are cached for performance:

```python
# Deprecator instances are cached per registry
dep1 = registry.for_package("mypackage")
dep2 = registry.for_package("mypackage")
assert dep1 is dep2  # Same instance
```

Registry operations are thread-safe through `functools.lru_cache`, allowing concurrent access during import.

## Best Practices

1. **Only frameworks create registries** - Plugins should use their framework's registry
2. **Use consistent naming** - Registry name should match framework's canonical name
3. **Document for plugin authors** - Explain how plugins should use the registry
4. **Standalone packages don't need registries** - Just use `for_package()` directly
