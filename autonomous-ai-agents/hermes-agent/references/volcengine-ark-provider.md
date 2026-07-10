# Volcengine Ark Provider (方舟 Coding Plan)

Custom provider for Volcengine Ark coding plan API.

## Configuration

Added to `~/.hermes/config.yaml` under `providers`:

```yaml
providers:
  volc-ark:
    base_url: https://ark.cn-beijing.volces.com/api/coding/v3
    api_key: ark-13d33827-bb08-4854-b24c-e09ed5503baa-d9367
    default: doubao-seed-2-0-code-preview-260215
```

## API Endpoints

- **OpenAI-compatible**: `https://ark.cn-beijing.volces.com/api/coding/v3`
- **Anthropic-compatible**: `https://ark.cn-beijing.volces.com/api/coding` (not configured)

## Available Models (as of 2026-06-08)

54 active models. Coding-relevant:

| Model ID | Name | Notes |
|----------|------|-------|
| `doubao-seed-2-0-code-preview-260215` | doubao-seed-2-0-code | Code-specific, default |
| `doubao-seed-2-0-pro-260215` | doubao-seed-2-0-pro | General pro |
| `doubao-seed-2-0-lite-260428` | doubao-seed-2-0-lite | Lightweight |
| `deepseek-v4-pro-260425` | deepseek-v4-pro | DeepSeek V4 Pro |
| `deepseek-v4-flash-260425` | deepseek-v4-flash | DeepSeek V4 Flash |
| `kimi-k2-250905` | kimi-k2 | Kimi K2 |
| `kimi-k2-thinking-251104` | kimi-k2 | Kimi K2 with thinking |
| `qwen3-32b-20250429` | qwen3-32b | Qwen3 32B |
| `glm-4-7-251222` | glm-4-7 | GLM 4.7 |

## Verify Models

```bash
curl -s https://ark.cn-beijing.volces.com/api/coding/v3/models \
  -H "Authorization: Bearer $VOLC_ARK_API_KEY" | python3 -c "
import sys, json
data = json.loads(sys.stdin.read())
active = [m for m in data.get('data',[]) if m.get('status') != 'Shutdown']
for m in sorted(active, key=lambda x: x['id']):
    print(f'{m[\"id\"]}  ({m.get(\"name\",\"\")})')
"
```

## Test Connection

```bash
curl -s https://ark.cn-beijing.volces.com/api/coding/v3/chat/completions \
  -H "Authorization: Bearer <api_key>" \
  -H "Content-Type: application/json" \
  -d '{"model":"doubao-seed-2-0-code-preview-260215","messages":[{"role":"user","content":"say hello"}],"max_tokens":20}'
```

## Usage in Hermes

- `hermes model` → select `volc-ark` provider
- `/model volc-ark/doubao-seed-2-0-code-preview-260215`
- As fallback: add to `fallback_providers` in profile config

## Notes

- Uses OpenAI-compatible API format (v3 endpoint)
- 119 total models, 54 active (rest are Shutdown)
- Includes doubao-seed, deepseek, kimi, qwen, glm models
- Some models have "Retiring" status — check before relying on them
