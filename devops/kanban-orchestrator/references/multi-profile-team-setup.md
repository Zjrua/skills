# Multi-Profile Kanban Team Setup

End-to-end workflow for creating a multi-agent kanban team with specialized profiles.

## Step 1: Create Profiles

Clone from default to inherit API keys and base config:

```bash
hermes profile create planner --clone --no-alias
hermes profile create coder --clone --no-alias
hermes profile create writer --clone --no-alias
hermes profile create researcher --clone --no-alias
hermes profile create reviewer --clone --no-alias
hermes profile create doubter --clone --no-alias
```

Each profile gets an independent directory at `~/.hermes/profiles/<name>/` with its own:
- `config.yaml` — model, toolsets, fallback chains
- `.env` — API keys (cloned from default)
- `SOUL.md` — system personality and role instructions

## Step 2: Write SOUL.md for Each Role

Each role needs a clear, concise SOUL.md defining:
- **Role** — what this agent does
- **What it does NOT do** — explicit boundaries (prevents role overlap)
- **Rules** — behavioral constraints
- **Output format** — what `kanban_complete` metadata should look like

### Key Role Distinctions

| Role | Timing | Questions | Works with |
|------|--------|-----------|------------|
| planner | Before execution | "How to break this down?" | — |
| doubter | Before execution | "Is this plan sound?" | planner's output |
| coder/writer/researcher | During execution | "Do the work" | task assignment |
| reviewer | After execution | "Is the output correct?" | worker output |

### Doubter vs Reviewer (avoid confusion)

- **Doubter** = upstream gate (questions the PLAN)
- **Reviewer** = downstream gate (checks the OUTPUT)
- Both exist to prevent errors, but at different stages

## Step 3: Configure Models per Profile

### Verify model names first

```bash
# Always verify — never guess model names
curl -s https://api.deepseek.com/v1/models -H "Authorization: Bearer $DEEPSEEK_API_KEY"
curl -s https://open.bigmodel.cn/api/paas/v4/models -H "Authorization: Bearer $ZAI_KEY"
```

### Configure model and fallback chain

Edit `~/.hermes/profiles/<name>/config.yaml`:

```yaml
model:
  default: glm-5.1        # primary model for this profile
  provider: zai           # provider name
fallback_model:            # first fallback (different cloud)
  provider: deepseek
  model: deepseek-v4-flash
fallback_providers: []     # keep empty — 2 layers is enough
```

### Cross-cloud pairing rule

If primary is `zai` → fallback is `deepseek` (and vice versa). This ensures one cloud's outage doesn't take down both layers.

### Cost-aware model assignment

- **Expensive/quota-limited models** (zai coding plan) → only for the most critical role (coder)
- **Cheap per-token models** (deepseek-v4-flash) → default for non-coder roles
- **Self-hosted models** (omlx) → NOT in fallback chains (machine may be off)

## Step 4: Configure Toolsets per Role

Restrict tools to what the role actually needs:

```yaml
# In config.yaml under agent:
agent:
  disabled_toolsets: ["terminal", "file", "web", "browser"]  # e.g., for planner
```

| Role | disabled_toolsets | Reason |
|------|-------------------|--------|
| planner | terminal, file, web, browser | Only decomposes, doesn't execute |
| coder | (none) | Needs full dev capability |
| writer | terminal | Focus on content, not system access |
| researcher | (none) | Needs web search and file access |
| reviewer | (none) | Needs to read and verify |
| doubter | terminal | Analytical role, no execution |

## Step 5: Initialize Kanban Board

```bash
hermes kanban init           # create board (idempotent)
hermes kanban boards         # verify board exists
```

## Step 6: Create Tasks with Dependencies

```bash
# Create tasks
hermes kanban create "title" --assignee <profile>

# Link dependencies (parent must complete before child)
hermes kanban link <parent_id> <child_id>
```

The dependency engine auto-promotes blocked tasks when all parents reach `done`.

## Pitfalls

1. **Don't skip model name verification** — a wrong model name silently fails at runtime
2. **Don't put self-hosted models in fallback chains** — they're unreliable as fallbacks
3. **Don't give planner execution tools** — it breaks the "decompose, don't execute" rule
4. **Keep fallback chains short (2 layers)** — more layers = slower failure cascades
5. **custom_providers must exist in profiles that reference them** — when fallback uses zai but primary is deepseek, ensure `custom_providers` has the zai entry in that profile's config.yaml
