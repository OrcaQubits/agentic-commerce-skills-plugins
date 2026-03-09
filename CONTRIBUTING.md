# Contributing to Agentic Commerce Claude Plugins

Thank you for your interest in contributing! This repository is a curated collection of Claude Code plugins for agentic commerce protocols and platforms. Every plugin follows a strict design philosophy: **bake in stable conceptual knowledge, fetch implementation details live**.

## Before You Start

- **Real-world use cases only.** Every plugin, skill, and hook must solve a genuine problem encountered when building agentic commerce systems. Do not submit hypothetical or untested plugins.
- **Attribution matters.** If your plugin is inspired by or based on someone else's work, integration guide, or sample code — credit them clearly.
- **Check for overlap.** Before starting, review the existing plugins to ensure your contribution does not duplicate existing coverage. If it extends an existing plugin, consider adding a new skill rather than a new plugin.

## Plugin Requirements

All submitted plugins must:

1. **Solve a genuine problem** — the plugin must address a real implementation challenge in agentic commerce (protocol integration, payment handling, agent orchestration, etc.)
2. **Follow the design philosophy:**
   - Stable conceptual knowledge (architecture, roles, flows, state machines) is embedded in the agent and skill definitions
   - Implementation-specific details (schemas, SDK methods, API parameters) are fetched live via `WebSearch`/`WebFetch` before writing code
   - Generated code cites the specification version it was written against
3. **Include a complete agent definition** with:
   - Live Documentation Rule section with official source URLs
   - Conceptual Architecture section covering stable protocol knowledge
   - Implementation Workflow section
4. **Include at least 3 skills** covering distinct aspects of the domain
5. **Include lifecycle hooks** where they add genuine safety value (secret detection, destructive command protection)
6. **Include a comprehensive README.md** with installation, usage, skill table, and official references
7. **Work with Claude Code** — test all skills and the subagent with real Claude Code sessions
8. **Use correct frontmatter format:**
   - Agent `tools` field must be a **comma-separated string** (e.g., `tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch`), NOT a YAML list
   - Skill frontmatter fields must follow the [Claude Code plugins reference](https://code.claude.com/docs/en/plugins-reference)

## Plugin Structure

Every plugin must follow this directory structure:

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json       # Plugin metadata
├── agents/
│   └── *-expert.md       # Expert subagent (one per plugin)
├── hooks/
│   ├── hooks.json        # Lifecycle hook configuration
│   └── scripts/
│       └── *.py          # Hook scripts (Python, no external dependencies)
├── skills/
│   └── skill-name/
│       └── SKILL.md      # Skill definition
├── .mcp.json             # MCP server config (only if a real MCP server exists)
├── .lsp.json             # LSP config (only for language-specific plugins)
└── README.md             # Plugin documentation
```

### Naming Conventions

- **Plugin directory**: `lowercase-with-hyphens` (e.g., `ucp-agentic-commerce`)
- **Skill directories**: `lowercase-with-hyphens` matching the skill name (e.g., `ucp-checkout-rest`)
- **Agent file**: `name-expert.md` (e.g., `ucp-expert.md`)
- **Hook scripts**: `snake_case.py` (e.g., `check_secrets.py`)
- **Plugin name in plugin.json**: must match the directory name

### plugin.json Template

```json
{
  "name": "your-plugin-name",
  "version": "1.0.0",
  "description": "One-line description of what the plugin provides",
  "keywords": ["relevant", "keywords", "for", "discovery"]
}
```

### Agent Frontmatter Template

```yaml
---
name: domain-expert
description: >
  Expert in [Protocol/Platform Name]. Deep conceptual knowledge of
  [key concepts]. Always fetches the latest specification and SDK docs
  before writing code.
tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
model: opus
---
```

### SKILL.md Frontmatter Template

```yaml
---
name: plugin-name:skill-name
description: >
  Brief description of what this skill does and when to use it.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, WebSearch, WebFetch
---
```

## Adding a New Plugin

### Step 1: Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/agentic-commerce-claude-plugins.git
cd agentic-commerce-claude-plugins
git checkout -b add-your-plugin-name
```

### Step 2: Create the Plugin Directory

```bash
mkdir -p your-plugin-name/.claude-plugin
mkdir -p your-plugin-name/agents
mkdir -p your-plugin-name/hooks/scripts
mkdir -p your-plugin-name/skills/your-first-skill
```

### Step 3: Write the Plugin Files

Follow the templates above. Key files to create:

1. `.claude-plugin/plugin.json` — metadata
2. `agents/your-expert.md` — subagent with Live Documentation Rule, Conceptual Architecture, and Implementation Workflow
3. `hooks/hooks.json` + `hooks/scripts/check_secrets.py` — at minimum, an async PostToolUse hook for secret detection
4. `skills/*/SKILL.md` — at least 3 skills covering distinct domain areas
5. `README.md` — follow the format of existing plugin READMEs

### Step 4: Test with Claude Code

Load your plugin and verify:

```bash
claude --plugin-dir ./your-plugin-name
```

- Run `/agents` — confirm your subagent appears
- Run `/plugin` — check the Errors tab for any loading issues
- Test each skill by describing a relevant task to Claude
- Verify the subagent fetches live documentation before writing code
- Confirm hooks fire correctly (check async hook output on the next turn)

### Step 5: Update the Root README

Add your plugin to the table in the root `README.md`, maintaining the existing format:

```markdown
| [your-plugin-name](./your-plugin-name) | Description of your plugin... | **Agent:** `your-expert`<br>**Skills (N):** List of skills<br>**Hooks:** Description of hooks |
```

### Step 6: Submit a Pull Request

```bash
git add your-plugin-name/
git add README.md
git commit -m "Add your-plugin-name plugin: brief description"
git push origin add-your-plugin-name
```

Then open a pull request.

## Adding a Skill to an Existing Plugin

If you want to add a new skill to an existing plugin:

1. Create a new directory under `skills/` with the skill name
2. Write the `SKILL.md` following the plugin's existing patterns
3. Update the plugin's `README.md` skill table and structure tree
4. Update the root `README.md` skill count
5. Test the skill with Claude Code
6. Submit a PR

## Adding or Modifying Hooks

When contributing hooks:

- **PostToolUse hooks must be async** (`"async": true`) — they must not block Claude's workflow
- **PreToolUse hooks should be fast** (< 10 second timeout) — they run synchronously before tool execution
- **Hook scripts must use only Python standard library** — no `pip install` dependencies
- **Hook scripts must handle JSON parse errors gracefully** — always wrap `json.load(sys.stdin)` in try/except
- **Exit codes matter**: 0 = success (output parsed as JSON), 2 = block (stderr shown to Claude), other = non-blocking error
- **Test on Windows with Git Bash** — this repo's primary environment uses bash on Windows

## Pull Request Guidelines

Your PR should include:

- **Descriptive title**: `Add [plugin-name]: [brief description]` or `Add [skill-name] skill to [plugin-name]`
- **What it does**: One paragraph explaining what the plugin/skill covers
- **Why it's needed**: What real-world problem does this solve?
- **What was tested**: Which Claude Code features did you verify (agent loading, skill invocation, hook behavior)?
- **Attribution**: Credit any protocols, documentation, or sample code that inspired the contribution

## What We Do NOT Accept

- **Plugins for hypothetical or unreleased protocols** — the protocol/platform must have a public specification or documentation
- **Plugins that hardcode implementation details** — schemas, SDK methods, and API parameters must be fetched live, not embedded
- **Plugins with `tools` as a YAML list** — the `tools` field must be a comma-separated string per the Claude Code spec
- **Hook scripts with external dependencies** — only Python standard library
- **Plugins without a README** — every plugin must be self-documenting
- **Duplicate coverage** — if an existing plugin already covers the domain, extend it with new skills instead

## Code of Conduct

- **Be respectful** in all interactions — issues, PRs, and reviews
- **Credit your sources** — if your plugin is based on a protocol specification, sample code, or integration guide, say so
- **Prioritize correctness** — agentic commerce involves payments and financial transactions; accuracy matters
- **Test before submitting** — every PR should include confirmation that the plugin loads and works in Claude Code
- **Keep it focused** — each plugin should cover one protocol or platform, not try to be everything

## Questions?

Open an issue if you have questions about contributing, or if you want to discuss a potential plugin before building it.
