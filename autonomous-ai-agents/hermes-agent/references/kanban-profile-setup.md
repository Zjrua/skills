# Setting Up Multi-Agent Kanban Profiles

End-to-end workflow for creating specialized agent profiles for Hermes Kanban.

## Step 1: Create Profiles

```bash
# Clone from default (inherits API keys, .env)
for profile in planner coder writer researcher reviewer doubter; do
  hermes profile create $profile --clone --no-alias
done
```

Each profile gets its own directory at `~/.hermes/profiles/<name>/` with:
- `config.yaml` — model, tools, fallback chain
- `.env` — API keys (cloned from default)
- `SOUL.md` — system prompt / personality

## Step 2: Write SOUL.md for Each Profile

Each SOUL.md should define:
1. **Role description** — what this agent does
2. **Capabilities** — what it can do
3. **Rules** — constraints and behavior
4. **Contrast with similar profiles** — e.g. Doubter vs Reviewer
5. **Output format** — expected handoff structure

Key design principle: **no overlap**. Each profile should have a clear, non-overlapping responsibility:
- Planner: decompose and route (before execution)
- Doubter: challenge plans (before execution)
- Coder/Writer: execute (during execution)
- Reviewer: check output (after execution)

## Step 3: Configure Models and Fallbacks

Edit each profile's `config.yaml`:

```yaml
model:
  default: deepseek-v4-flash      # Primary model (API-verified name!)
  provider: deepseek               # Provider name
fallback_model:                    # First fallback
  provider: zai
  model: glm-5-turbo
fallback_providers: []             # Keep chain short (2 levels max)
```

### Fallback Design Principles

1. **Cross-cloud redundancy**: primary and fallback should be on different providers
2. **Consider availability**: cloud APIs (deepseek, zai) > local models (omlx) which depend on machine uptime
3. **Keep chains short**: primary + one fallback is enough. Long chains add latency on failures.
4. **Match capability**: don't put a weak model as fallback for a critical profile (e.g. don't fallback coder to a non-coding model)

### Set Delegation Config

Each profile that spawns subagents MUST set delegation explicitly:

```yaml
delegation:
  provider: deepseek              # Match the profile's primary provider
  model: deepseek-v4-flash        # Match the profile's primary model
  max_iterations: 80              # Default 50 is too low for research tasks
```

If this is left empty, subagents inherit the gateway's provider/model combo, which may not match — causing HTTP 400 errors.

## Step 4: Configure Toolsets Per Profile

```yaml
agent:
  max_turns: 60                   # Default; increase for research (90)
  disabled_toolsets: []           # Restrict tools per role
```

Guidelines:
- **Planner**: disable terminal/file/web (only decomposes, doesn't execute)
- **Writer**: disable terminal (content creation only)
- **Coder/Researcher**: full tools
- **Reviewer/Doubter**: full tools (need to read code/docs)

## Step 5: Verify

```bash
hermes profile list                # All profiles visible
# For each profile, verify model name exists:
curl -s <provider_base_url>/models -H "Authorization: Bearer <key>"
```

## Common Pitfalls

1. **Wrong model names**: `deepseek-chat` doesn't exist → use `deepseek-v4-flash`. Always verify via `/models` endpoint.
2. **Missing custom_providers**: If a profile's fallback uses a custom provider (e.g. `zai`), the `custom_providers` list must exist in that profile's config.yaml.
3. **Delegation inherits gateway model**: Worker on deepseek spawns subagent that tries zai endpoint with deepseek model → 400 error. Fix: set `delegation.provider` and `delegation.model` explicitly.
4. **omlx in fallback chain**: Local model depends on Mac being on. Only include if the machine is always available.
