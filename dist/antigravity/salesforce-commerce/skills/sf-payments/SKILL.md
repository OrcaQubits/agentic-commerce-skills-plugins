---
name: sf-payments
description: >
  Implement Salesforce Commerce payments — Salesforce Payments (supports
  multiple processors including Stripe and Adyen), B2C payment adapters
  (JavaScript cartridge-based), B2B payment adapters (Apex-based), PCI
  compliance via tokenization, 3D Secure/SCA support, and payment method
  management. Use when implementing payment processing.
---

# sf-payments

## Before Writing Code

**Fetch live docs before implementing payment processing features.**

1. Web-search: "Salesforce Payments documentation Stripe Adyen 2026"
2. Web-search: "Salesforce B2C Commerce payment cartridge integration guide 2026"
3. Web-search: "Salesforce B2B Commerce Apex PaymentGatewayAdapter 2026"
4. Web-search: "PCI DSS SAQ-A compliance tokenization 2026"
5. Web-search: "3D Secure 2 SCA authentication flow implementation 2026"
6. Web-fetch the Salesforce Payments setup guide and B2C payment hook documentation

## Conceptual Architecture

### Payment Flow Overview

```
Authorize (reserve funds)
  -> Capture (collect on shipment)
    -> Refund (return funds, full or partial)
  -> Void (cancel before capture)
```

This authorize-capture-refund lifecycle applies to both B2C and B2B. Some flows combine authorize + capture into a single "sale" operation.

### Salesforce Payments (Native)

**Multi-processor support:** Salesforce Payments integrates with Stripe, Adyen, PayPal, and other processors. Configuration is unified within Salesforce Commerce setup.

| Feature | Detail |
|---|---|
| Payment methods | Cards, Apple Pay, Google Pay, ACH, SEPA, local methods |
| Saved methods | Tokenized cards for returning customers |
| Fraud detection | Via configured processor (Stripe Radar, Adyen risk) |
| 3DS / SCA | Built-in support through processor |
| Dispute management | Chargeback handling and evidence submission |
| Multi-currency | Configured per processor account |

### B2C Payment Processor Architecture

**Cartridge-based integration:**
- Payment processors packaged as SFCC cartridges (int_stripe, int_adyen, int_paypal, int_cybersource)
- Cartridge overlays base commerce cartridge
- Configuration in Business Manager: credentials, endpoints, payment method assignment
- Site-specific processor configuration per locale

**Payment Hook Points:**

| Hook | Purpose |
|---|---|
| Authorize | Reserve funds on payment method |
| Capture | Capture authorized amount (full or partial) |
| Refund | Return funds to customer |
| Void | Cancel authorization before capture |
| Verify | Validate payment method ($0 auth) |

**Server-side scripts** (authorize.js, capture.js, refund.js, void.js) receive basket/order, payment instrument, and amount; return `{authorized, error, errorMessage}`.

**Client-side integration:**
- Tokenization via processor SDK (Stripe Elements, Adyen Drop-in)
- Hosted payment fields (iframe) for PCI compliance
- Token submitted to server instead of raw card data

### B2B Payment Adapter Architecture

**Apex PaymentGatewayAdapter interface:**
- Implement in custom Apex class with methods: authorize, capture, refund, sale
- Return PaymentGatewayResponse with status, transaction ID, errors
- Register adapter in Setup > Payment Gateways

```apex
// Pattern: B2B PaymentGatewayAdapter skeleton
public class MyAdapter implements PaymentGatewayAdapter {
    // Fetch live docs for PaymentGatewayAdapter interface
    // Implement: authorize, capture, refund
}
```

**B2B Payment Method Types:**

| Method | Notes |
|---|---|
| Credit / debit card | Via PaymentGatewayAdapter |
| Purchase order (PO) | PO number required at checkout |
| Net terms | Net 30, Net 60 per account |
| ACH / bank transfer | For B2B bank payments |
| Invoice | Payment against generated invoice |

**B2B-specific considerations:**
- Credit limit enforcement at checkout
- Integration with approval workflows for high-value orders
- Multiple payment methods per order (split payment)

### PCI Compliance

**Tokenization Principle:**
- Never store or transmit raw card numbers through merchant servers
- Payment processor tokens replace card data; tokens stored in Salesforce (safe)
- Processor maintains secure vault with actual card data

**SAQ-A Compliance:**

| Requirement | Implementation |
|---|---|
| Card data never touches merchant servers | Use hosted payment fields (iframe) |
| Client-side tokenization only | Processor JS SDK tokenizes before form submit |
| Server receives tokens only | No raw card data in server logs or database |
| Processor handles PCI DSS Level 1 | Stripe Elements, Adyen Drop-in provide compliant fields |

### 3D Secure / SCA

**3DS2 Authentication Flow:**

```
Payment submitted
  -> Processor risk assessment
    -> Frictionless (low risk): instant approval
    -> Challenge (high risk): redirect/iframe to bank
      -> Customer authenticates (password, biometric, OTP)
        -> Success: proceed with authorization
        -> Failure: decline payment
```

**SCA Requirements (European Transactions):**
- Strong Customer Authentication required for European cards/merchants
- Exemptions: low-value (<30 EUR), recurring, trusted beneficiaries
- 3DS2 is primary SCA compliance method
- Successful 3DS2 shifts liability to card issuer

## Code Examples

```javascript
// Pattern: B2C payment authorization hook
// Fetch live docs for SFCC PaymentProcessor scripts
// function authorize(order, paymentInstrument, amount)
//   -> call processor API -> return {authorized, error}
```

```apex
// Pattern: B2B gateway registration
// Fetch live docs for PaymentGateway setup
// Setup > Payment Gateways > register adapter class
// Store API keys in Named Credentials, not code
```

## Best Practices

### General Payment Security
- Always tokenize; never handle or store raw card data
- Use hosted payment fields (processor iframe) for SAQ-A eligibility
- Store API keys in Named Credentials or Custom Settings, never in code
- Implement webhook signature verification for async payment events

### B2C Cartridge Development
- Follow standard cartridge structure for payment scripts
- Return proper error messages for failed authorizations
- Always capture and store processor transaction IDs
- Support partial capture (split shipments) and partial refund (returns)

### B2B Payment Integration
- Support purchase orders with net payment terms for B2B buyers
- Validate against account credit limits before authorization
- Integrate payment with B2B approval workflows
- Enable ACH/bank transfer methods for B2B transactions

### 3D Secure
- Request 3DS2 authentication for all card payments
- Handle SCA exemptions properly (recurring, low-value)
- Provide good UX for challenge flows (iframe preferred over redirect)
- Verify 3DS authentication status and liability shift before proceeding

Fetch the Salesforce Payments configuration guide, PaymentGatewayAdapter Apex reference, and your processor's SDK docs for exact implementation details before coding.
