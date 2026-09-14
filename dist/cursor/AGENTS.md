# Agentic Commerce — Agent Rules

This repository contains expert knowledge for agentic commerce protocols and platforms. Each plugin directory has its own AGENTS.md with detailed rules and skills.

## Plugins

| Plugin | Description |
|--------|-------------|
| [commerce-readiness](./commerce-readiness/AGENTS.md) | Agentic Commerce Readiness Audit — executable stdlib-Python probes that score a live site on agent access, protocol discovery (UCP/ACP/A2A), catalog structured data (Product/ProductGroup JSON-LD), checkout transactability (ACP/UCP REST, MCP tools/list, NLWeb /ask), payment surfaces (handlers, delegate_payment, AP2, HTTP 402), and trust (OAuth, signing keys, TLS), mapping every gap to the marketplace skill that closes it |

## How to Use

Copy or symlink the plugin directories you need into your project. Your AI dev tool will automatically pick up the AGENTS.md files and the skills in `.cursor/skills/`.

