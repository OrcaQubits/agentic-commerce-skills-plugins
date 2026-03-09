---
name: ap2-credentials-provider
description: Build an AP2 Credentials Provider — the agent that manages payment credentials, provides payment methods to users, handles tokenization (DPAN), and facilitates secure payment between Shopping Agent and Payment Processor. Use when implementing the Credentials Provider role.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---

# AP2 Credentials Provider Implementation

## Before writing code

**Fetch live docs**:
1. Fetch `https://ap2-protocol.org/specification/` for Credentials Provider responsibilities
2. Web-search `site:github.com google-agentic-commerce AP2 samples roles credentials_provider` for reference implementation
3. Web-search `site:github.com google-agentic-commerce AP2 credentials provider tokenization DPAN` for tokenization details
4. Fetch `https://ap2-protocol.org/topics/privacy-and-security/` for security requirements

## Conceptual Architecture

### What the Credentials Provider Does

The Credentials Provider (CP) is the **payment credentials custodian** — a digital wallet that securely manages payment methods and handles tokenization:

1. **Stores payment credentials** — User's payment methods (cards, wallets)
2. **Provides payment method listings** — Returns available methods to Shopping Agent
3. **Handles tokenization** — Converts real credentials to DPANs (Digitized Primary Account Numbers)
4. **Validates Payment Mandates** — Verifies user authorization before releasing tokens
5. **Facilitates payment** — Provides credentials to Merchant Payment Processor
6. **Manages user identity** — Links user identity to payment methods

### Critical Security Role

The Credentials Provider is the **only entity that handles raw payment credentials**:
- Shopping Agents never see real card numbers
- Merchants receive only tokenized references
- PCI data stays within the CP's security boundary
- This role-based separation is fundamental to AP2's privacy model

### Agent Card

The Credentials Provider advertises:
- AP2 extension support
- Available payment method types
- Tokenization capabilities
- Authentication requirements (OAuth2 recommended)
- Endpoint URL (reference: port 8002, path `/a2a/credentials_provider`)

### Key Responsibilities

#### Payment Method Management
- Store user payment methods securely (PCI DSS compliance)
- Return available payment methods when queried by Shopping Agent
- Include method details sufficient for user selection (last 4 digits, card type, expiry)
- Never expose full card numbers to Shopping Agents

#### Tokenization
- Generate DPANs (Digitized Primary Account Numbers) for selected payment methods
- Bind tokens to specific transactions
- Handle token lifecycle (creation, validation, expiration)
- Support network tokenization standards

#### Payment Mandate Validation
- Receive Payment Mandate + user attestation from Shopping Agent
- Verify user authorization signature
- Verify mandate contents integrity
- Perform additional tokenization if needed
- Release credentials to Merchant Payment Processor upon valid mandate

#### Credential Release
When the Merchant Payment Processor requests credentials:
- Validate the Payment Mandate
- Resolve the token to real credentials
- Release credentials securely to the MPP
- Never release credentials without a valid Payment Mandate

### Payment Method Addition

If a user lacks eligible payment methods:
- CP instructs the Shopping Agent on the setup process
- May require a tokenization flow on CP's trusted surface
- Network/issuer security requirements enforced
- New method added before transaction can proceed

### Security Requirements

- PCI DSS compliance for credential storage
- Hardware security modules (HSM) for key management
- Encryption of all credential data at rest and in transit
- Secure token generation with proper entropy
- Rate limiting on credential access
- Audit logging of all credential operations

### Best Practices

- Never expose raw credentials to Shopping Agents — always tokenize
- Implement proper PCI DSS controls
- Use hardware-backed token generation
- Validate every Payment Mandate before releasing credentials
- Support multiple payment method types (cards, wallets, bank accounts)
- Implement proper session management for user interactions
- Log all credential access for audit compliance
- Handle token expiration and renewal gracefully

Fetch the specification for exact Credentials Provider API, tokenization requirements, and Payment Mandate validation process before implementing.
