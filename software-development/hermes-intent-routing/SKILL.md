---
name: hermes-intent-routing
description: Extend Hermes Agent with Router LLM-based intent routing — classify user messages by intent (chat/code/math/search/tool) and route to different models accordingly.
version: 1.0.0
author: Hermes Agent
tags: [hermes, routing, intent, llm, model-selection]
---

# Hermes Intent-Based Model Routing

## Overview

Hermes Agent has built-in `smart_model_routing` (keyword-based simple/complex bifurcation). This skill extends it with **intent-based routing**: a small/fast LLM classifies the user's intent, then a routing table maps each intent to a specific model+provider.

## Architecture

```
User message → Router LLM (glm-4-flash, ~0.5s)
                     ↓
    Intent classification (chat/code/math/search/tool/default)
                     ↓
    Route table lookup → target model + provider
                     ↓
    AIAgent uses target model to respond
```

## Files Modified/Created

| File | Action | Purpose |
|------|--------|---------|
| `agent/intent_router.py` | **NEW** | Router LLM client, intent classification, route lookup, caching |
| `agent/smart_model_routing.py` | **MODIFIED** | Extended `resolve_turn_route()` to support `mode: "intent"` |
| `hermes_cli/config.py` | **MODIFIED** | Added `mode`, `intent_router`, `routes` to DEFAULT_CONFIG |
| `cli.py` | **MODIFIED** | Added `mode: "simple"` to CLI defaults |

## Key Code Locations

- **Routing entry point**: `cli.py::_resolve_turn_agent_config()` (L2836) — called from CLI main loop (L7824), background tasks (L5886), query mode (L6020), cron (L780)
- **Route resolution**: `agent/smart_model_routing.py::resolve_turn_route()` — the single function all callers use
- **Intent classifier**: `agent/intent_router.py::classify_intent()` — calls router LLM with a system prompt
- **Config schema**: `hermes_cli/config.py` DEFAULT_CONFIG `smart_model_routing` key (L473)

## Config Format (config.yaml)

```yaml
smart_model_routing:
  enabled: true
  mode: intent          # "simple" (original) or "intent" (new)
  max_simple_chars: 160
  max_simple_words: 28
  cheap_model: {}       # only used in "simple" mode
  intent_router:        # only used in "intent" mode
    provider: zai
    model: glm-4-flash  # fast, cheap model for classification
    timeout: 3          # seconds before fallback to primary
    api_key_env: ""     # optional env var for router API key
    base_url: ""        # optional override
  routes:
    - intent: chat      # casual conversation, greetings, Q&A
      provider: zai
      model: glm-4-flash
    - intent: code      # programming, debugging, architecture
      provider: zai
      model: glm-5.1
    - intent: math      # math, stats, data analysis
      provider: zai
      model: glm-5.1
    - intent: search    # web search, news, research
      provider: zai
      model: glm-5.1
    - intent: tool      # file ops, browser, cron, messaging
      provider: zai
      model: glm-5.1
    - intent: default   # required fallback
      provider: zai
      model: glm-5.1
```

## Design Decisions

1. **Backward compatible**: `mode: "simple"` preserves original keyword routing. Default is `"simple"`.
2. **Fail-safe**: Router LLM timeout/errors → falls back to `"default"` route → falls back to primary model.
3. **Caching**: SHA256-based cache with 5-min TTL avoids re-classifying identical messages. Max 200 entries.
4. **Truncation**: Only first 500 chars of user message sent to router to save tokens.
5. **Provider resolution**: Uses existing `resolve_runtime_provider()` so route entries support all providers (zai, openrouter, anthropic, custom, etc.).
6. **Temperature 0.0**: Router LLM uses deterministic output for consistent classification.

## Supported Intents

The router system prompt classifies into these categories:
- **chat**: Casual conversation, greetings, simple Q&A, jokes, opinions
- **code**: Programming, debugging, code review, architecture, DevOps
- **math**: Mathematics, statistics, data analysis, formulas, proofs
- **search**: Web search, news, current events, research
- **tool**: File operations, browser, cron jobs, messaging
- **default**: Anything else, complex multi-step tasks

To add new intents: update `_ROUTER_SYSTEM_PROMPT` in `intent_router.py` and add route entries in config.

## Testing

```bash
cd /root/.hermes/hermes-agent
source venv/bin/activate

# Quick smoke test
python3 -c "
from agent.intent_router import classify_intent, find_route_for_intent
config = {'provider': 'zai', 'model': 'glm-4-flash', 'timeout': 3}
routes = [
    {'intent': 'chat', 'provider': 'zai', 'model': 'glm-4-flash'},
    {'intent': 'code', 'provider': 'zai', 'model': 'glm-5.1'},
    {'intent': 'default', 'provider': 'zai', 'model': 'glm-5.1'},
]
print(classify_intent('hello', config, routes))
print(classify_intent('fix this bug', config, routes))
"
```

## Pitfalls

- **GLM models**: Must pass `extra_body={"enable_thinking": False}` to disable thinking mode on the router call, or it wastes tokens/slow.
- **API key resolution**: The router needs its own API key. It tries `api_key_env` → provider-specific env var → main config `api_key`. If none work, it silently falls back.
- **Cron compatibility**: `cron/scheduler.py` calls `resolve_turn_route()` — fully compatible, no changes needed.
- **Prompt caching**: Changing routing config mid-session is fine (route is resolved per-turn), but changing tools/system prompt is not (breaks caching).
- **`cli.py` has its own defaults dict** at L279 — must add `mode: "simple"` there too, not just in `config.py`.
