---
name: spree-checkout
description: >
  Implement Spree's checkout — the Order state machine (cart → address →
  delivery → payment → confirm → complete), the Payment and Shipment sub-state
  machines, the return flow (ReturnAuthorization → CustomerReturn →
  Reimbursement → Refund), guest checkout, payment-step skipping for
  credit-covered orders, and the V3 checkout API surface. Use when building or
  customizing checkout flows, debugging state transitions, or wiring custom
  checkout steps.
---

# Spree Checkout

## Before writing code

**Fetch live docs**:
1. Fetch https://spreecommerce.org/docs/developer/core-concepts/orders for the canonical state machine.
2. Fetch https://spreecommerce.org/docs/developer/core-concepts/payments for the Payment + PaymentSession (v5.4+) flow.
3. Check the live `Spree::Order` source on GitHub for the `state_machine` block — transitions and callbacks change.
4. For headless checkout, fetch the v3 Store API docs at https://spreecommerce.org/docs/api-reference.
5. Verify any custom-step pattern against the latest examples in `spree-starter`.

## Conceptual Architecture

### The Order State Machine

```
cart → address → delivery → payment → confirm → complete
                                ↓
                              skip if store-credit-covered
```

Each transition validates prerequisites:

| State | Prerequisites |
|-------|---------------|
| `cart` | One or more line items |
| `address` | Bill + ship address present |
| `delivery` | Shipping method selected for every shipment |
| `payment` | At least one payment method valid for the total |
| `confirm` | Optional review step (configurable) |
| `complete` | All sub-states valid; transitions trigger fulfillment + emails |

### Payment Sub-State

`Order#payment_state` is a separate field summarizing all `Payment` rows:

| Value | Meaning |
|-------|---------|
| `balance_due` | Outstanding amount remains |
| `paid` | Fully paid |
| `credit_owed` | Refund pending |
| `failed` | All payments failed |
| `void` | Voided |

### Shipment Sub-State

`Order#shipment_state` summarizes all `Shipment` rows:

| Value | Meaning |
|-------|---------|
| `pending` | Awaiting payment / stock |
| `ready` | Ready to ship |
| `partial` | Some shipped |
| `shipped` | All shipped |
| `backorder` | Inventory shortfall |
| `canceled` | Canceled |

### Individual Shipment / Payment State Machines

- **`Shipment#state`**: `pending → ready → shipped` (+ `canceled`)
- **`Payment#state`**: `checkout → processing → pending → completed` (+ `failed`, `void`, `invalid`)

### Return Flow

```
ReturnAuthorization (authorized | canceled)
  → CustomerReturn
    → Reimbursement (pending | reimbursed | errored)
      → Refund (against original Payment)
```

`StoreCredit` reimbursements skip the Refund step and credit the user's balance.

### Skipping the Payment Step

If `order.outstanding_balance.zero?` after store-credit/gift-card application, the state machine skips `payment` and goes straight to `confirm`. Useful for free-trial / 100%-off scenarios.

### Guest vs Authenticated Checkout

Spree supports guest checkout by default — orders carry an `email` and `order_token` even without a `User`. The token allows a guest to revisit their order. Convert guests to users post-checkout via `Spree::Order#associate_user!`.

### Custom Checkout Steps

Add a custom step by inserting into the state machine via decorator:

```ruby
# app/models/spree/order_decorator.rb
module MyApp::OrderDecorator
  def self.prepended(base)
    base.state_machine.before_transition to: :delivery, do: :verify_gift_message
  end

  def verify_gift_message
    # …
  end

  Spree::Order.prepend(self)
end
```

Custom steps are powerful but **upgrade-fragile** — Spree's state machine evolves. Prefer events or service objects when you only need to react.

### Checkout via API v3 (v5.4+)

Headless checkout typically:

1. `POST /api/v3/store/cart` — create cart (returns `ord_…` ID + cart token)
2. `POST /api/v3/store/cart/line_items` — add items
3. `PUT /api/v3/store/checkout` — set addresses, shipping method, payment method
4. `POST /api/v3/store/checkout/payment_sessions` — create a PaymentSession (Stripe/Adyen/PayPal)
5. `POST /api/v3/store/checkout/complete` — finalize

(Verify exact paths in the v3 API reference — endpoint shapes are still settling.)

### Payment Sessions (v5.4+)

The v5.4 `PaymentSession` abstracts the payment-provider handshake. The storefront creates a PaymentSession, the user authorizes via the gateway's hosted UI (Stripe Elements, Adyen Drop-in, PayPal Checkout), and the session is captured into a `Payment` on completion. Provider-specific.

## Implementation Guidance

### Reading the Current State

```ruby
order.state                # one of cart/address/delivery/payment/confirm/complete
order.payment_state        # balance_due/paid/...
order.shipment_state       # pending/ready/...
order.can_transition?(:complete)  # check before triggering
```

### Triggering Transitions Programmatically

```ruby
order.next!     # advance to the next state if valid
order.complete! # force to complete if valid (typically last step)
order.cancel!   # cancel + revert inventory
```

Never call `update_attribute(:state, …)` directly — bypasses callbacks and corrupts inventory/payments.

### Subscribing to Checkout Events

```ruby
class CheckoutSubscriber < Spree::Subscriber
  subscribes_to 'order.completed'
  on 'order.completed', :send_welcome_email

  def send_welcome_email(event)
    return if event.order.user.nil?
    # …
  end
end
```

Events fire after the database commit — safe to enqueue background jobs.

### Headless Checkout Patterns

- **Always use httpOnly cookies for the cart/order token**, not localStorage.
- **Confirm the cart server-side before showing the review step** — prices, tax, shipping can change between page loads.
- **Idempotency-Key headers on `/complete`** — prevent double-charging on retry.
- **Use Payment Sessions for v5.4+** — they handle 3DS / SCA / Apple Pay / Google Pay uniformly.

### Debugging Stuck Transitions

```ruby
order.errors.full_messages
order.valid?(state)  # validate for a specific state
order.checkout_steps  # configured step list
```

### Returns Workflow

```ruby
ra = Spree::ReturnAuthorization.create!(order: order, return_items: items)
ra.authorize!
cr = Spree::CustomerReturn.create!(return_items: ra.return_items, stock_location: location)
cr.fully_received?
reimbursement = Spree::Reimbursement.create!(customer_return: cr, order: order)
reimbursement.perform!  # creates Refunds or StoreCredits
```

### Common Pitfalls

- **Bypassing the state machine** by setting `state` directly → corrupts inventory and payment totals.
- **Forgetting to recompute totals** after adjusting line items → use `Spree::OrderUpdater`.
- **Marking a Payment `completed` manually** → use the gateway's capture flow; manual completion skips reconciliation.
- **Treating `confirm` as required** — it's configurable (`checkout_steps` order).
- **Headless checkout drift** — the storefront's local state can diverge from the server's `Order#state`. Re-fetch after every mutating call.
- **Custom decorator on `state_machine`** — survives minor upgrades poorly; prefer event subscribers when possible.

Always re-verify state names and transition guards against the live `Spree::Order` source for the version you target.
