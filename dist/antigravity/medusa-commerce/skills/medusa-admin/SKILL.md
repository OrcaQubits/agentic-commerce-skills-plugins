---
name: medusa-admin
description: >
  Extend the Medusa v2 admin dashboard — widgets injected at zones, custom UI
  routes, Medusa UI components, and Admin API integration. Use when customizing
  the admin interface.
---

# Medusa v2 Admin Dashboard Extensions

## Before writing code

**Fetch live docs**:
1. Fetch `https://docs.medusajs.com/learn/fundamentals/admin/widgets` for widget development
2. Web-search `site:docs.medusajs.com admin UI routes` for custom admin pages
3. Web-search `site:docs.medusajs.com admin widget injection zones` for available zones
4. Web-search `site:docs.medusajs.com medusa UI components` for component library
5. Web-search `site:docs.medusajs.com admin API client` for making API calls from admin

## Admin Extension Concept

Medusa v2 admin is a React-based SPA that supports two extension types:
- **Widgets** -- injected into predefined zones on existing admin pages
- **UI Routes** -- entirely new pages accessible via the admin sidebar or navigation

Extensions live in `src/admin/` and are automatically discovered and bundled.

## Admin Extension Directory Structure

| Directory | Purpose |
|-----------|---------|
| `src/admin/widgets/` | Widget components (e.g., `product-custom-widget.tsx`) |
| `src/admin/routes/custom-page/page.tsx` | Custom admin page |
| `src/admin/routes/custom-page/[id]/page.tsx` | Dynamic route page |
| `src/admin/lib/` | Shared API utilities |

## Widgets

### Widget Injection Zones

| Zone | Location | Use Case |
|------|----------|----------|
| `product.details.before` | Product detail, top | Custom product fields |
| `product.details.after` | Product detail, bottom | Related data display |
| `product.details.side.before` | Product detail sidebar, top | Quick actions |
| `product.details.side.after` | Product detail sidebar, bottom | Metadata display |
| `order.details.before` | Order detail, top | Custom order info |
| `order.details.after` | Order detail, bottom | Fulfillment tracking |
| `order.details.side.before` | Order sidebar, top | Order tags |
| `order.details.side.after` | Order sidebar, bottom | Order notes |
| `customer.details.before` | Customer detail, top | Loyalty info |
| `customer.details.after` | Customer detail, bottom | Purchase history |

> **Fetch live docs** for the complete zone list -- zones are added with each Medusa release.

### Widget Definition Skeleton

```typescript
// src/admin/widgets/product-custom-widget.tsx
// Fetch live docs for defineWidgetConfig and zone types
import { defineWidgetConfig } from "@medusajs/admin-sdk"
import { Container, Heading } from "@medusajs/ui"

const ProductCustomWidget = ({ data }) => (
  <Container><Heading level="h2">Custom</Heading></Container>
)
```

```typescript
export const config = defineWidgetConfig({ zone: "product.details.after" })
export default ProductCustomWidget
```

### Widget Props

| Prop | Type | Description |
|------|------|-------------|
| `data` | Entity object | The entity displayed on the page (product, order, etc.) |

The `data` prop shape depends on the zone -- a `product.details.*` zone receives the product object.

## Custom UI Routes

### Route File Convention

| File Path | Admin URL |
|-----------|-----------|
| `src/admin/routes/custom-page/page.tsx` | `/app/custom-page` |
| `src/admin/routes/custom-page/[id]/page.tsx` | `/app/custom-page/:id` |
| `src/admin/routes/settings/my-setting/page.tsx` | `/app/settings/my-setting` |

### Route Page Skeleton

```typescript
// src/admin/routes/custom-page/page.tsx
// Fetch live docs for defineRouteConfig
import { defineRouteConfig } from "@medusajs/admin-sdk"
import { Container, Heading } from "@medusajs/ui"

const CustomPage = () => (
  <Container><Heading level="h1">Custom Page</Heading></Container>
)
```

```typescript
export const config = defineRouteConfig({ label: "Custom Page" })
export default CustomPage
// Fetch live docs for icon options in defineRouteConfig
```

### Adding Sidebar Navigation

The `defineRouteConfig` with a `label` property automatically adds the page to the admin sidebar. Pages under `routes/settings/` appear in the Settings section.

## Medusa UI Component Library

| Category | Key Components |
|----------|---------------|
| Layout | `Container`, `Drawer`, `FocusModal`, `Prompt` |
| Typography | `Heading`, `Text`, `Label`, `Code` |
| Forms | `Input`, `Select`, `Checkbox`, `RadioGroup`, `Switch`, `Textarea`, `DatePicker` |
| Data | `Table`, `Badge`, `StatusBadge`, `Avatar`, `Copy` |
| Actions | `Button`, `IconButton`, `DropdownMenu`, `CommandBar` |
| Feedback | `Toast`, `Alert`, `ProgressBar`, `Spinner` |
| Navigation | `Tabs`, `Breadcrumbs` |

> **Fetch live docs**: Web-search `site:docs.medusajs.com @medusajs/ui components` for the full component catalog and prop APIs.

## Making Admin API Calls

### Using the Medusa JS SDK

```typescript
// Fetch live docs for admin SDK client setup
// Use the SDK or fetch wrapper provided by Medusa admin
// Fetch live docs for createAdminClient or useAdminXxx hooks
const { data } = await sdk.admin.product.list()
```

### Using fetch with Admin Auth

Admin extensions run within the authenticated admin session. Use the built-in `fetch` wrapper or the JS SDK which automatically includes session credentials.

## Admin API Scopes

| Scope | Endpoints | Requires |
|-------|-----------|----------|
| Store API (`/store/*`) | Storefront operations | Optional customer auth |
| Admin API (`/admin/*`) | Back-office operations | Admin user session |
| Custom (`/admin/custom/*`) | Custom admin endpoints | Admin auth middleware |

Custom admin pages typically call `/admin/*` endpoints which require the admin session token.

## Limitations

| Limitation | Workaround |
|-----------|-----------|
| Cannot modify core admin pages | Use widgets injected at zones |
| Cannot override core admin routes | Create new routes with custom functionality |
| Limited styling control | Use `@medusajs/ui` components for consistency |
| No server-side rendering | Admin is a client-side SPA |
| Bundle size | Keep widget dependencies minimal |

## Best Practices

- Use `@medusajs/ui` components for visual consistency with the core admin
- Keep widgets focused on a single concern -- use multiple widgets for multiple features
- Use custom UI routes for complex multi-step interfaces
- Call the Admin API through the JS SDK or built-in fetch wrapper -- do not hardcode URLs
- Type your widget `data` prop for type safety
- Place shared utilities in `src/admin/lib/` for reuse across widgets and routes

## Testing Admin Extensions

| Approach | Description |
|----------|-------------|
| Storybook | Render components in isolation with `@medusajs/ui` |
| Browser testing | Run `npx medusa develop` and manually verify |
| Unit tests | Test logic functions separately from React rendering |

Fetch the Medusa admin extension documentation for exact injection zone names, component props, and route configuration options before implementing.
