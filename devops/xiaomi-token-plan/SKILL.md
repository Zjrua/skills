---
name: xiaomi-token-plan
description: "Configure Xiaomi MiMo Token Plan as a Hermes provider — model setup, TTS via chat completions, and STT via omni model audio input."
version: 1.0.0
author: Hermes Agent
tags: [xiaomi, mimo, token-plan, tts, stt, provider, custom-command]
---

# Xiaomi MiMo Token Plan Provider

Xiaomi's MiMo Token Plan (`token-plan-cn.xiaomimimo.com`) is an OpenAI-compatible API
for chat, vision, TTS, and multimodal models. This skill covers deploying it as a
Hermes provider, including non-standard TTS/STT integration.

## Provider Setup

```yaml
# ~/.hermes/.env
XIAOMI_API_KEY=tp-xxxx...
XIAOMI_BASE_URL=https://token-plan-cn.xiaomimimo.com/v1
```

Hermes has a **built-in** `xiaomi` provider (no need for `custom_providers`). The
default base_url is `https://api.xiaomimimo.com/v1`, override with `XIAOMI_BASE_URL`.

### Available Models (verified via `/v1/models`)

| Model | Type |
|-------|------|
| `mimo-v2.5-pro` | **Recommended** — latest Pro |
| `mimo-v2.5` | Standard |
| `mimo-v2-omni` | Multimodal (audio input) |
| `mimo-v2.5-tts` | TTS |
| `mimo-v2.5-tts-voiceclone` | TTS with voice cloning |
| `mimo-v2.5-tts-voicedesign` | TTS with voice design |
| `mimo-v2-pro` | Legacy Pro |
| `mimo-v2-tts` | Legacy TTS |

### Using as a model

```bash
hermes model                    # Interactive picker → select xiaomi
# Or config directly:
hermes config set model.provider xiaomi
hermes config set model.default mimo-v2.5-pro
```

## TTS (Text-to-Speech) — Custom Command Provider

Xiaomi's TTS models (`mimo-v2.5-tts`) do **NOT** use the standard OpenAI
`/audio/speech` endpoint. Instead, they work through **chat completions**:

- User message: context/instruction
- Assistant message: text to be spoken
- Response `choices[0].message.audio.data`: **base64-encoded WAV audio**

A custom command provider script bridges this gap:

### Script: `~/.hermes/scripts/xiaomi-tts.sh`

```bash
# Usage: xiaomi-tts.sh <input_text_file> <output_audio_path>
# - Reads text from input_text_file
# - Calls mimo-v2.5-tts via chat completions
# - Extracts and decodes audio.data to output_audio_path (WAV format)
```

### Config

```yaml
# ~/.hermes/config.yaml
tts:
  provider: xiaomi          # or keep 'edge' and switch when needed
  providers:
    xiaomi:
      type: command
      command: "~/.hermes/scripts/xiaomi-tts.sh {input_path} {output_path}"
      output_format: wav
      max_text_length: 5000
```

**To switch**: change `tts.provider: xiaomi` in config.yaml, or `hermes config set tts.provider xiaomi`.

**Pitfall**: The `~` expansion works because the command runs via `shell=True` in Hermes' TTS tool. Always use the full path or `~` — `$HOME` may or may not be set depending on how the gateway runs.

## STT (Speech-to-Text) — Omni Model via Local Command

Xiaomi's `mimo-v2-omni` model supports **native audio input** through chat completions
(confirmed — returns `audio_tokens` in usage). This avoids installing
`faster-whisper` and saves ~1GB RAM.

Uses Hermes' `HERMES_LOCAL_STT_COMMAND` env var mechanism (check
`tools/transcription_tools.py`, function `_transcribe_local_command`).

### How it works

1. Hermes receives voice message from gateway
2. `_prepare_local_audio()` converts to WAV via ffmpeg
3. Custom script reads WAV, base64-encodes it
4. Sends to `mimo-v2-omni` with `audio_url` content type
5. Extracts transcribed text from response
6. Writes to `{output_dir}/xiaomi-omni.txt`

### API Format

The omni model accepts audio via the OpenAI multimodal chat completions format:

```json
{
  "model": "mimo-v2-omni",
  "messages": [{"role": "user", "content": [
    {"type": "text", "text": "Transcribe this audio:"},
    {"type": "audio_url", "audio_url": {"url": "data:audio/wav;base64,<base64_audio>"}}
  ]}],
  "max_tokens": 2048
}
```

Response contains `prompt_tokens_details.audio_tokens` confirming audio processing.

### Script: `~/.hermes/scripts/xiaomi-stt.sh`

```bash
# Usage: xiaomi-stt.sh <input_audio_path> <output_dir> <language> <model>
# - input_audio_path: WAV file (pre-converted by Hermes)
# - output_dir: where to write xiaomi-omni.txt
# - language: zh / en / etc.
# - model: mimo-v2-omni (default)
```

### Config

```bash
# ~/.hermes/.env
HERMES_LOCAL_STT_COMMAND=~/.hermes/scripts/xiaomi-stt.sh {input_path} {output_dir} {language} {model}
HERMES_LOCAL_STT_LANGUAGE=zh
```

```yaml
# ~/.hermes/config.yaml
stt:
  enabled: true
  provider: local                 # uses the local command mechanism
  local:
    model: base                   # ignored by custom script, but required field
    language: zh                  # passed as {language} placeholder
```

**Pitfall**: `source ~/.hermes/.env` in terminal will error on this env var because
`{input_path}` gets interpreted by bash. The gateway/Hermes config loader reads the
`.env` file properly — the env var is only used programmatically by
`transcription_tools.py`.

**Pitfall**: `faster-whisper` must NOT be installed when using `HERMES_LOCAL_STT_COMMAND`
— the local command path is only taken when the whisper binary is absent. If
`faster_whisper` is installed, the `local` provider will try to use it instead.

## File Layout

```
~/.hermes/
├── scripts/
│   ├── xiaomi-tts.sh     # TTS: text → WAV via chat completions
│   └── xiaomi-stt.sh     # STT: WAV → text via omni model
├── config.yaml            # tts.providers.xiaomi + stt config
└── .env                   # XIAOMI_API_KEY, XIAOMI_BASE_URL, HERMES_LOCAL_STT_*
```

## Linked Files

| File | Description |
|------|-------------|
| `references/xiaomi-api-shapes.md` | Exact JSON request/response shapes for TTS and STT API calls |
| `templates/config-snippet.yaml` | Complete config.yaml + .env snippet for quick deployment |

## Pitfalls

1. **`mimo-v2-omni` is NOT for chat completions without audio** — it's a multimodal
   model. For text-only chat, use `mimo-v2.5-pro` or `mimo-v2.5`.
2. **TTS model returns audio in chat completions response** — not via standard
   `/audio/speech`. The `audio.data` field contains raw base64 WAV bytes.
3. **Server RAM matters** — at 3.8GB RAM, avoid installing `faster-whisper` as it
   consumes ~1GB for the base model. The omni-based STT uses zero local ML resources.
4. **Custom command TTS/STT scripts must load `.env` internally** — when run as
   subprocesses by Hermes, they don't inherit the Hermes Python env vars. Each script
   reads `~/.hermes/.env` for `XIAOMI_*` variables.
5. **Config reload** — after changing TTS/STT config, the gateway needs `/restart`
   (or CLI exit & relaunch). `/reset` in-session is not enough for TTS/STT changes.
