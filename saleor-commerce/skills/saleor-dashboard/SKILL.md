---
name: saleor-dashboard
description: Extend the Saleor Dashboard — mounting points, App Bridge actions, MacawUI components, iframe extensions, and custom views. Use when building Dashboard extensions.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Saleor Dashboard Extensions

## Before writing code

**Fetch live docs**:
1. Fetch `https://docs.saleor.io/docs/developer/extending/apps/extending-dashboard-with-apps` for Dashboard extension guide
2. Web-search `site:docs.saleor.io app bridge actions dispatch notification` for App Bridge API
3. Web-search `site:docs.saleor.io dashboard mounting points extensions` for extension points reference
4. Web-search `site:github.com saleor/macaw-ui components` for MacawUI component library
5. Web-search `site:docs.saleor.io app iframe communication` for iframe messaging patterns

## Dashboard Extension Architecture

Saleor Dashboard extensions are rendered as Apps inside iframes. The Dashboard loads your App's URL in a sandboxed iframe and communicates with it through the App Bridge messaging protocol.

| Layer | Component |
|-------|-----------|
| Dashboard | React SPA (host application) |
| Extension | Your App (rendered in an iframe) |
| Communication | App Bridge (postMessage API) |
| Styling | MacawUI component library |

## Mounting Points

Mounting points define where your App's extension appears in the Dashboard UI:

| Mounting Point | Location | Use Case |
|---------------|----------|----------|
| `PRODUCT_DETAILS_MORE_ACTIONS` | Product detail page dropdown | Product-level actions |
| `PRODUCT_OVERVIEW_CREATE` | Product list page | Custom product creation flows |
| `PRODUCT_OVERVIEW_MORE_ACTIONS` | Product list actions | Bulk product operations |
| `ORDER_DETAILS_MORE_ACTIONS` | Order detail page dropdown | Order-level actions |
| `ORDER_OVERVIEW_CREATE` | Order list page | Custom order creation flows |
| `ORDER_OVERVIEW_MORE_ACTIONS` | Order list actions | Bulk order operations |
| `CUSTOMER_DETAILS_MORE_ACTIONS` | Customer detail page | Customer-level actions |
| `CUSTOMER_OVERVIEW_CREATE` | Customer list page | Custom customer flows |
| `NAVIGATION_CATALOG` | Catalog navigation section | Custom catalog pages |
| `NAVIGATION_ORDERS` | Orders navigation section | Custom order pages |
| `NAVIGATION_CUSTOMERS` | Customers navigation section | Custom customer pages |

Mounting points are declared in the App manifest under the `extensions` array.

## Manifest Extension Fields

| Field | Type | Purpose |
|-------|------|---------|
| `label` | string | Button or menu item text |
| `mount` | string | Mounting point identifier |
| `target` | string | `APP_PAGE` (full page) or `POPUP` (modal) |
| `permissions` | string[] | Required permissions to see the extension |
| `url` | string | App URL path for this extension |

### Extension Declaration Example

```yaml
# In App manifest JSON (extensions array)
# Fetch live docs for current manifest extension shape
# label: "My Extension"
# mount: "PRODUCT_DETAILS_MORE_ACTIONS"
# target: "APP_PAGE"
# url: "/extensions/product-action"
```

## App Bridge

The App Bridge is the communication layer between the Dashboard and your iframe App:

### App Bridge Actions

| Action | Direction | Purpose |
|--------|-----------|---------|
| `dispatch` | App -> Dashboard | Trigger a Dashboard action |
| `redirect` | App -> Dashboard | Navigate the Dashboard to a URL |
| `notification` | App -> Dashboard | Show a toast notification |
| `handshake` | Dashboard -> App | Initial connection with context data |
| `theme` | Dashboard -> App | Current Dashboard theme (light/dark) |
| `token` | Dashboard -> App | JWT token for authenticated API calls |
| `response` | Dashboard -> App | Result of a dispatched action |

### Notification Types

| Type | Appearance |
|------|-----------|
| `success` | Green toast -- operation completed |
| `error` | Red toast -- operation failed |
| `warning` | Yellow toast -- caution needed |
| `info` | Blue toast -- informational message |

### App Bridge Setup

```typescript
// Fetch live docs for current App Bridge initialization
import { useAppBridge } from "@saleor/app-sdk/app-bridge"

function MyExtension() {
  const { appBridge } = useAppBridge()
  // Use appBridge.dispatch(), appBridge.state, etc.
}
```

## MacawUI Components

MacawUI is the official design system for Saleor Dashboard extensions:

| Component | Purpose |
|-----------|---------|
| `Button` | Primary and secondary action buttons |
| `Input`, `Select` | Form input fields and dropdowns |
| `Box`, `Sprinkles` | Layout primitives with design tokens |
| `Text` | Typography component with variants |
| `List`, `Table` | Data display components |
| `Chip` | Tag/badge component |
| `Combobox` | Searchable select with autocomplete |
| `Checkbox`, `Switch` | Toggle controls |
| `Skeleton` | Loading state placeholders |
| `Tooltip` | Contextual information popover |

Install via `npm install @saleor/macaw-ui` -- fetch live docs for the current version and available components.

### Theming

MacawUI supports the Dashboard's light and dark themes. Use the theme tokens from the App Bridge to ensure your extension matches the current Dashboard appearance.

## Extension Development Flow

| Step | Action |
|------|--------|
| 1 | Scaffold App with `saleor app create` |
| 2 | Define extension mounting points in the manifest |
| 3 | Create Next.js pages for each extension URL |
| 4 | Initialize App Bridge in each extension page |
| 5 | Build UI with MacawUI components |
| 6 | Use App Bridge token for authenticated GraphQL calls |
| 7 | Tunnel and install for local testing |
| 8 | Deploy and update the App manifest URL |

## Iframe Communication Details

| Aspect | Detail |
|--------|--------|
| Protocol | `window.postMessage` over the iframe boundary |
| Origin | Messages are validated against the Saleor instance origin |
| Handshake | Dashboard sends initial state (domain, token, theme) |
| Security | Always verify message origin before processing |
| Size | Use `ResizeObserver` to communicate content height to Dashboard |

## Dashboard Navigation

Your App can register full navigation entries that appear in the Dashboard sidebar:

| Navigation Area | Manifest Mount |
|----------------|---------------|
| Catalog section | `NAVIGATION_CATALOG` |
| Orders section | `NAVIGATION_ORDERS` |
| Customers section | `NAVIGATION_CUSTOMERS` |

These appear as sidebar links that load your App's page in the main content area.

## Best Practices

- Use MacawUI components exclusively for a consistent Dashboard look and feel
- Initialize App Bridge on every extension page to receive the auth token and theme
- Keep extension pages lightweight -- they load inside an iframe
- Use the `redirect` action for Dashboard navigation instead of direct URL changes
- Show loading states with MacawUI `Skeleton` while fetching data
- Handle both light and dark themes using MacawUI design tokens
- Test extensions at different Dashboard viewport sizes for responsive behavior
- Verify postMessage origins to prevent cross-origin security issues

Fetch the Saleor Dashboard extension documentation for exact mounting point identifiers, App Bridge action signatures, and MacawUI component APIs before implementing.
