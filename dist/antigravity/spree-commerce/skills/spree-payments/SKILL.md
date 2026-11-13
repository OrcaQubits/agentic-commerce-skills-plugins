---
name: spree-payments
description: >
  Integrate payment gateways with Spree — PaymentMethod model, the v5.4+
  PaymentSession provider-agnostic checkout flow, Stripe via `spree_stripe`
  (Apple/Google Pay, Link, Connect for marketplaces), Adyen via `spree_adyen`,
  PayPal via `spree_paypal_checkout`, StoreCredit / GiftCard as payment methods,
  refunds, payment state machine, and authoring a custom gateway. Use when
  wiring a payment integration, handling webhooks from a gateway, or debugging
  payment-state issues.
---

# Spree Payments

## Before writing code

**Fetch live docs**:
1. Fetch https://spreecommerce.org/docs/developer/core-concepts/payments for the Payment + PaymentSession model.
2. Fetch the integration repo README — https://github.com/spree/spree_stripe / spree_adyen / spree_paypal_checkout — for current install + config.
3. Check the gateway's own SDK docs (Stripe / Adyen / PayPal) for the latest API version.
4. Inspect the live `Spree::Payment` source for state transitions and column names.
5. Check the v5.4 announcement for the PaymentSession introduction.

## Conceptual Architecture

### PaymentMethod, Payment, PaymentSession

| Model | Purpose |
|-------|---------|
| **`PaymentMethod`** | Admin-configured way to pay (Stripe, Adyen, PayPal, StoreCredit, etc.). Per-store, per-currency. |
| **`Payment`** | A specific payment attempt on an Order. Has a `state`, a `source` (CreditCard/StoreCredit/...), and an `amount`. |
| **`PaymentSession`** (v5.4+) | Provider-agnostic envelope around a payment authorization. Wraps Stripe Payment Intents, Adyen sessions, PayPal orders. |

### Payment State Machine

```
checkout → processing → pending → completed
                    ↓
                  failed | void | invalid
```

- **`checkout`** — initialized, waiting for capture
- **`processing`** — sent to gateway
- **`pending`** — gateway accepted, awaiting async confirmation (3DS, ACH)
- **`completed`** — captured
- **`failed`** — declined
- **`void`** — voided pre-capture
- **`invalid`** — gateway returned an unparseable response

### Payment Sources

Most `Payment` rows have a polymorphic `source`:
- `Spree::CreditCard` — tokenized card data
- `Spree::StoreCredit` — user's store credit balance
- `Spree::GiftCard` — gift card balance
- Gateway-specific (`Spree::PayPalCheckout::Order`, etc.)

### The v5.4 PaymentSession Flow

1. Storefront calls `POST /api/v3/store/checkout/payment_sessions` with `payment_method_id`.
2. Spree creates a `PaymentSession`, hits the gateway's session API (Stripe Payment Intent, Adyen `/sessions`, PayPal `/v2/orders`).
3. Storefront renders the gateway's hosted UI (Stripe Elements, Adyen Drop-in, PayPal Buttons) with the returned client secret / session data.
4. User authorizes (handles 3DS, SCA, Apple/Google Pay).
5. Storefront calls `POST /api/v3/store/checkout/complete`.
6. Spree captures the session into a `Payment` and advances the order.

Provider differences are hidden behind the `PaymentSession` envelope — the storefront code is gateway-agnostic above the UI layer.

### Stripe via spree_stripe

- One-click installer in admin (Settings → Payment Methods → Stripe → Connect)
- Supports cards, Apple Pay, Google Pay, Link, Klarna, Affirm, SEPA
- **Stripe Connect** for marketplace payouts (Enterprise marketplace)
- Webhooks: `payment_intent.succeeded`, `payment_intent.payment_failed`, etc. routed to `/webhooks/stripe`

### Adyen via spree_adyen

- Supports cards + many local payment methods
- Drop-in UI in the Next.js storefront
- HMAC-signed webhooks

### PayPal via spree_paypal_checkout

- PayPal Checkout (Smart Buttons) + PayPal Credit
- Server-side order creation

### Refunds

Refund a captured Payment:

```ruby
refund = Spree::Refund.create!(
  payment: payment,
  amount: payment.amount,
  reason: Spree::RefundReason.first
)
refund.perform!
```

`perform!` hits the gateway's refund endpoint and updates the `Payment#state` if fully refunded.

### Reimbursement vs Refund

- **Refund** — credits back the original payment method.
- **Reimbursement** — orchestrates the return flow; can issue a Refund OR a StoreCredit, on a CustomerReturn.

### StoreCredit and GiftCard as Payment Methods

Both work as native payment sources. The checkout state machine skips the `payment` step if store credit fully covers the order.

## Implementation Guidance

### Adding Stripe to a Spree v5.4+ Project

```ruby
# Gemfile
gem 'spree_stripe'

# Then
bundle install
bin/rails g spree_stripe:install
bin/rails db:migrate
```

In admin → Settings → Payment Methods → Stripe → connect via OAuth (Stripe Express / Standard). Set webhook endpoint in Stripe dashboard to `https://yourdomain/webhooks/stripe`. Verify the env vars (`STRIPE_API_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_WEBHOOK_SECRET`) — check the README for the current naming.

### Creating a PaymentSession (v5.4+ headless)

```typescript
// In a Server Action of the Next.js storefront
const session = await spree.checkout.createPaymentSession({
  paymentMethodId: 'pm_stripe',
});
// session.clientSecret used by Stripe Elements
// session.dropInPayload used by Adyen Drop-in
```

(Verify against `@spree/sdk` docs.)

### Authoring a Custom Gateway

```ruby
# app/models/my_app/payment_method/custom_gateway.rb
class MyApp::PaymentMethod::CustomGateway < Spree::PaymentMethod
  def payment_source_class
    Spree::CreditCard
  end

  def gateway_class
    MyApp::Gateways::CustomBilling
  end

  def supports?(source)
    source.is_a?(Spree::CreditCard)
  end

  def actions
    %w[capture void credit]
  end
end

# app/models/my_app/gateways/custom_billing.rb
class MyApp::Gateways::CustomBilling
  def initialize(options = {})
    @api_key = options[:api_key]
  end

  def authorize(amount_cents, source, options = {})
    # Hit the gateway's authorize endpoint
    # Return ActiveMerchant::Billing::Response.new(...)
  end

  def capture(amount_cents, authorization_token, options = {})
    # …
  end

  def void(authorization_token, options = {})
    # …
  end

  def credit(amount_cents, authorization_token, options = {})
    # refund
  end
end
```

Register the payment method type in an initializer:

```ruby
Rails.application.config.spree.payment_methods << MyApp::PaymentMethod::CustomGateway
```

### Webhook Handling

Spree gateway gems mount their own webhook routes (e.g., `/webhooks/stripe`). When customizing:

```ruby
# Subscribe to Spree's own events after webhook processing
class PaymentSubscriber < Spree::Subscriber
  subscribes_to 'payment.paid'
  on 'payment.paid', :sync_to_accounting
end
```

### Handling 3DS / SCA

`Payment#state == 'pending'` after authorize means the gateway is waiting for the customer to complete a challenge. The storefront polls or listens for the gateway's webhook, then either `payment.complete!` or `payment.failure!`.

### Split Tender (StoreCredit + Card)

Spree natively supports multiple `Payment` rows per order. The order updater allocates outstanding balance across them in order of creation. The order state machine completes only when sum(payments.completed) == order.total.

### Common Pitfalls

- **Hardcoding gateway secrets in `config/spree.rb`** — use Rails credentials or env vars.
- **Manually setting `Payment#state = 'completed'`** — bypasses the gateway flow; reconciliation breaks.
- **Refunding more than the original Payment amount** — gateway rejects; pre-validate.
- **Forgetting webhook signature verification** — gateway gems handle this, but custom integrations must verify HMAC.
- **PaymentSession not cleaned up on cart abandonment** — gateways have their own expiry; don't rely on Spree to release holds.
- **Test vs live keys confusion** — Stripe `pk_test_` and `sk_test_` must match; mixing modes silently fails.
- **Wrong payment_method per store** — multi-store deployments need a PaymentMethod per store unless you explicitly mark it shared.

Always re-fetch the gateway gem's README before writing integration code — gateway APIs and Spree wrapper versions drift independently.
