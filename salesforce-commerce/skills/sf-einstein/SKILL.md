---
name: sf-einstein
description: Implement Einstein AI for Salesforce Commerce — Einstein Recommendations (product-to-product, user-to-product, trending), predictive sort, search ranking, Einstein Search Dictionaries, and Data Cloud personalization. Use when adding AI-powered features to commerce storefronts.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# Einstein AI for Salesforce Commerce

## Before Writing Code

**Fetch live docs before implementing Einstein AI features.**

1. Web-search: "Salesforce Commerce Cloud Einstein Recommendations API 2026"
2. Web-search: "Salesforce Einstein Search dictionaries relevance tuning 2026"
3. Web-search: "Salesforce Data Cloud B2C Commerce personalization 2026"
4. Web-search: "Salesforce Commerce Cloud PWA Kit Einstein recommendations 2026"
5. Web-fetch the Einstein Recommendations API reference for current configuration parameters
6. Web-fetch Data Cloud connector setup and unified profile schema docs

## Conceptual Architecture

### Einstein Recommendations

**Recommender Types:**

| Type | Description | Typical Placement |
|---|---|---|
| Product-to-Product | Similar or complementary items (cross-sell) | PDP |
| Recently Viewed | User's browsing history | Homepage, category |
| Also Bought | Products frequently purchased together | Cart, PDP |
| Trending | Popular items across all users | Homepage, category |
| Top Sellers | Best-selling products by category/site | Homepage, category |
| Personalized | ML-driven per-user recommendations | Homepage (returning users) |

**Recommender Configuration (Business Manager):**
- Create recommenders with specific types and filtering rules
- Configure zone placement (homepage, PDP, cart, category page)
- Set filtering: exclude out-of-stock, price range limits, category restrictions
- Map recommendation zones to recommenders

**Activity Collection:**

Einstein activity tracking uses a `collect.js` library loaded on storefront pages. It automatically captures product views, add-to-cart, purchases, and search events. Configured via Business Manager > Einstein > Activity Tracking.

> **Warning:** The `_etmc` beacon pattern is for Marketing Cloud Einstein, not Commerce Cloud Einstein. Do not confuse the two.

**Recommendation Zones:**
- Define placement areas on storefront pages
- Map zones to recommenders in Business Manager
- Customize rendering per zone (carousel, grid, list)

### Einstein Predictive Sort

Personalized category page sorting powered by ML.

| Aspect | Detail |
|---|---|
| Input | User behavior (clicks, purchases, browse history) |
| Output | Per-user product ranking on category pages |
| Fallback | Default sorting for new / anonymous users |
| Config | Per-category toggle in Business Manager |

### Einstein Search

**Search Dictionaries:**

| Dictionary Type | Purpose | Example |
|---|---|---|
| Synonyms | Map equivalent terms | sneakers -> running shoes |
| Hypernyms | Broader category terms | iPhone -> smartphone |
| Compound Words | Multi-word phrases | ice cream, swimming pool |

**Search Relevance Tuning:**
- Boost or bury specific products in search results
- Configured per site/locale in Business Manager
- Sorting rules: relevance, price, newest, custom

**Typeahead Suggestions:**
- Search-as-you-type with phrase suggestions and hit counts
- Configured via Business Manager search settings

### Data Cloud Personalization

**Integration Architecture:**

```
B2C Commerce -> Data Cloud Connector -> Unified Profile
  -> Segmentation + ML Models (Einstein)
    -> Personalized Recommendations / Content
      -> Commerce Storefront (SFRA / PWA Kit)
```

**Key Concepts:**
- Aggregates data from Commerce Cloud, Service Cloud, Marketing Cloud into unified profiles
- Real-time profile updates via Data Cloud connector
- Segment membership drives personalized content and recommendations
- Cross-channel offer consistency based on unified customer view

**Data Cloud vs Commerce Cloud Einstein:**

| Aspect | Commerce Cloud Einstein | Data Cloud Personalization |
|---|---|---|
| Data source | Commerce activity only | Cross-cloud unified profile |
| Setup | Business Manager config | Data Cloud connector + config |
| Segments | Implicit (ML-driven) | Explicit (rule-based + ML) |
| Best for | Product recommendations | Cross-channel personalization |

**Zone Placement Strategy:**

| Page | Recommended Zones |
|---|---|
| Homepage | Trending + personalized (returning users) |
| PDP | Similar products + complementary items (cross-sell) |
| Cart | Cross-sell + upsell opportunities |
| Category | Predictive sort + trending in category |
| Search Results | Einstein-ranked results |

## Code Examples

```javascript
// Pattern: SFRA recommendation zone
// Fetch live docs for Einstein Recommendations API
var recs = einsteinAPI.getRecommendations(zone, customer);
// Render recs in ISML template
```

```javascript
// Pattern: PWA Kit recommendations hook
// Fetch live docs for commerce-sdk-react useRecommendations
const {data} = useRecommendations({recommenderName, products});
```

```javascript
// Pattern: Fallback when Einstein unavailable
// Fetch live docs for CacheMgr and fallback strategies
// try Einstein -> catch -> return getTopSellers(zone)
```

## Best Practices

### Activity Collection
- Configure activity tracking before enabling recommendations (minimum 2-4 weeks of data)
- Track all key events: views, add-to-cart, purchases, search queries
- Validate tracking via Einstein Activity Dashboard

### Performance
- Cache recommendations (5-15 min TTL) to reduce API calls
- Lazy-load recommendation zones below the fold
- Limit number of products per zone (8-12 typical)

### Privacy and Consent
- Respect customer privacy preferences (GDPR, CCPA)
- Allow opt-out from personalized recommendations
- Implement clear data retention and right-to-be-forgotten policies

### Rollout Strategy
- Start with one high-traffic zone (homepage); monitor 2-4 weeks
- A/B test Einstein vs. manual curation or top-sellers fallback
- Track CTR, conversion rate, revenue attribution per zone
- Gradually expand to PDP, category, cart after proven ROI

Fetch the Einstein Recommendations API reference and Data Cloud connector docs for exact configuration parameters and SDK versions before implementing.
