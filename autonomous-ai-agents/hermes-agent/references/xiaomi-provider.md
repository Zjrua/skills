# Xiaomi MiMo Provider

## LLM Provider

Xiaomi MiMo is a **built-in Hermes provider** (plugin at `plugins/model-providers/xiaomi/`).
**Do NOT use `custom_providers`** — configure via env vars:

```bash
# ~/.hermes/.env
XIAOMI_API_KEY=tp-xxxx...                     # Required
XIAOMI_BASE_URL=https://token-plan-cn.xiaomimimo.com/v1   # Default: https://api.xiaomimimo.com/v1
```

The default base_url is `https://api.xiaomimimo.com/v1`. Token Plan users must set `XIAOMI_BASE_URL` to the Token Plan endpoint.

### Available Models (verified May 2026)

| Model | Type |
|-------|------|
| `mimo-v2.5-pro` | Latest Pro (recommended for LLM) |
| `mimo-v2.5` | Standard |
| `mimo-v2-pro` | Legacy Pro |
| `mimo-v2-omni` | Legacy multimodal |
| `mimo-v2.5-omni` | Multimodal |
| `mimo-v2.5-tts` | TTS (see below) |
| `mimo-v2.5-tts-voiceclone` | TTS with voice cloning |
| `mimo-v2.5-tts-voicedesign` | TTS with voice design |
| `mimo-v2-tts` | Legacy TTS |
| `mimo-v2.5-tts` | Latest TTS |

## Xiaomi TTS (Custom Command Provider)

Xiaomi's TTS API is **NOT** OpenAI `/v1/audio/speech` compatible. It uses the
**chat completions** endpoint with a special format:

```
POST /v1/chat/completions
{
  "model": "mimo-v2.5-tts",
  "messages": [
    {"role": "user", "content": "Convert the following text to speech."},
    {"role": "assistant", "content": "<text to speak>"}
  ]
}
```

Response contains `choices[0].message.audio.data` as base64-encoded WAV.

### Config

Registered as a custom command TTS provider in `~/.hermes/config.yaml`:

```yaml
tts:
  provider: xiaomi      # switch from 'edge' to 'xiaomi' to use
  providers:
    xiaomi:
      type: command
      command: "~/.hermes/scripts/xiaomi-tts.sh {input_path} {output_path}"
      output_format: wav
      max_text_length: 5000
```

### Script

`~/.hermes/scripts/xiaomi-tts.sh` — a shell script that:
1. Reads text from `{input_path}`
2. Calls Xiaomi chat completions API with the TTS model
3. Decodes the base64 audio and writes to `{output_path}`
4. Output: WAV, 24000Hz, 16-bit, mono, PCM

### Pitfalls

- Requires assistant role message — the text-to-speak goes in the assistant's `content`
- The `command` format expects `{input_path}` and `{output_path}` placeholders
- Not compatible with `/voice on` (voice-to-voice mode) — only works via `text_to_speech_tool()`
