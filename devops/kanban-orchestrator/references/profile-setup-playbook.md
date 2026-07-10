# Kanban Profile Setup Playbook

Session-validated workflow for creating kanban worker profiles.

## Step 1: Verify model names via API

**Never guess model names.** Call each provider's models endpoint:

```bash
# Zhipu (zai)
curl -s https://open.bigmodel.cn/api/paas/v4/models \
  -H "Authorization: Bearer $ZAI_API_KEY" | python3 -m json.tool

# DeepSeek
curl -s https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer $DEEPSEEK_API_KEY" | python3 -m json.tool
```

Use the exact `id` values returned. Common mistake: using `deepseek-chat` when the real name is `deepseek-v4-flash`.

## Step 2: Create profiles

```bash
for profile in planner coder writer researcher reviewer doubter; do
  hermes profile create $profile --clone --no-alias
done
```

## Step 3: Write SOUL.md for each profile

Each profile needs a focused personality in `~/.hermes/profiles/<name>/SOUL.md`:
- **planner**: Decompose and route only. "Don't execute yourself."
- **coder**: Full dev capabilities. Report changed_files/tests/decisions.
- **writer**: Content creation. Match tone and cite sources.
- **researcher**: Search and synthesize. Always cite URLs.
- **reviewer**: Post-execution QA. Rate severity. Create remediation tasks.
- **doubter**: Pre-execution skepticism. Challenge plans before they run.

Key distinction: **doubter vs reviewer** — doubter works UPSTREAM (before execution, questions plans), reviewer works DOWNSTREAM (after execution, checks output quality).

## Step 4: Configure models and fallback chains

Design principle: **only 2 layers per chain (primary + one fallback)**. More is wasteful. The fallback should be a different cloud provider for availability redundancy.

```yaml
# coder: uses premium model, falls back to cheaper cloud
model:
  default: glm-5.1
  provider: zai
fallback_model:
  provider: deepseek
  model: deepseek-v4-flash
fallback_providers: []  # empty — don't chain local models (unreliable availability)

# non-coder profiles: cheap cloud primary, different cloud fallback
model:
  default: deepseek-v4-flash
  provider: deepseek
fallback_model:
  provider: zai
  model: glm-5-turbo
fallback_providers: []
```

Availability ranking for fallback design:
1. **deepseek**: most reliable (cloud, high concurrency, pay-per-token)
2. **zai**: cloud but has quota/concurrency limits on coding plans
3. **omlx**: local (Mac), not always on — do NOT include in fallback chains

## Step 5: Configure delegation for worker profiles

Workers that use `delegate_task` need explicit delegation config matching their primary model:

```yaml
delegation:
  provider: deepseek        # match the worker's primary provider
  model: deepseek-v4-flash  # match the worker's primary model
  max_iterations: 80        # research tasks need more than default 50
```

Without this, sub-agents may route to a wrong provider (e.g. deepseek provider with a zai model name → HTTP 400).

## Step 6: Tune per-profile settings

| Profile | disabled_toolsets | max_turns | Notes |
|---------|-------------------|-----------|-------|
| planner | terminal, file, web, browser | 30 | Only decompose, don't execute |
| coder | (none) | 60 | Full dev capabilities |
| writer | terminal | 40 | Content only |
| researcher | (none) | 90 | Search-heavy, needs many turns |
| reviewer | (none) | 40 | Focused QA |
| doubter | terminal | 30 | Read plans, output critique |

## Step 7: Ensure custom_providers is present in profiles that need cross-provider fallback

When a profile's primary is `deepseek` but fallback uses `zai`, the `custom_providers` list must include the zai entry:

```yaml
custom_providers:
  - name: zai
    api_key: <key>
    base_url: https://open.bigmodel.cn/api/coding/paas/v4
    model: glm-5-turbo
    api_mode: chat_completions
```

Clone (`--clone`) copies this from default profile automatically.

## Known Pitfalls

1. **Dependency promotion deadlock**: `promote_ready_tasks()` only scans `todo` status, not `blocked`. If dispatcher auto-blocks a child before parents complete, it stays blocked forever. Manual `hermes kanban unblock <id>` is needed after parents finish.

2. **Protocol violation**: Workers must call `kanban_complete` or `kanban_block` before exiting. If iteration limit is reached, the worker exits cleanly (rc=0) without finalizing → auto-block. Budget iterations: start wrapping up at ~80% of max_turns.

3. **Delegation model mismatch**: Sub-agents inherit `delegation.*` config, not the primary model. Always set `delegation.provider` and `delegation.model` explicitly in worker profiles.
