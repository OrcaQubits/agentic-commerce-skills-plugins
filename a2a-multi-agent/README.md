# A2A Multi-Agent Plugin for Claude Code

A deeply expert Claude Code plugin for building multi-agent systems using the **A2A (Agent-to-Agent) protocol** — the open standard initiated by Google (now under the Linux Foundation) for inter-agent communication.

## Design Philosophy

This plugin is built to **stay current**:

- **Conceptual knowledge is baked in** — protocol architecture, Agent Cards, task lifecycle, state machines, message/part types, transport details, and design patterns that are stable across spec versions.
- **Implementation-specific details are fetched live** — the subagent and every skill instruct Claude Code to web-search and fetch the official docs before writing code, so you always get the latest schemas, SDK methods, and API shapes.
- **Spec version is always cited** — generated code includes comments referencing the A2A specification version it was written against.

## Plugin Structure

```
a2a-multi-agent/
├── .claude-plugin/
│   └── plugin.json                         # Plugin manifest
├── agents/
│   └── a2a-expert.md                       # Subagent: full A2A protocol expert
├── hooks/
│   ├── hooks.json                          # Lifecycle hooks configuration
│   └── scripts/
│       └── check_secrets.py                # PostToolUse: detect hardcoded auth secrets
├── skills/
│   ├── a2a-setup/SKILL.md                  # Project scaffolding & SDK install
│   ├── a2a-agent-card/SKILL.md             # Agent Card creation & configuration
│   ├── a2a-server/SKILL.md                 # A2A server implementation
│   ├── a2a-client/SKILL.md                 # A2A client implementation
│   ├── a2a-task-lifecycle/SKILL.md         # Task states, transitions, artifacts
│   ├── a2a-messages-parts/SKILL.md         # Messages, TextPart/FilePart/DataPart
│   ├── a2a-streaming/SKILL.md              # SSE streaming (message/stream)
│   ├── a2a-push-notifications/SKILL.md     # Push notification callbacks
│   ├── a2a-authentication/SKILL.md         # API Key, Bearer, OAuth2, OIDC, mTLS
│   ├── a2a-multi-turn/SKILL.md             # Multi-turn conversations (input-required)
│   ├── a2a-error-handling/SKILL.md         # JSON-RPC errors & A2A error codes
│   ├── a2a-jsonrpc-transport/SKILL.md      # JSON-RPC 2.0 transport layer
│   ├── a2a-mcp-bridge/SKILL.md             # A2A + MCP integration patterns
│   ├── a2a-framework-integration/SKILL.md  # ADK, LangGraph, CrewAI, AutoGen, Bedrock
│   ├── a2a-testing/SKILL.md                # Testing strategies & mock agents
│   └── a2a-dev-patterns/SKILL.md           # Orchestration, observability, deployment
└── README.md
```

## Installation

### Per-session

```bash
claude --plugin-dir "a2a-multi-agent"
```

### Persistent

Add to `~/.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "a2a-multi-agent": {
      "type": "local",
      "path": "/path/to/agentic-commerce-claude-plugins/a2a-multi-agent"
    }
  }
}
```

### Verify

Run `/agents` in Claude Code — you should see `a2a-multi-agent:a2a-expert`.

## Using the Subagent

### Auto-delegation

Claude auto-delegates when your task involves A2A:

```
Build an A2A agent that summarizes documents
```

```
Create a multi-agent system where a coordinator delegates to specialist agents
```

```
Add streaming and push notifications to my A2A server
```

### Explicit invocation

```
Use the a2a-expert subagent to implement Agent Card discovery
```

### What makes it different

The subagent has `WebSearch` and `WebFetch` in its tool list. Before writing implementation code, it will:

1. Search for the latest spec version on a2a-protocol.org
2. Fetch the relevant specification page for exact schemas
3. Fetch the SDK README for current install/usage instructions
4. Write code against the verified-current spec, citing the version

## Available Skills (16)

| Skill | Invocation | Description |
|---|---|---|
| **a2a-setup** | Auto + manual | Scaffold project, install SDK, create Agent Card |
| **a2a-agent-card** | Auto + manual | Agent Card creation, skills, capabilities, authentication |
| **a2a-server** | Auto + manual | Server implementation — JSON-RPC handler, task management |
| **a2a-client** | Auto + manual | Client implementation — discovery, requests, response handling |
| **a2a-task-lifecycle** | Auto + manual | Task states (9), transitions, artifacts, history |
| **a2a-messages-parts** | Auto + manual | Messages, TextPart, FilePart, DataPart, content negotiation |
| **a2a-streaming** | Auto + manual | SSE streaming, event types, re-subscription |
| **a2a-push-notifications** | Auto + manual | Callback registration, notification delivery, management |
| **a2a-authentication** | Auto + manual | API Key, Bearer, OAuth2, OIDC, mTLS security schemes |
| **a2a-multi-turn** | Auto + manual | Multi-turn conversations, input-required handling |
| **a2a-error-handling** | Auto + manual | JSON-RPC errors, A2A error codes, retry strategies |
| **a2a-jsonrpc-transport** | Auto + manual | JSON-RPC 2.0 protocol, methods, request/response format |
| **a2a-mcp-bridge** | Auto + manual | A2A + MCP integration, hybrid multi-agent systems |
| **a2a-framework-integration** | Auto + manual | ADK, LangGraph, CrewAI, AutoGen, Bedrock AgentCore |
| **a2a-testing** | Auto + manual | Unit, integration, conformance, and e2e testing |
| **a2a-dev-patterns** | Auto + manual | Orchestration topologies, observability, deployment patterns |

## Hooks

The plugin includes lifecycle hooks that provide safety guardrails:

| Event | Trigger | Behavior |
|-------|---------|----------|
| **PostToolUse** (async) | Write or Edit tool completes | Scans written code for hardcoded Bearer tokens, API keys (OpenAI, Google, Anthropic), client secrets, and private key material. Outputs a warning if detected. Non-blocking. |

Hooks require Python in PATH.

## A2A Protocol at a Glance

### Three Core Concepts

| Concept | What It Is |
|---------|------------|
| **Agent Card** | JSON document describing an agent's capabilities, skills, auth, and endpoint |
| **Task** | Unit of work with a lifecycle (9 states), messages, and artifacts |
| **Message** | Communication unit with Parts (TextPart, FilePart, DataPart) and roles |

### Nine Task States

```
submitted → working → completed
    |          |          |
    |          +→ input-required → (more input) → working
    |          +→ failed
    |          +→ canceled
    |
    +→ rejected
    +→ auth-required

unspecified (default)
```

### Core JSON-RPC Methods

| Method | Purpose |
|--------|---------|
| `message/send` | Send message, synchronous response |
| `message/stream` | Send message, SSE streaming response |
| `tasks/get` | Retrieve task by ID |
| `tasks/cancel` | Cancel a task |
| `tasks/resubscribe` | Re-subscribe to task SSE stream |

### A2A vs MCP

| Aspect | A2A | MCP |
|--------|-----|-----|
| **Purpose** | Agent ↔ Agent | Agent ↔ Tool/Data |
| **Primitives** | Tasks & Messages | Tool Calls |
| **Discovery** | Agent Cards | Server Manifests |
| **Transport** | JSON-RPC over HTTP | JSON-RPC over stdio/HTTP+SSE |
| **Complementary** | Yes | Yes |

### Five Auth Schemes

| Scheme | Use Case |
|--------|----------|
| **API Key** | Simple, development, internal |
| **HTTP Bearer** | Token-based, JWTs |
| **OAuth 2.0** | Production, scoped access |
| **OpenID Connect** | Enterprise SSO |
| **Mutual TLS** | High-security, zero-trust |

### Official SDKs

| Language | Package | Repository |
|----------|---------|------------|
| Python | `a2a-sdk` | github.com/a2aproject/a2a-python |
| JavaScript/TS | `@a2a-js/sdk` | github.com/a2aproject/a2a-js |
| Go | — | github.com/a2aproject/a2a-go |
| Java | — | github.com/a2aproject/a2a-java |
| .NET | — | github.com/a2aproject/a2a-dotnet |

## Official References

| Resource | URL |
|----------|-----|
| A2A Website | https://a2a-protocol.org |
| Specification (latest) | https://a2a-protocol.org/latest/specification/ |
| GitHub Organization | https://github.com/a2aproject/A2A |
| Python SDK | https://github.com/a2aproject/a2a-python |
| JS/TS SDK | https://github.com/a2aproject/a2a-js |
| Go SDK | https://github.com/a2aproject/a2a-go |
| Samples | https://github.com/a2aproject/a2a-samples |
| Google ADK | https://google.github.io/adk-docs/ |
| Linux Foundation AI & Data | https://lfaidata.foundation/ |

## Endorsed By

Google, Atlassian, Block, Cisco, Deloitte, Intuit, MongoDB, PayPal, Salesforce, SAP, ServiceNow, UKG, and 40+ others.
