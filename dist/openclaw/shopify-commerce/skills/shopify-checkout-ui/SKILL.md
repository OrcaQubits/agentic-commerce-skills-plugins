---
name: shopify-checkout-ui
description: >
  Build Shopify checkout UI extensions — extension targets, UI primitives,
  Preact/Remote DOM rendering, checkout APIs, metafield access, post-purchase
  extensions, and thank-you page customization. Use when customizing Shopify
  checkout.
---

# Shopify Checkout UI Extensions

## Before writing code

**Fetch live docs**:
1. Fetch `https://shopify.dev/docs/apps/build/checkout` for checkout extensions
2. Web-search `site:shopify.dev checkout ui extension targets` for available targets
3. Web-search `site:shopify.dev checkout ui components` for UI primitives

## What Are Checkout UI Extensions

Client-side extensions that add UI to Shopify's checkout:
- Render at specific **extension targets** (locations in checkout flow)
- Use Shopify's **UI primitives** (not Polaris, not HTML)
- Built with **Preact** and **Remote DOM** — sandboxed rendering
- Access checkout state via **APIs** (no direct DOM access)

**Important:** You cannot replace Shopify's checkout — only extend it at designated points.

## Extension Targets

Locations where extensions can render:

### Checkout Page
- `purchase.checkout.block.render` — general block in checkout
- `purchase.checkout.header.render-after` — after checkout header
- `purchase.checkout.footer.render-after` — after checkout footer
- `purchase.checkout.contact.render-after` — after contact info
- `purchase.checkout.shipping-option-list.render-after` — after shipping options
- `purchase.checkout.payment-method-list.render-after` — after payment methods
- `purchase.checkout.actions.render-before` — before pay button

### Thank You Page
- `purchase.thank-you.block.render` — block on thank-you page

### Order Status Page
- `customer-account.order-status.block.render` — block on order status

### Post-Purchase
- `purchase.post-purchase.render` — full-page post-purchase upsell
- `purchase.post-purchase.should-render` — decide whether to show post-purchase

## UI Primitives

Checkout extensions use Shopify's UI components (NOT Polaris, NOT HTML):

| Component | Purpose |
|-----------|---------|
| `Banner` | Information/warning/error messages |
| `BlockStack` | Vertical layout |
| `Button` | Action buttons |
| `Checkbox` | Boolean input |
| `ChoiceList` | Radio/checkbox groups |
| `Divider` | Visual separator |
| `Form` | Form container |
| `Heading` | Section headings |
| `Icon` | Icons |
| `Image` | Images |
| `InlineStack` | Horizontal layout |
| `Link` | Navigation links |
| `Select` | Dropdown selection |
| `Text` | Text content |
| `TextBlock` | Block of text |
| `TextField` | Text input |

## Extension Structure

```
extensions/checkout-ui/
├── src/
│   └── Checkout.tsx           # Extension component
├── shopify.extension.toml     # Configuration
├── locales/
│   └── en.default.json        # Translations
└── package.json
```

### Configuration

```toml
api_version = "2025-01"

[[extensions]]
name = "Custom Checkout Banner"
handle = "custom-checkout-banner"
type = "ui_extension"

  [[extensions.targeting]]
  module = "./src/Checkout.tsx"
  target = "purchase.checkout.block.render"
```

### Extension Component

```tsx
import {
  Banner,
  useExtensionApi,
  useCartLines,
  useApplyCartLinesChange,
  reactExtension,
} from '@shopify/ui-extensions-react/checkout';

export default reactExtension(
  'purchase.checkout.block.render',
  () => <CheckoutBanner />,
);

function CheckoutBanner() {
  const { extension } = useExtensionApi();
  const cartLines = useCartLines();
  const applyCartLinesChange = useApplyCartLinesChange();

  const itemCount = cartLines.reduce((sum, line) => sum + line.quantity, 0);

  if (itemCount < 3) {
    return (
      <Banner status="info">
        Add {3 - itemCount} more item(s) for free shipping!
      </Banner>
    );
  }

  return null;
}
```

## Checkout APIs (Hooks)

| Hook | Purpose |
|------|---------|
| `useCartLines()` | Current cart line items |
| `useApplyCartLinesChange()` | Modify cart lines |
| `useShippingAddress()` | Shipping address |
| `useBuyerJourney()` | Intercept checkout progression |
| `useAppMetafields()` | Read app metafields |
| `useCheckoutToken()` | Checkout session token |
| `useCurrency()` | Current currency |
| `useLocalizationCountry()` | Customer country |
| `useExtensionApi()` | Full extension API |

## Best Practices

- Use Shopify UI primitives — never attempt raw HTML or Polaris components
- Keep checkout extensions minimal — do not slow down checkout
- Use `useBuyerJourney()` to validate before checkout progression
- Store extension configuration in metafields
- Support localization with locale files
- Test with `shopify app dev` and a development store checkout
- Follow Shopify's checkout UX guidelines — do not distract from payment

Fetch the Shopify checkout UI extensions docs for exact component APIs, available hooks, and extension target names before implementing.
