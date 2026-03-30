---
name: ap2-setup
description: >
  Scaffold a new AP2 project — install the SDK, set up agent roles, configure
  credentials, and create a basic multi-agent payment system. Use when starting
  a new AP2 agentic payments project from scratch.
---

# AP2 Project Setup

## Before writing code

**Fetch live docs**:
1. Fetch `https://ap2-protocol.org/` for the latest protocol overview
2. Fetch `https://github.com/google-agentic-commerce/AP2` for the current README and installation instructions
3. Web-search `site:github.com google-agentic-commerce AP2 samples python` for the sample project structure
4. Fetch `https://github.com/google-agentic-commerce/AP2/tree/main/samples/python` for Python sample layout

## Conceptual Architecture

### What Setup Involves

An AP2 project creates a multi-agent payment system with distinct roles:
1. **Install the AP2 Python package** from GitHub
2. **Create agent role directories** — Shopping Agent, Merchant, Credentials Provider, Payment Processor
3. **Configure authentication** — Google API key or Vertex AI credentials
4. **Define Agent Cards** — each agent advertises its AP2 capabilities
5. **Set up the agent framework** — Google ADK (Agent Development Kit) is the reference framework

### Installation

```bash
# Requires Python 3.10+ and uv
uv pip install git+https://github.com/google-agentic-commerce/AP2.git@main
```

### Project Structure (Reference from Official Samples)

```
my-ap2-project/
├── roles/
│   ├── shopping_agent/           # Shopping Agent — orchestrates purchases
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── merchant_agent/           # Merchant — product catalog, cart creation
│   │   ├── __init__.py
│   │   └── agent.py
│   ├── credentials_provider_agent/  # CP — payment methods, tokenization
│   │   ├── __init__.py
│   │   └── agent.py
│   └── merchant_payment_processor_agent/  # MPP — payment processing
│       ├── __init__.py
│       └── agent.py
├── .env                          # GOOGLE_API_KEY or Vertex AI config
├── pyproject.toml
├── run.sh                        # Launches all agents
└── tests/
    └── test_flow.py
```

### Environment Configuration

Two authentication options:
- **Google API Key** (development): Set `GOOGLE_API_KEY` in `.env`
- **Vertex AI** (production): Set `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION`

### Agent Ports (Reference)

Each agent runs on its own port:
- Shopping Agent: port 8000 (with ADK web UI)
- Merchant Agent: separate port
- Credentials Provider: port 8002 (RPC path `/a2a/credentials_provider`)
- Payment Processor: separate port

### Key Dependencies

- **Python 3.10+**
- **uv** — Python package manager (recommended)
- **Google ADK** — Agent Development Kit
- **Gemini 2.5 Flash** — LLM for agent reasoning
- **AP2 types** — `ap2.types` for mandate and payment structures

### Key Decisions During Setup

- **Which roles to implement** — You may implement one role (e.g., just a Merchant) or all four
- **Framework choice** — ADK is reference, but AP2 works with LangGraph, CrewAI, AG2, or any framework
- **Payment methods** — Start with mocked payments for development
- **A2A transport** — Agents communicate via A2A protocol over HTTP

### Best Practices

- Start with the official sample as a template
- Use mocked payment providers for development (no real money)
- Keep each agent role in a separate directory/module
- Use `.env` files for credentials, never hardcode
- Set up logging early — the `.logs/watch.log` pattern from samples is useful
- Test with the "verbose" mode to see all mandate payloads

Fetch the latest GitHub README and sample READMEs for exact setup commands, current package versions, and framework requirements before scaffolding.
