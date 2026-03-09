# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this repository, **please report it privately** rather than opening a public issue.

### How to Report

1. **GitHub Private Vulnerability Reporting**: Go to the [Security tab](https://github.com/OrcaQubits/agentic-commerce-claude-plugins/security/advisories/new) of this repository and click **Report a vulnerability**.
2. **Email**: Send details to the maintainers via the contact information on [orcaqubits-ai.com](https://orcaqubits-ai.com).

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Which plugin(s) are affected
- Potential impact (e.g., credential exposure, code injection)

### What to Expect

- **Acknowledgement** within 72 hours
- **Status update** within 7 days
- **Fix or mitigation** as soon as possible, depending on severity

### Scope

This policy covers:

- **Hook scripts** (`hooks/scripts/*.py`) — secret detection and CLI protection logic
- **Skill definitions** (`skills/*/SKILL.md`) — instructions that guide code generation
- **Agent definitions** (`agents/*.md`) — instructions that guide subagent behavior
- **Plugin metadata** (`.claude-plugin/plugin.json`, `marketplace.json`)

Since these plugins generate code via Claude Code rather than executing application logic directly, the primary risk vectors are:

- Hook scripts that fail to detect hardcoded secrets
- Skill or agent instructions that could lead to insecure generated code
- Plugin metadata that could be manipulated in a supply chain attack

### Out of Scope

- Vulnerabilities in Claude Code itself (report to [Anthropic](https://www.anthropic.com/responsible-disclosure))
- Vulnerabilities in the underlying protocols (UCP, ACP, AP2, A2A, WebMCP) — report to their respective maintainers
- Vulnerabilities in commerce platforms (Magento, BigCommerce, WooCommerce) — report to their respective security teams

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | Yes       |
