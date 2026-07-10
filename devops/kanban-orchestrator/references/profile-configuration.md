# Kanban Profile Configuration Guide

## Verified model names (API-checked 2026-05-27)

| Provider | API endpoint | Verified model IDs |
|----------|-------------|-------------------|
| **zai (智谱)** | `open.bigmodel.cn/api/coding/paas/v4` | `glm-5.1`, `glm-5-turbo`, `glm-5`, `glm-4.7`, `glm-4.6`, `glm-4.5`, `glm-4.5-air` |
| **deepseek** | `api.deepseek.com/v1` | `deepseek-v4-flash`, `deepseek-v4-pro` |

⚠️ Model names change over time. Always verify via `curl <endpoint>/models` before configuring.

## Profile config.yaml key sections

```yaml
# Primary model
model:
  default: deepseek-v4-flash
  provider: deepseek

# First fallback (when primary fails)
fallback_model:
  provider: zai
  model: glm-5-turbo

# Second+ fallback chain (optional, keep short)
fallback_providers: []

# Worker iteration limits (research-heavy profiles need more)
agent:
  max_turns: 90        # default is 50, too low for web search tasks
  disabled_toolsets:   # e.g. ["terminal"] for non-coding profiles

# Delegation config — MUST match primary to avoid routing errors
delegation:
  provider: deepseek
  model: deepseek-v4-flash
  max_iterations: 80   # default is 50, too low for multi-step research

# Custom providers (needed when fallback uses a different cloud)
custom_providers:
  - name: zai
    api_key: <key>
    base_url: https://open.bigmodel.cn/api/coding/paas/v4
    model: glm-5-turbo
    api_mode: chat_completions
```

## Fallback chain design principles

1. **Cross-cloud redundancy**: primary on one cloud, fallback on another
2. **Keep it to 2 layers**: primary + one fallback. More layers = more things to break
3. **Don't use local/self-hosted as fallback** unless reliably available (e.g., a Mac that's not always on is NOT a reliable fallback)
4. **Cost matters**: use expensive models only where they matter (coder), cheap models elsewhere (planner, writer)

## SOUL.md template for kanban workers

Each profile needs a clear SOUL.md defining:
- **Role**: one-sentence identity
- **What you do**: specific capabilities
- **What you do NOT do**: boundaries (especially vs other profiles)
- **Rules**: kanban protocol requirements
- **Output format**: expected handoff structure

Key rule: every worker must call `kanban_complete()` or `kanban_block()` before exiting. Exiting without either is a protocol violation → auto-block.
