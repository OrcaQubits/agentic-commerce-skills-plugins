---
name: nlweb-llm-providers
description: >
  Configure NLWeb LLM and embedding providers — OpenAI, Azure OpenAI (default),
  Anthropic, Google Gemini, DeepSeek on Azure, Llama on Azure, HuggingFace,
  Inception Labs, Snowflake Cortex, Ollama, Pi Labs. Covers `config_llm.yaml`
  high/low tier model selection, the ModelRouter cost/quality routing logic,
  `config_embedding.yaml`, and adding a custom provider. Use when picking
  models, tuning cost, or wiring a new LLM backend.
---

# NLWeb LLM & Embedding Providers

## Before writing code

**Fetch live docs**:
1. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/docs/nlweb-providers.md for the canonical provider list and config schema.
2. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/config/config_llm.yaml for the **exact model IDs and env-var names currently shipped**.
3. Fetch https://github.com/nlweb-ai/NLWeb/blob/main/config/config_embedding.yaml for embedding defaults.
4. Inspect `AskAgent/python/llm_providers/<provider>.py` for the SDK calls the provider class makes.
5. Web-search the latest release notes — new providers and models get added often.

## Conceptual Architecture

### Mixed-Mode = Many Small LLM Calls

NLWeb's pipeline doesn't make one big LLM call per query. It makes **many small calls**: decontextualize the query, detect Schema.org item type, route to a tool, rank results, optionally summarize/generate. Each call has a strict `<returnStruc>` JSON schema in `prompts.xml`. Cost and latency are dominated by the *number* of calls, not the size of any single one.

### High / Low Tier Model Selection

`config_llm.yaml` defines a **high model** and a **low model** per provider:

```yaml
providers:
  openai:
    high: gpt-4.1
    low: gpt-4.1-mini
    api_key_env: OPENAI_API_KEY
```

The codebase decides which tier to use per call site — e.g., decontextualization is "low", final generate is "high". The exact assignment lives in `core/` modules and the `ModelRouter` subsystem.

### The Default Provider

Out of the box, NLWeb's `preferred_endpoint` (in `config_llm.yaml`) is **`azure_openai`** with `gpt-4.1` / `gpt-4.1-mini`. Most users override this in `.env` or by editing the YAML.

### All Supported LLM Providers

(Verify the live `config_llm.yaml` for current models and key names.)

| Provider | Default high | Default low | Env var |
|----------|--------------|-------------|---------|
| OpenAI | gpt-4.1 | gpt-4.1-mini | `OPENAI_API_KEY` |
| Azure OpenAI | gpt-4.1 | gpt-4.1-mini | `AZURE_OPENAI_API_KEY` + `AZURE_OPENAI_ENDPOINT` |
| Anthropic | claude-3-7-sonnet-latest | claude-3-5-haiku-latest | `ANTHROPIC_API_KEY` |
| Google Gemini | gemini-2.5-pro | gemini-2.0-flash-lite | `GEMINI_API_KEY` |
| DeepSeek on Azure | deepseek-coder-33b | deepseek-coder-7b | `AZURE_DEEPSEEK_ENDPOINT` |
| Llama on Azure | llama-2-70b | llama-2-13b | `AZURE_LLAMA_ENDPOINT` |
| HuggingFace | Qwen2.5-72B | Qwen2.5-Coder-7B | `HF_TOKEN` |
| Inception Labs | mercury-small | mercury-small | `INCEPTION_API_KEY` |
| Snowflake Cortex | claude-3-5-sonnet | llama3.1-8b | Snowflake creds |
| Ollama | configurable | configurable | local — no key |
| Pi Labs | (class present, may not be in default YAML) | — | — |

### Embedding Providers

| Provider | Default model | Dim |
|----------|---------------|-----|
| OpenAI | text-embedding-3-small | 1536 |
| Azure OpenAI | text-embedding-3-small | 1536 |
| Gemini | text-embedding-004 | 768 |
| Snowflake | arctic-embed-m-v1.5 | 768 |
| Elasticsearch | multilingual-e5-small | 384 |
| Ollama | nomic-embed-text (typically) | 768 |

Set `preferred_provider` in `config_embedding.yaml`. **This must match what you used at ingest time** — the most common NLWeb bug is changing the embedding provider after data is loaded, then getting empty results.

### ModelRouter

NLWeb's `ModelRouter/` subsystem is a cost/quality router that picks the right model tier (high vs low) per call site. It's still evolving — verify whether it's active in your release.

### Why So Many Providers?

R.V. Guha's design goal: NLWeb should run on whatever LLM stack the site operator already has. A Snowflake customer uses Cortex; an Azure shop uses Azure OpenAI; a privacy-conscious deployment uses Ollama on prem. The provider abstraction is intentional.

## Implementation Guidance

### Switching the Primary LLM Provider

In `config_llm.yaml`:

```yaml
preferred_endpoint: anthropic

providers:
  anthropic:
    high: claude-3-7-sonnet-latest
    low: claude-3-5-haiku-latest
    api_key_env: ANTHROPIC_API_KEY
```

Set `ANTHROPIC_API_KEY` in `.env`. Restart the server.

### Running Locally with Ollama (Offline)

Install Ollama, pull a model:
```bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

In `config_llm.yaml`:
```yaml
preferred_endpoint: ollama
providers:
  ollama:
    high: llama3.1:8b
    low: llama3.1:8b
    base_url: http://localhost:11434
```

In `config_embedding.yaml`:
```yaml
preferred_provider: ollama
providers:
  ollama:
    model: nomic-embed-text
    dim: 768
```

Important: re-ingest after switching embedding provider — old vectors are now wrong-dim.

### Adding a Custom Provider

1. Subclass the base class in `llm_providers/` (look at `openai.py` or `anthropic.py` as templates).
2. Implement the required methods (typically `complete()` returning JSON-conformant output for the `<returnStruc>` schemas, plus optional streaming).
3. Register in the provider factory (verify exact location — usually a registry in `core/llm.py`).
4. Add an entry in `config_llm.yaml`.
5. Test against a known-good `<returnStruc>` prompt before deploying.

### Tuning Cost

- Use `low` tier for everything except the final generate (default behavior — verify).
- Set `tool_selection_enabled: false` in `config_nlweb.yaml` to skip the router call entirely.
- Disable `who_endpoint_enabled` to skip federated discovery.
- Pre-compute `decontextualized_query` client-side to skip that LLM call.

### Switching Embedding Providers Safely

```bash
# 1. Stop serving traffic
# 2. Change config_embedding.yaml
# 3. Drop the index
python -m data_loading.db_load --only-delete delete-site <site>
# 4. Re-ingest
python -m data_loading.db_load <source> <site>
# 5. Restart
```

You cannot mix-and-match embedding providers across a single retrieval index. Vectors are not portable across providers.

### Verifying Provider Wiring

`nlweb check` runs connectivity diagnostics for all configured providers. Use it before debugging "the model isn't responding" issues — the answer is usually a missing env var.

### Provider Failure Modes

- **OpenAI / Anthropic / Gemini 429s**: rate limits. Add backoff in the provider class or reduce concurrency.
- **Azure OpenAI 404 on deployment**: the `deployment_name` in config doesn't match what's deployed in Azure. They're per-deployment, not per-model.
- **Ollama "model not found"**: `ollama pull <model>` first.
- **Snowflake Cortex authentication**: requires the warehouse + role to have Cortex enabled.
- **HuggingFace inference endpoint cold-start**: first call takes 30-60s. Pre-warm.

Always re-fetch `config_llm.yaml` from the live repo — provider keys and model IDs change.
