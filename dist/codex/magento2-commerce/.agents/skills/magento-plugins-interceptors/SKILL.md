---
name: magento-plugins-interceptors
description: >
  Implement Magento 2 plugins (interceptors) — before, after, and around
  methods for modifying class behavior without inheritance. Use when extending
  core or third-party module functionality.
---

# Magento 2 Plugins (Interceptors)

## Before writing code

**Fetch live docs**: Fetch `https://developer.adobe.com/commerce/php/development/components/plugins/` for the official plugins guide with exact method signatures and limitations.

## Conceptual Architecture

### What Plugins Do

Plugins intercept public method calls on any non-final class, allowing you to modify arguments, return values, or wrap entire method execution — without modifying the original class or using inheritance.

### Three Plugin Types

| Type | Method Prefix | Purpose | Receives |
|------|-------------|---------|----------|
| **Before** | `before<MethodName>` | Modify input arguments | Subject + original args |
| **After** | `after<MethodName>` | Modify return value | Subject + result (+ original args) |
| **Around** | `around<MethodName>` | Wrap entire execution | Subject + `$proceed` callable + original args |

### Before Plugin

- Method: `beforeOriginalMethod($subject, $arg1, $arg2, ...)`
- Return: array of modified arguments, or `null` to keep originals
- Executes before the original method

### After Plugin

- Method: `afterOriginalMethod($subject, $result, ...$args)`
- Return: modified result
- Executes after the original method
- Since 2.2: receives original arguments after `$result`

### Around Plugin

- Method: `aroundOriginalMethod($subject, callable $proceed, $arg1, $arg2, ...)`
- Return: whatever the method should return
- Must call `$proceed($arg1, $arg2)` to invoke the original (or skip it)
- **Use sparingly** — most cases are better served by before + after

### Plugin Declaration (di.xml)

Plugins are declared as children of a `<type>` element:
- `name` — unique plugin identifier
- `type` — fully qualified plugin class name
- `sortOrder` — execution priority (lower runs first)
- `disabled` — `true` to disable

### Execution Order

1. Before plugins execute in sortOrder (ascending)
2. Around plugin's pre-`$proceed` code
3. Original method (via `$proceed`)
4. Around plugin's post-`$proceed` code
5. After plugins execute in sortOrder (ascending)

### Limitations — Cannot Intercept

- `final` classes or `final` methods
- `__construct()` (constructor)
- `static` methods
- Non-public methods (`protected`, `private`)
- Virtual types (directly)
- Classes instantiated before the interception framework bootstraps

### Plugin Class Location

Place plugin classes in the `Plugin/` directory of your module:
```
VendorName/ModuleName/Plugin/SomePlugin.php
```

## Best Practices

- Prefer before/after over around — around is harder to debug
- Always call `$proceed` in around plugins unless intentionally skipping
- Use descriptive plugin names to avoid conflicts
- Set appropriate sortOrder when multiple plugins target the same method
- Check if a before or after plugin can achieve the goal before using around
- Test with other modules' plugins to verify sortOrder interactions

Fetch the plugins documentation for exact method signatures, the latest limitations list, and any changes in recent Magento versions before implementing.
