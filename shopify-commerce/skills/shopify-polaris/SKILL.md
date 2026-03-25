---
name: shopify-polaris
description: Build Shopify app UIs with Polaris — component categories, Web Components transition, React legacy components, App Design Guidelines, accessibility, @shopify/draggable, and design tokens. Use when building Shopify admin app interfaces.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Shopify Polaris Design System

## Before writing code

**Fetch live docs**:
1. Fetch `https://polaris.shopify.com/` for Polaris component documentation and examples
2. Web-search `site:shopify.dev polaris app design guidelines` for design guidelines
3. Web-search `site:shopify.dev polaris web components migration` for migration status
4. Web-search `site:polaris.shopify.com components` for current component APIs and props
5. Web-search `site:polaris.shopify.com tokens` for current design token values

## What Is Polaris

Shopify's design system for building admin app UIs:
- Component library with consistent Shopify admin look and feel
- Design tokens for colors, spacing, typography
- App Design Guidelines for embedded apps
- Accessibility-first design patterns

> **IMPORTANT:** Polaris React is in maintenance mode. Shopify is transitioning to Polaris Web Components. Check current migration status before choosing components.

## Component Categories

### Layout
- `Page` — top-level page container with title and actions
- `Layout` — two-column annotated layout
- `Card` — content container with sections
- `Box` — flexible container with spacing/color
- `InlineStack` — horizontal layout
- `BlockStack` — vertical layout
- `Divider` — visual separator
- `Grid` — CSS grid layout

### Actions
- `Button` — primary, secondary, destructive actions
- `ButtonGroup` — group related actions
- `ActionList` — dropdown menu of actions
- `Popover` — dropdown container

### Navigation
- `Navigation` — sidebar navigation
- `Tabs` — tabbed content
- `Pagination` — page navigation

### Forms
- `TextField` — text input
- `Select` — dropdown select
- `Checkbox` — boolean input
- `RadioButton` — single selection
- `ChoiceList` — radio/checkbox groups
- `DatePicker` — date selection
- `DropZone` — file upload
- `Form` — form container
- `FormLayout` — form field arrangement

### Feedback
- `Banner` — info, success, warning, critical messages
- `Toast` — temporary notifications
- `Badge` — status indicators
- `Spinner` — loading state
- `SkeletonPage` / `SkeletonBodyText` — loading placeholders
- `ProgressBar` — progress indicator

### Data Display
- `IndexTable` — resource list with bulk actions (primary list component)
- `DataTable` — simple tabular data
- `ResourceList` — list of resources (legacy, prefer IndexTable)
- `ResourceItem` — individual resource entry
- `DescriptionList` — key-value pairs
- `EmptyState` — no-content placeholder
- `Thumbnail` — small image

### Overlays
- `Modal` — dialog overlay
- `Sheet` — side panel (deprecated in React, check Web Components)

> **Fetch live docs** for current component APIs and props — components are updated frequently. Always check `https://polaris.shopify.com/components` before using any component.

## Minimal Usage Patterns

### Page with Card Layout

```tsx
// Pattern: standard Polaris page layout
// Fetch live docs for current Page, Card, and BlockStack props
<Page title="Products" primaryAction={{ content: "Add product", onAction: handleAdd }}>
  <Layout>
    <Layout.Section>
      <Card>
        <BlockStack gap="300">
          <Text variant="headingMd">Product List</Text>
          {/* IndexTable or content here */}
        </BlockStack>
      </Card>
    </Layout.Section>
    <Layout.Section variant="oneThird">
      <Card>
        <Text variant="headingMd">Filters</Text>
      </Card>
    </Layout.Section>
  </Layout>
</Page>
```

### Form Pattern

```tsx
// Pattern: form with validation
// Fetch live docs for current TextField, Select, and Form props
<Form onSubmit={handleSubmit}>
  <FormLayout>
    <TextField label="Product name" value={name} onChange={setName} autoComplete="off" />
    <Select label="Status" options={statusOptions} value={status} onChange={setStatus} />
    <Button submit variant="primary">Save</Button>
  </FormLayout>
</Form>
```

### Feedback Pattern

```tsx
// Pattern: Banner for persistent messages, Toast for transient
<Banner title="Order shipped" tone="success" onDismiss={handleDismiss}>
  <p>Tracking number: {trackingNumber}</p>
</Banner>

// Toast via App Bridge (not Polaris component in embedded apps)
shopify.toast.show("Product saved");
```

## Design Tokens

Consistent design values used across all Polaris components:

| Category | Token Pattern | Examples |
|----------|--------------|---------|
| Colors | `--p-color-bg-*`, `--p-color-text-*` | `--p-color-bg-surface`, `--p-color-text-critical` |
| Spacing | `--p-space-*` | `--p-space-100` (4px) through `--p-space-1200` (48px) |
| Typography | `--p-font-size-*`, `--p-font-weight-*` | `--p-font-size-300`, `--p-font-weight-bold` |
| Border | `--p-border-radius-*` | `--p-border-radius-200` |
| Shadow | `--p-shadow-*` | `--p-shadow-100`, `--p-shadow-200` |

> **Fetch live docs** for current token values and names — token naming conventions change across Polaris versions. Check `https://polaris.shopify.com/tokens`.

## @shopify/draggable

Shopify's drag-and-drop library:
- Draggable, Sortable, Swappable, Droppable
- Touch and mouse support
- Accessible with keyboard support
- Used for reorderable lists, kanban boards, custom interfaces

> **Fetch live docs**: Web-search `site:github.com shopify draggable` for current API and examples.

## App Design Guidelines

### Embedded Apps Must

- Use Polaris components for consistent admin experience
- Use App Bridge for navigation and titles
- Follow Shopify's color, typography, and spacing tokens
- Implement loading states (skeleton screens)
- Handle errors with Banner components
- Support responsive layouts

### Do NOT

- Use custom CSS that overrides Polaris styles
- Build custom navigation chrome (use App Bridge)
- Use non-Polaris modals or toasts in embedded apps
- Mix design systems (e.g., Material UI with Polaris)

## Accessibility

Polaris components are built with accessibility:
- ARIA attributes included by default
- Keyboard navigation support
- Focus management in modals and popovers
- Color contrast meets WCAG AA
- Screen reader announcements for dynamic content

> **Fetch live docs**: Web-search `site:polaris.shopify.com accessibility` for current accessibility guidelines and component-specific a11y notes.

## Best Practices

- Check Polaris Web Components status before starting — prefer Web Components if available
- Use `IndexTable` for resource lists (not `DataTable` for CRUD interfaces)
- Use `Banner` for persistent messages, `Toast` (via App Bridge) for transient confirmations
- Use skeleton components (`SkeletonPage`, `SkeletonBodyText`) for loading states
- Follow the `Page` → `Layout` → `Card` → content hierarchy
- Use `BlockStack` and `InlineStack` for layout (not CSS flex/grid directly)
- Apply design tokens for custom styles instead of hardcoded values
- Test keyboard navigation and screen reader output
- Always fetch live docs for component props before implementation — APIs change frequently

Fetch the Polaris documentation for exact component APIs, design tokens, prop types, and Web Components migration status before implementing.
