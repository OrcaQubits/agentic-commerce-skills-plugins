---
name: spree-security
description: >
  Secure a Spree deployment — Rails credentials and env-var hygiene, Devise
  auth (Spree v5 ships it in-core; `spree_auth_devise` is archived), CanCanCan
  authorization rules, Doorkeeper OAuth2 scopes, Storefront publishable key vs
  admin API key, webhook HMAC verification, OWASP Top 10 for Rails (mass
  assignment, CSRF, SQL injection via Ransack, XSS, IDOR through prefixed IDs),
  PCI scope (Spree never touches raw cards thanks to gateway tokenization), and
  multi-store data isolation. Use when auditing a Spree app, hardening a deploy,
  or addressing a security incident.
---

# Spree Security

## Before writing code

**Fetch live docs**:
1. Check https://github.com/spree/spree/security for the security policy and known advisories.
2. Cross-reference https://rubysec.com for Rails / Ruby gem CVEs.
3. Inspect `Spree::Ability` (CanCanCan) in the live source for current default permissions.
4. Verify auth config in `config/initializers/devise.rb`.
5. For OAuth2, check Doorkeeper config in `config/initializers/doorkeeper.rb`.

## Conceptual Architecture

### Auth Stack

| Layer | Tool |
|-------|------|
| **Customer authentication** | Devise (v5 ships in-core; `spree_auth_devise` is **archived**) |
| **Admin authentication** | Same Devise system; differentiation via Spree::Role |
| **Authorization** | CanCanCan via `Spree::Ability` |
| **API auth (v3 Store)** | Publishable key + per-user JWT |
| **API auth (v3 Admin)** | Per-user API key + OAuth2 (Doorkeeper) |
| **API auth (v2 legacy)** | OAuth2 (Doorkeeper) password + client_credentials grants |
| **OAuth2 server** | Doorkeeper |
| **CSRF** | Rails default — required for HTML, exempted for API |

### `spree_auth_devise` Is Deprecated

The standalone `spree_auth_devise` gem is **archived as of Feb 2026**. Spree v5+ ships Devise auth in the core gem. Do NOT install the old gem on new projects — it conflicts and creates a maintenance burden.

### CanCanCan Permission Model

```ruby
# app/models/spree/ability.rb
class Spree::Ability
  include CanCan::Ability

  def initialize(user)
    user ||= Spree.user_class.new
    if user.has_spree_role?(:admin)
      can :manage, :all
    elsif user.has_spree_role?(:order_manager)
      can :manage, Spree::Order
    else
      can :read, [Spree::Product, Spree::Taxon]
    end
  end
end
```

Extend via decorator — don't replace.

### API Auth Tiers (v3)

| Token type | Scope | Where stored |
|------------|-------|--------------|
| **Publishable key** (`pk_…`) | Read-only public catalog + cart endpoints | Browser env (`NEXT_PUBLIC_*`) — safe |
| **User JWT** | Customer's account, their orders | **httpOnly cookie** server-side |
| **Cart token** (`order_token`) | Anonymous cart only | **httpOnly cookie** server-side |
| **Admin API key** | Per-user admin scope | Server env vars or vault — **never to browser** |
| **OAuth2 access token (admin scope)** | App integration | Server-to-server only |

### Webhook HMAC Verification

Webhooks 2.0 signs with HMAC-SHA256 over the raw body using a per-endpoint shared secret. Always verify:

```ruby
def verify(body, header, secret)
  expected = OpenSSL::HMAC.hexdigest('SHA256', secret, body)
  ActiveSupport::SecurityUtils.secure_compare(expected, header.sub(/^sha256=/, ''))
end
```

Use `secure_compare` — never `==` (timing attack).

### Rails OWASP Checklist for Spree

| Risk | Spree-specific mitigation |
|------|---------------------------|
| **A01 Broken access control** | CanCanCan `Spree::Ability` — never skip `authorize!`. Multi-store scoping. |
| **A02 Cryptographic failures** | Rails credentials. TLS everywhere. No secrets in YAML. |
| **A03 Injection** | ActiveRecord parameterization. Ransack: lock `ransackable_attributes`. |
| **A04 Insecure design** | Don't accept user-supplied IDs without ownership check. Use prefixed IDs. |
| **A05 Misconfiguration** | `config.force_ssl = true`. `config.action_controller.default_url_options = { protocol: 'https' }`. |
| **A06 Vulnerable deps** | `bundler-audit`, `brakeman` in CI. |
| **A07 ID&A failures** | Devise default rate-limits. Add 2FA via `devise-two-factor`. |
| **A08 Software integrity** | Pin gem versions. Verify gem signatures where supported. |
| **A09 Logging** | Filter params: `Rails.application.config.filter_parameters += [:password, :credit_card]`. |
| **A10 SSRF** | Never `Net::HTTP.get(params[:url])`. |

### Ransack Filter Exposure

API v2 filters use Ransack (`filter[status_eq]=complete`). By default, **all columns and associations are filterable**. Lock down per-model:

```ruby
# app/models/spree/order_decorator.rb
module SecureOrderRansack
  def self.prepended(base)
    base.class_eval do
      def self.ransackable_attributes(_auth = nil)
        %w[number state payment_state shipment_state created_at]
      end

      def self.ransackable_associations(_auth = nil)
        %w[user line_items]
      end
    end
  end
end
Spree::Order.prepend(SecureOrderRansack)
```

Without this, attackers can filter by sensitive columns (passwords, tokens).

### Prefixed IDs (v3)

API v3's prefixed IDs (`prod_…`, `ord_…`) are **opaque** strings — they don't expose row counts (sequential integers do). But always pair with **ownership checks**:

```ruby
order = current_store.orders.find(params[:id])  # scoped lookup
```

Not:
```ruby
order = Spree::Order.find(params[:id])  # IDOR risk
```

### PCI Scope

Spree's **never touches raw card numbers** when configured correctly:
- Stripe Elements / Adyen Drop-in / PayPal Buttons collect card data in the gateway's iframe
- Spree stores only the gateway's token (`tok_…`, `pm_…`, etc.)
- This keeps the merchant in **SAQ-A** scope, the lightest PCI tier

**Don't** build a custom card form that sends `params[:card_number]` to Rails. That escalates PCI scope dramatically.

### Multi-Store Data Isolation

As covered in `spree-multi-store`, always scope queries by `current_store`. A single missed scope can leak another tenant's orders.

### Devise Password Policies

Configure in `config/initializers/devise.rb`:

```ruby
config.password_length = 12..128
config.maximum_attempts = 5
config.unlock_in = 30.minutes
config.timeout_in = 30.minutes
```

Add zxcvbn-style strength via `devise_zxcvbn` if needed.

### 2FA

Spree doesn't ship 2FA, but Devise extensions add it:

```ruby
gem 'devise-two-factor'
```

Or use WebAuthn (`webauthn-ruby`) for hardware-key auth on admin accounts.

### Rails Master Key Hygiene

- **`RAILS_MASTER_KEY`** unlocks `config/credentials.yml.enc`
- Store it in your platform's secret manager (Heroku config, AWS Secrets Manager, etc.)
- **Never commit `config/master.key`** — gitignore it
- Rotate periodically: re-encrypt credentials with a new key, update env

### CSRF Exemption for APIs

```ruby
class Spree::Api::V3::BaseController < ActionController::API
  # ActionController::API doesn't include CSRF protection — correct for APIs
end
```

But **never disable CSRF on HTML controllers** (admin UI). Default Rails CSRF tokens protect admin from cross-origin attacks.

### Rate Limiting

Spree's per-endpoint API rate limiting is built in (v5+). For brute-force protection on admin login, layer **`rack-attack`**:

```ruby
# config/initializers/rack_attack.rb
Rack::Attack.throttle('admin_login', limit: 5, period: 15.minutes) do |req|
  req.ip if req.path == '/admin/login' && req.post?
end
```

## Implementation Guidance

### Pre-Production Security Checklist

1. **`config.force_ssl = true`** + HSTS headers
2. **`RAILS_MASTER_KEY` in vault** (not in code)
3. **Devise password policy** raised from defaults
4. **CanCanCan abilities** reviewed; no `can :manage, :all` outside admin role
5. **Ransack `ransackable_attributes` locked** per exposed model
6. **`bundler-audit` and `brakeman` clean** in CI
7. **Webhook signature verification** on every receiver
8. **OAuth2 application secrets rotated** quarterly
9. **API key issuance auditable** — Spree stores them; track in logs
10. **Multi-store scope test** — assert customer can't fetch other stores' orders
11. **PCI scope verified** — gateway iframes only; never custom card form
12. **Admin 2FA** for all admin users
13. **`config.filter_parameters`** includes `password`, `token`, `secret`, `credit_card`
14. **CSP headers** for the storefront (`Content-Security-Policy`)
15. **Backup encryption** at rest
16. **Image upload validation** — limit MIME types, sizes; scan for ImageMagick CVEs

### Brakeman in CI

```yaml
- run: bundle exec brakeman -q --no-pager --exit-on-warn
```

Treat new findings as build failures.

### Bundler-Audit

```bash
bundle exec bundler-audit check --update
```

Run on every CI build and weekly via scheduled job.

### Secrets in Decorators

```ruby
# Wrong — secret in code
ApiClient.new('sk_live_…')

# Right
ApiClient.new(Rails.application.credentials.dig(:my_service, :api_key))

# Also right
ApiClient.new(ENV.fetch('MY_SERVICE_API_KEY'))
```

### Common Security Pitfalls

- **Adding `spree_auth_devise` to a v5 project** — archived gem; conflicts.
- **Forgetting `current_store.orders` scoping** — leaks across stores.
- **Open Ransack filters** — exfiltration attack surface.
- **Custom credit card form** — escalates PCI scope.
- **Storing JWTs in `localStorage`** — XSS-exfiltratable.
- **Webhook handler without signature verification** — anyone can forge events.
- **Admin endpoints with `skip_before_action :authenticate_user!`** — accidental backdoor.
- **Mass assignment via permit!** — auditing the param permit list is essential.
- **Image processing on user-uploaded files without limits** — ImageMagick CVEs, memory exhaustion.
- **Sidekiq Web UI exposed without auth** — common production miss.

Always cross-reference the Spree security advisories page and `rubysec.com` for the gems your Spree version depends on.
