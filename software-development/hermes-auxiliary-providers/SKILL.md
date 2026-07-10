---
name: hermes-auxiliary-providers
description: "Configure Hermes auxiliary model providers (vision, compression, web extraction, etc.) to use specific backends from custom_providers or other providers."
---

# Hermes Auxiliary Provider Configuration

Hermes uses auxiliary models for side tasks like vision analysis, context compression, web extraction, and more. These can be configured independently from the main chat model in `~/.hermes/config.yaml`.

## Config Structure

```yaml
auxiliary:
  vision:
    provider: ''        # Provider name or 'auto'
    model: ''           # Model slug (leave empty for provider default)
    base_url: ''        # Direct endpoint override (forces provider='custom')
    api_key: ''         # API key for direct endpoint
    timeout: 30
    download_timeout: 30
  compression:
    provider: ''
    model: ''
    base_url: ''
    api_key: ''
    timeout: 120
  web_extract:
    provider: ''
    model: ''
    base_url: ''
    api_key: ''
    timeout: 360
```

## Provider Resolution Chain (from source: `agent/auxiliary_client.py`)

Priority order for resolving provider + model:

1. **Explicit args** (function call parameters) — always win
2. **Env var overrides** — e.g. `AUXILIARY_VISION_PROVIDER`, `AUXILIARY_VISION_MODEL`, `AUXILIARY_VISION_BASE_URL`, `AUXILIARY_VISION_API_KEY`
3. **Config file** — `auxiliary.{task}.*` in config.yaml
4. **Auto mode** — full auto-detection chain

## Key Insight: Named Custom Providers

When you set `auxiliary.vision.provider: bailian` (or any name matching a `custom_providers` entry), Hermes automatically looks up `base_url` and `api_key` from the `custom_providers` list in config.yaml. **No need to manually fill in `base_url`/`api_key` in the auxiliary section.**

The resolution happens via `_get_named_custom_provider()` in `resolve_provider_client()`.

Example: If you have:
```yaml
custom_providers:
  - name: bailian
    base_url: https://coding.dashscope.aliyuncs.com/v1
    api_key: sk-xxx
```

Then simply setting:
```yaml
auxiliary:
  vision:
    provider: bailian
    model: qwen3.5-plus
```

Will automatically use bailian's base_url and api_key for vision tasks.

## Vision Auto-Detection Order

When `provider: auto`:
1. Active main provider (if known vision-capable)
2. OpenRouter
3. Nous Portal
4. Stop

Known vision-capable providers in `_VISION_AUTO_PROVIDER_ORDER`: openrouter, nous, openai-codex, anthropic, custom.

For "exotic" providers (DeepSeek, Alibaba, named custom, etc.), auto mode falls through to `resolve_provider_client` which checks `custom_providers`.

## Direct Endpoint Override

If you set `base_url` in the auxiliary config, provider is forced to `"custom"` and uses that endpoint directly:

```yaml
auxiliary:
  vision:
    provider: auto       # ignored when base_url is set
    model: qwen3.5-plus
    base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
    api_key: sk-xxx      # required for direct endpoint
```

Use this when the provider is NOT in `custom_providers`.

## Common Auxiliary Provider Defaults

From `_API_KEY_PROVIDER_AUX_MODELS`:
| Provider | Default Aux Model |
|----------|------------------|
| zai | glm-4.5-flash |
| kimi-coding | kimi-k2-turbo-preview |
| minimax / minimax-cn | MiniMax-M2.7 |
| anthropic | claude-haiku-4-5-20251001 |

## Verification

After changing config, restart the Hermes gateway:
```bash
hermes gateway restart
```

## OMLX (Local MLX Inference) via ZeroTier

OMLX runs Qwen MLX-quantized models on macOS, exposed via OpenAI-compatible API. When the Mac is on the same ZeroTier network, Hermes can use it as a custom provider — for fallback, vision, or any auxiliary task.

### Config Pattern (config.yaml)

```yaml
custom_providers:
  # ... other providers ...
  - name: omlx
    api_key: 'YOUR_KEY'
    api_mode: chat_completions
    base_url: http://192.168.192.x:8000/v1
    model: Qwen3.6-35B-A3B-MLX-4bit
    context_length: 262144        # Qwen3.6-35B-A3B max context
  - name: omlx-vision
    api_key: 'YOUR_KEY'
    api_mode: chat_completions
    base_url: http://192.168.192.x:8000/v1
    model: Qwen3.5-9B-MLX-4bit
    context_length: 131072        # Qwen3.5-9B max context

# Fallback chain — OMLX as last resort
fallback_model:
  provider: deepseek
  model: deepseek-v4-flash
fallback_providers:
  - provider: omlx
    model: Qwen3.6-35B-A3B-MLX-4bit
    context_length: 262144

# Vision auxiliary using the 9B model
auxiliary:
  vision:
    provider: omlx-vision
    model: Qwen3.5-9B-MLX-4bit
    base_url: http://192.168.192.x:8000/v1
    api_key: 'YOUR_KEY'
    timeout: 60          # MLX models are slower than cloud, raise timeout
    download_timeout: 60
```

### Key Points
- **Timeout**: MLX inference on consumer Macs is slower than cloud APIs. Raise `timeout` to 60+ seconds for both vision and chat.
- **context_length**: Set to the model's max (Qwen3.5-9B=128K, Qwen3.6-35B-A3B=256K) so Hermes doesn't artificially truncate.
- **Named custom providers for auxiliary**: When `auxiliary.vision.provider` matches a `custom_providers` name, Hermes auto-resolves `base_url`/`api_key`. But setting them explicitly in the auxiliary section is also fine and more robust.
- **API compatibility**: OMLX exposes `/v1/models` and `/v1/chat/completions` — fully OpenAI-compatible, works with Hermes's `chat_completions` api_mode.
- **ZeroTier dependency**: The `192.168.192.x` address requires ZeroTier to be running on both machines. If ZeroTier is down, all OMLX calls will fail — that's fine for a last-resort fallback, but be aware for vision tasks.

### Model Load Latency
OMLX lazily loads models — first request to a cold model incurs ~3-5s load time (returned in `model_load_duration` field). Subsequent requests are faster. This is normal.

## Pitfalls

- The `api_key` in `custom_providers` is redacted in terminal output by Hermes security (`redact_secrets: true`). Use `patch` tool instead of `cat`/`grep` to read it.
- `qwen3.5-plus` on Bailian supports vision natively (Qwen3.5 series supports `vl_high_resolution_images`). For pure VL models, use `qwen-vl-plus`, `qwen3-vl-plus`, etc.
- Auxiliary tasks (vision, compression) run as separate API calls — they use the auxiliary provider, NOT the main chat model.
- When using `custom_providers` for both fallback and auxiliary, give each a distinct `name` so Hermes can resolve them independently (e.g. `omlx` vs `omlx-vision`).
