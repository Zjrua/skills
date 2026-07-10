# Kanban Profile Setup Guide

When a user wants to use Kanban multi-agent capabilities, they need dedicated Hermes profiles for each specialist role. This guide covers the full setup procedure.

## Prerequisites

- Hermes Agent installed and configured (`~/.hermes/config.yaml`)
- At least one LLM provider with API key configured
- `hermes kanban init` has been run (board exists)

## Step 1: Create Profiles

Clone from the default profile to inherit API keys and base config:

```bash
for role in planner coder writer researcher reviewer; do
    hermes profile create "$role" --clone --no-alias
done
```

`--clone` copies config.yaml, .env, and SOUL.md from the active profile.
`--no-alias` skips creating wrapper scripts (kanban workers are spawned by the dispatcher, not invoked directly by the user).

## Step 2: Write SOUL.md for Each Profile

Each profile needs a `~/.hermes/profiles/<name>/SOUL.md` that defines the agent's role, capabilities, and behavioral rules. See `templates/soul-*.md` for ready-to-use templates.

Key principles for SOUL.md content:
- **Role definition** — one clear sentence about what the agent IS
- **Capabilities** — what it can do (bulleted list)
- **Rules** — behavioral constraints (use `kanban_block` for unclear tasks, `kanban_heartbeat` for long tasks, etc.)
- **Output format** — what `kanban_complete` metadata should contain
- **Anti-patterns** — what NOT to do (e.g., planner must never execute tasks)

## Step 3: Configure Per-Profile Settings

Edit `~/.hermes/profiles/<name>/config.yaml`:

### Tool restrictions by role

| Role | `disabled_toolsets` | Rationale |
|---|---|---|
| `planner` | `terminal, file, web, browser` | Only decomposes and routes — no execution |
| `coder` | _(none)_ | Needs full development toolchain |
| `writer` | `terminal` | Content creation only, no shell access needed |
| `researcher` | _(none)_ | Needs web search and content extraction |
| `reviewer` | _(none)_ | Needs file read for code/content review |

### Max turns by role

| Role | `agent.max_turns` | Rationale |
|---|---|---|
| `planner` | 30 | Short-lived: read task, decompose, create cards, done |
| `coder` | 60 | Complex code may need many iterations |
| `writer` | 40 | Drafting and revising content |
| `researcher` | 50 | Multiple search-extract-synthesize cycles |
| `reviewer` | 40 | Read, analyze, write findings |

### Model per role (optional)

If the user has multiple providers, assign stronger models to roles that need them:

```bash
# Example: coder uses Claude, others use cheaper model
hermes -p coder config set model.default anthropic/claude-sonnet-4
hermes -p coder config set model.provider anthropic
```

Or edit `~/.hermes/profiles/<name>/.env` for per-profile API keys.

## Step 4: Verify

```bash
hermes profile list
# Should show all profiles with correct model

# Check each profile's SOUL.md loads correctly
for role in planner coder writer researcher reviewer; do
    echo "=== $role ==="
    head -1 ~/.hermes/profiles/$role/SOUL.md
done
```

## Step 5: Test with a Simple Task

```bash
# Initialize a kanban board (if not already done)
hermes kanban init

# Create a test task
hermes kanban create "Test: summarize AI trends in 2025" --assignee researcher
```

## File Layout After Setup

```
~/.hermes/profiles/
├── planner/
│   ├── config.yaml      # disabled_toolsets: [terminal, file, web, browser]
│   ├── .env             # API keys (cloned from default)
│   └── SOUL.md          # Planner personality
├── coder/
│   ├── config.yaml      # full tools, max_turns: 60
│   ├── .env
│   └── SOUL.md          # Coder personality
├── writer/
│   ├── config.yaml      # disabled_toolsets: [terminal], max_turns: 40
│   ├── .env
│   └── SOUL.md          # Writer personality
├── researcher/
│   ├── config.yaml      # full tools, max_turns: 50
│   ├── .env
│   └── SOUL.md          # Researcher personality
└── reviewer/
    ├── config.yaml      # full tools, max_turns: 40
    ├── .env
    └── SOUL.md          # Reviewer personality
```

## Fallback Chain Configuration

Each profile supports independent fallback chains via `config.yaml`. Two keys:

- `fallback_model` — first model to try if the primary fails (e.g. rate limit, outage)
- `fallback_providers` — array of additional fallbacks tried in order

### Designing cost-optimized fallback chains

When the user has mixed billing models (flat-rate plans with quotas + pay-per-token), put quota-limited models only where needed and use cheaper per-token models as defaults:

```
Example (zai coding plan = 5h quota + concurrency limit; deepseek = per-token):
  coder:     zai/glm-5.1 → zai/glm-5-turbo → deepseek-v4-flash → omlx/local
  planner:   deepseek-v4-flash → zai/glm-5-turbo → omlx/local
  writer:    deepseek-v4-flash → zai/glm-5-turbo → omlx/local
  researcher: deepseek-v4-flash → deepseek-v4-pro → omlx/local
  reviewer:  deepseek-v4-flash → deepseek-v4-pro → omlx/local
```

Key principles:
- **Expensive/limited models only on roles that need them** (coder gets the coding plan model)
- **Budget model as default** (deepseek-flash for routine tasks)
- **Mid-tier fallback** can serve as free quota sink (zai/glm-5-turbo on non-coder profiles)
- **Quality upgrade for critical roles** (researcher/reviewer fallback to pro, not down)
- **Local model always last** (guaranteed available, zero cost)

### Config YAML structure

```yaml
# Primary model
model:
  default: deepseek-v4-flash
  provider: deepseek

# First fallback
fallback_model:
  provider: zai
  model: glm-5-turbo

# Additional fallbacks (tried in order)
fallback_providers:
  - provider: omlx
    model: Qwen3.6-35B-A3B-MLX-4bit
    context_length: 262144
```

### custom_providers requirement

If a profile's primary provider is NOT `zai` but it falls back TO `zai`, the `custom_providers` array must include the zai entry in that profile's config.yaml. Otherwise the fallback will fail with "provider not found":

```yaml
custom_providers:
  - name: zai
    api_key: <key>
    base_url: https://open.bigmodel.cn/api/coding/paas/v4
    model: glm-5-turbo
    api_mode: chat_completions
```

This happens because `--clone` copies custom_providers from default, but if you later change the primary provider, verify the fallback provider's entry still exists.

## Pitfalls

- **Planner without tool restrictions** will try to execute tasks itself instead of creating kanban cards. Always disable execution tools for the planner.
- **Missing SOUL.md** means the worker has no role guidance and will behave like a generic assistant. Always write SOUL.md for each profile.
- **Shared API keys** (via --clone) are fine for same-provider setups, but if roles need different models/providers, edit each profile's `.env` separately.
- **Profile not showing in `hermes profile list`** — check the directory name is lowercase and matches the profile name used in `kanban create --assignee`.
- **NEVER invent or guess model names.** Always verify model IDs against the provider's API (`GET /v1/models` or `GET /models`). Model names like `deepseek-chat`, `gpt-4`, or `claude-3` may be deprecated, renamed, or never existed. Example verification:
  ```bash
  # DeepSeek
  curl -s https://api.deepseek.com/v1/models -H "Authorization: Bearer $DEEPSEEK_API_KEY"
  # Returns: deepseek-v4-flash, deepseek-v4-pro (as of 2026-05)

  # Zhipu (zai)
  curl -s https://open.bigmodel.cn/api/paas/v4/models -H "Authorization: Bearer $ZAI_KEY"
  # Returns: glm-5.1, glm-5-turbo, glm-5, glm-4.7, glm-4.6, glm-4.5, glm-4.5-air (as of 2026-05)
  ```
- **Fallback to custom provider without custom_providers entry.** If profile A's fallback uses a custom provider (e.g. `zai`), ensure `custom_providers` in that profile's config.yaml has the entry. Missing entries cause silent fallback failures.
- **Coding plan endpoints differ from standard endpoints.** Zhipu's coding plan uses `/api/coding/paas/v4/` not `/api/paas/v4/`. The `base_url` in custom_providers must match the plan type.
