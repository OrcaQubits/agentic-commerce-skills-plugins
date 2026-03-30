---
name: bc-payments
description: >
  Integrate BigCommerce payments — Payment Processing API, stored payment
  instruments, payment methods, server-side payment processing for headless, and
  PCI considerations. Use when building custom payment flows or processing
  payments programmatically.
---

# BigCommerce Payment Integration

## Before writing code

**Fetch live docs**:
1. Fetch `https://developer.bigcommerce.com/docs/integrations/payments` for payments guide
2. Web-search `site:developer.bigcommerce.com payments processing api` for Payment Processing API
3. Web-search `bigcommerce payment methods api configuration` for payment method management

## Payment Architecture

### How Payments Work in BigCommerce

BigCommerce handles payment gateway connections:
- **Admin-Configured** — merchants configure payment providers (Stripe, PayPal, Square, etc.) in the BigCommerce admin
- **Native Checkout** — payment gateway integration is built into BigCommerce checkout
- **Headless/API** — use the Payment Processing API to process payments server-side

### Payment Flow (Headless)

1. Create cart → checkout → order via API
2. Get accepted payment methods: `GET /v3/payments/methods`
3. Create payment access token: `POST /v3/payments/access_tokens`
4. Process payment: `POST https://payments.bigcommerce.com/stores/{hash}/payments`

## Payment Processing API

### Get Payment Methods

`GET /v3/payments/methods?order_id={id}` — returns accepted methods for an order:
```json
{
  "data": [
    {
      "id": "stripe.card",
      "name": "Stripe",
      "supported_instruments": [
        { "instrument_type": "VISA", "verification_value_required": true }
      ],
      "test_mode": false,
      "type": "CARD"
    }
  ]
}
```

### Create Payment Access Token

`POST /v3/payments/access_tokens`:
```json
{
  "order": { "id": 12345 }
}
```

Returns a single-use access token for the Payments endpoint.

### Process Payment

`POST https://payments.bigcommerce.com/stores/{hash}/payments`

Headers:
- `Authorization: PAT {payment_access_token}`
- `Content-Type: application/json`

```json
{
  "payment": {
    "instrument": {
      "type": "card",
      "number": "4111111111111111",
      "expiry_month": 12,
      "expiry_year": 2025,
      "name": "John Doe",
      "verification_value": "123"
    },
    "payment_method_id": "stripe.card"
  }
}
```

**Important**: Sending raw card data requires PCI DSS compliance. Most implementations should use tokenized payment methods instead.

## Stored Payment Instruments

### Stored Cards

Customers can save payment methods for future purchases:
- `GET /v3/payments/methods?customer_id={id}` — list stored instruments
- Stored instruments are tokenized — no raw card data stored
- Reference stored instruments by token during payment

### Using Stored Instruments

```json
{
  "payment": {
    "instrument": {
      "type": "stored_card",
      "token": "abc123tokenvalue",
      "verification_value": "123"
    },
    "payment_method_id": "stripe.card"
  }
}
```

## Payment Method Configuration

### Admin-Level

Payment methods configured in BigCommerce admin:
- Stores > Settings > Payments
- Enable/disable providers
- Configure API keys per provider
- Set test/sandbox mode

### API-Level

`GET /v3/payments/methods` — list configured payment methods:
- Returns only methods available for the current checkout context
- Filtered by order currency, customer location, etc.

## Refunds

Via V3 Payment Actions API:
- `POST /v3/orders/{id}/payment_actions/refund_quotes` — get refund options
- `POST /v3/orders/{id}/payment_actions/refunds` — process refund
- Supports full and partial refunds
- Refund routed through the original payment provider

## Void / Capture

For gateways supporting authorize-then-capture:
- `POST /v3/orders/{id}/payment_actions/void` — void authorization
- `POST /v3/orders/{id}/payment_actions/capture` — capture authorized payment

## PCI Compliance

### Reducing PCI Scope

- **Embedded Checkout** — BigCommerce hosts the payment form, keeping your site out of PCI scope
- **Tokenized payments** — use gateway-provided JS SDKs (Stripe Elements, Braintree Drop-in) to tokenize card data client-side
- **Stored instruments** — reference tokens instead of raw card data
- **Never** log, store, or transmit raw card numbers through your servers

### When PCI Compliance is Required

If you use the Payment Processing API with raw card data (`type: "card"`), your infrastructure must be PCI DSS compliant.

## Best Practices

- Use Embedded Checkout or tokenized payments to avoid PCI scope
- Use stored payment instruments for returning customers
- Always use payment access tokens (PAT) — they're single-use and time-limited
- Handle payment failures gracefully — display clear error messages
- Implement refunds through the API for accurate records
- Test with sandbox/test mode before going live
- Support multiple payment methods for better conversion
- Never log or store raw card data

Fetch the BigCommerce Payment Processing API documentation for exact endpoints, request formats, and supported payment methods before implementing.
