---
name: medusa-plugins
description: >
  Develop and publish Medusa v2 plugins — plugin structure, plugin vs module
  comparison, npm packaging, and reusable plugin template. Use when building
  distributable Medusa extensions.
---

# Medusa v2 Plugin Development

## Before writing code

**Fetch live docs**:
1. Fetch `https://docs.medusajs.com/learn/fundamentals/plugins` for plugin overview
2. Web-search `site:docs.medusajs.com plugin vs module` for comparison
3. Web-search `site:docs.medusajs.com create medusa plugin` for plugin scaffolding
4. Web-search `site:docs.medusajs.com plugin options configuration` for plugin options pattern
5. Web-search `site:docs.medusajs.com publish plugin npm` for packaging and distribution

## Plugin vs Module

| Aspect | Module | Plugin |
|--------|--------|--------|
| Scope | Single concern (data + service) | Full feature (modules + routes + workflows + admin) |
| Location | `src/modules/` in project | Separate npm package |
| Distribution | Not distributable | Published to npm |
| Configuration | Registered in `modules` array | Registered in `plugins` array |
| Contains | Models, service, loaders | Modules, API routes, workflows, subscribers, admin, links |
| Use case | Project-specific domain | Reusable across projects |

A plugin is essentially a packaged Medusa project that can contain all the same `src/` directories.

## Plugin Directory Structure

| Directory | Contents |
|-----------|----------|
| `src/modules/` | Custom modules (models, services) |
| `src/workflows/` | Workflow definitions |
| `src/api/store/`, `src/api/admin/` | API routes + `middlewares.ts` |
| `src/subscribers/` | Event subscribers |
| `src/admin/widgets/`, `src/admin/routes/` | Admin UI extensions |
| `src/links/` | Module link definitions |
| Root | `package.json`, `tsconfig.json`, `README.md` |

A plugin mirrors the standard Medusa `src/` directory structure — all conventions apply.

## Plugin Definition

The plugin's `package.json` must include specific fields:

### package.json Key Fields

| Field | Value | Purpose |
|-------|-------|---------|
| `name` | `medusa-plugin-my-feature` | npm package name |
| `main` | `./dist/index.js` | Compiled entry point |
| `types` | `./dist/index.d.ts` | TypeScript declarations |
| `files` | `["dist", "!dist/**/*.map"]` | Included in npm package |
| `keywords` | `["medusa-plugin"]` | Discoverability |
| `peerDependencies` | `@medusajs/framework` | Medusa version compatibility |

### Plugin Entry Point

```typescript
// src/index.ts
// Fetch live docs for plugin export shape
// Plugin entry exports nothing directly --
// Medusa discovers modules, routes, etc. by convention
export default {}
```

## Plugin Options

Plugins receive configuration options from the consuming project:

### Consuming a Plugin

```typescript
// In consuming project's medusa-config.ts plugins array
// Fetch live docs for plugin registration options
{
  resolve: "medusa-plugin-my-feature",
  options: { apiKey: process.env.MY_FEATURE_API_KEY },
}
```

### Accessing Options in Plugin Code

```typescript
// In a plugin loader or service
// Fetch live docs for accessing plugin options from container
// Options are injected via the module/plugin options mechanism
```

## Build and Compilation

| Step | Command | Purpose |
|------|---------|---------|
| Build | `tsc` or `tsup` | Compile TypeScript to `dist/` |
| Watch | `tsc --watch` | Development rebuild on changes |
| Clean | `rm -rf dist` | Remove compiled output |
| Pack | `npm pack` | Create tarball for testing |

## Local Development with npm link

| Step | Command | Context |
|------|---------|---------|
| 1. Build plugin | `npm run build` | In plugin directory |
| 2. Create link | `npm link` | In plugin directory |
| 3. Link in project | `npm link medusa-plugin-my-feature` | In Medusa project |
| 4. Register | Add to `plugins` in `medusa-config.ts` | In Medusa project |
| 5. Migrate | `npx medusa db:migrate` | In Medusa project |

## Plugin Testing

| Approach | Description |
|----------|-------------|
| Unit tests | Test services, workflow steps in isolation |
| Integration tests | Use `medusa-test-utils` to spin up a test Medusa instance |
| Local linking | Link plugin into a real Medusa project and test manually |
| CI pipeline | Build + unit tests on every push |

## Publishing to npm

### Pre-publish Checklist

| Check | Why |
|-------|-----|
| Build succeeds | Consumers need compiled JS |
| `files` in package.json | Only ship `dist/`, not `src/` |
| `peerDependencies` set | Avoid version conflicts |
| README with install instructions | Developer experience |
| `.npmignore` or `files` field | Exclude tests, config, etc. |
| License field set | Legal clarity |
| Version follows semver | Compatibility signals |

### Publishing Commands

```bash
npm version patch   # or minor / major
npm publish --access public
# Fetch live docs for Medusa plugin registry conventions
```

## Naming Conventions

| Convention | Example |
|-----------|---------|
| npm package name | `medusa-plugin-my-feature` |
| Module key inside plugin | `my-feature` |
| API route prefix | `/store/my-feature`, `/admin/my-feature` |
| Admin widget files | `src/admin/widgets/my-feature-widget.tsx` |

## Best Practices

- Follow the `medusa-plugin-*` naming convention for npm discoverability
- Keep `peerDependencies` on `@medusajs/framework` and `@medusajs/medusa` -- do not bundle them
- Ship only compiled output (`dist/`) -- never ship `src/` or test files
- Include TypeScript declarations for consuming projects to get type safety
- Document all plugin options in your README with required vs optional markers
- Test with `npm link` against a real Medusa project before publishing
- Use semantic versioning -- breaking changes to options or models require a major bump

Fetch the Medusa plugin documentation for exact project structure, build configuration, and publishing requirements before implementing.
