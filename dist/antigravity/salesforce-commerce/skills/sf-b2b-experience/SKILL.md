---
name: sf-b2b-experience
description: >
  Build B2B Commerce storefronts with Experience Builder — LWR templates, page
  types (Home, Product, Category, Cart, Checkout), standard and custom
  components, theme layouts, navigation, SEO configuration, and site publishing.
  Use when assembling B2B/D2C storefronts.
---

# sf-b2b-experience

Build B2B Commerce storefronts using Salesforce Experience Builder (formerly Community Builder).

## Before Writing Code

**Fetch live docs BEFORE writing code:**

1. **Web-search** the latest:
   - "Salesforce Experience Builder documentation 2026"
   - "Salesforce B2B Commerce storefront setup guide 2026"
   - "Lightning Web Runtime LWR template 2026"
   - "Salesforce Commerce standard components 2026"
   - "Experience Builder SEO configuration 2026"

2. **Web-fetch** official sources:
   - `developer.salesforce.com/docs/commerce/salesforce-commerce/guide/experience-builder.html`
   - `help.salesforce.com/s/articleView?id=sf.b2b_comm_lightning_storefront_setup.htm`
   - `developer.salesforce.com/docs/platform/lwc/guide/lwr-get-started.html`

3. **Verify** current LWR template structure, standard component catalog, page types, buyer group configuration, and SEO metadata options.

## Conceptual Architecture

### LWR vs Aura Comparison

| Feature | LWR (Modern) | Aura (Legacy) |
|---------|--------------|---------------|
| Performance | Faster, optimized rendering | Slower, heavier framework |
| Standards | Web standards (ES modules, Shadow DOM) | Proprietary component model |
| Components | LWC only | Aura + LWC |
| SEO | Better server-side rendering | Limited |
| PWA support | Progressive Web App capable | No |
| Future | Active development | Maintenance mode |

Always use **LWR templates** for new B2B Commerce storefronts.

### Page Types

| Page Type | Purpose | Key Components |
|-----------|---------|---------------|
| **Home** | Landing page | Hero banner, featured products, category nav, search |
| **Product Detail (PDP)** | Single product view | Gallery, pricing, inventory, add-to-cart, variations |
| **Product List (PLP)** | Category/search results | Product grid, filters, sorting, pagination, breadcrumbs |
| **Cart** | Shopping cart | Line items, quantities, pricing summary, promo codes |
| **Checkout** | Multi-step purchase flow | Shipping, delivery, payment, review, submit |
| **Order Confirmation** | Post-purchase | Order number, details, shipping, continue shopping |
| **Search Results** | Query results | Product matches, filters, sorting, suggestions |
| **Account Management** | Customer self-service | Order history, addresses, payment methods, profile |

### Template and Theme Structure

```
Theme Configuration
├── Company Settings (logo, favicon)
├── Color Palette (primary, secondary, text, bg)
├── Typography (headings, body, font families)
└── Custom CSS (advanced overrides)
```

**Layout components:** Header (logo, nav, search, cart, account), Footer (links, contact, social), Sidebar (filters, category tree), Grid System (responsive columns).

**Responsive breakpoints:** Desktop (1024px+), Tablet (768-1023px), Mobile (<768px). Component visibility can be configured per device type.

### Buyer Groups and Entitlements

**Buyer groups** are collections of accounts that share product catalog visibility, pricing rules, entitlement policies, and payment terms.

| Concept | Description |
|---------|-------------|
| **Product entitlements** | Which products each buyer group can see |
| **Pricing rules** | Group-specific pricing (negotiated, volume, contract) |
| **Payment terms** | Net 30, Net 60, credit limits per group |
| **Guest browsing** | Limited catalog, list prices only, no checkout (configurable) |

Use cases: VIP customers, regional buyers, partner tiers (Gold/Silver/Bronze), contract-based pricing.

### SEO Considerations

| Element | Configuration |
|---------|--------------|
| Page title | `<title>` tag, 50-60 chars, set per page |
| Meta description | Search snippet, 150-160 chars |
| URL slug | User-friendly path (no random IDs) |
| Open Graph tags | Social media sharing metadata |
| Canonical URL | Prevent duplicate content |
| Structured data | Schema.org (Product, Breadcrumb, Organization) |
| Sitemap | Automatic XML generation; submit to Search Console |

### Component Visibility Rules

Experience Builder supports conditional component visibility:
- Show/hide components per device type (desktop, tablet, mobile)
- Show/hide based on user authentication state (guest vs logged-in)
- Buyer group-specific component visibility
- Page-level access control (public vs authenticated)

### Custom Components in Experience Builder

Custom LWC components are exposed to Experience Builder via `js-meta.xml` (see `sf-b2b-lwc` skill for development details):
- Set `isExposed: true` and target `lightningCommunity__Page` / `lightningCommunity__Default`
- Define configurable properties (String, Integer, Boolean) visible in the builder property panel
- Components appear in the Components panel for drag-and-drop placement

### Site Publishing Workflow

| Stage | Description |
|-------|-------------|
| **Draft** | Build pages, add components, configure settings (not visible to visitors) |
| **Preview** | Preview as different user types (guest, authenticated, buyer groups) |
| **Publish** | One-click publish; changes go live immediately; version history for rollback |
| **Activate/Deactivate** | Control site availability; set maintenance page when deactivated |

## Best Practices

### Component Strategy
- Use standard commerce components first (proven, maintained, optimized)
- Build custom components only for brand-specific or unique functionality
- Compose standard components creatively before building from scratch

### User Experience
- Mobile-first design (many B2B buyers browse on mobile)
- Clear checkout flow with progress indication
- Intuitive category navigation and faceted search
- WCAG AA accessibility compliance

### B2B Specific
- Respect buyer group entitlements for product visibility and pricing
- Support multi-user accounts (buyer, approver, admin roles)
- Enable bulk ordering (CSV upload, quick order forms)
- Provide reorder functionality from order history
- Display contract/negotiated pricing per account

### Testing and Deployment
- Test with multiple buyer groups to verify entitlements and pricing
- Cross-browser testing (Chrome, Firefox, Safari, Edge)
- Build in sandbox, deploy via change sets or Metadata API
- Run Lighthouse and accessibility audits before go-live

Fetch Experience Builder docs, LWR template guide, and B2B Commerce setup documentation for exact page configuration, component catalog, and buyer group setup before implementing.
