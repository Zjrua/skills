# Xiaomi Token Plan — Scripts Reference

## TTS: `~/.hermes/scripts/xiaomi-tts.sh`

Converts text to speech using `mimo-v2.5-tts` via chat completions.

### Algorithm

1. Load `XIAOMI_API_KEY` and `XIAOMI_BASE_URL` from `~/.hermes/.env`
2. Read input text from `$1`
3. Build JSON payload with assistant role containing the text to speak
4. POST to `${BASE_URL}/chat/completions`
5. Extract `choices[0].message.audio.data` (base64)
6. Decode and write to `$2`

### JSON Payload Shape

```json
{
  "model": "mimo-v2.5-tts",
  "messages": [
    {"role": "user", "content": "Convert the following text to speech."},
    {"role": "assistant", "content": "<text to speak>"}
  ]
}
```

### Response Shape

```json
{
  "choices": [{
    "message": {
      "audio": {
        "data": "<base64 WAV>",
        "expires_at": null,
        "transcript": null
      }
    }
  }]
}
```

---

## STT: `~/.hermes/scripts/xiaomi-stt.sh`

Transcribes audio to text using `mimo-v2-omni` native audio input.

### Algorithm

1. Load `XIAOMI_API_KEY` and `XIAOMI_BASE_URL` from `~/.hermes/.env`
2. Read WAV file from `$1`, base64-encode
3. Build JSON payload with `audio_url` content type
4. POST to `${BASE_URL}/chat/completions`
5. Extract `choices[0].message.content` as transcript
6. Write to `${output_dir}/xiaomi-omni.txt`

### JSON Payload Shape

```json
{
  "model": "mimo-v2-omni",
  "messages": [{"role": "user", "content": [
    {"type": "text", "text": "请将这段音频完整地转写为文字"},
    {"type": "audio_url", "audio_url": {"url": "data:audio/wav;base64,<base64>"}}
  ]}],
  "max_tokens": 2048
}
```

### Response Shape

```json
{
  "choices": [{"message": {"content": "<transcribed text>"}}],
  "usage": {
    "prompt_tokens_details": {"audio_tokens": <count>}
  }
}
```

### MIME Type Mapping

| Extension | MIME |
|-----------|------|
| wav/WAV | `audio/wav` |
| mp3/MP3 | `audio/mpeg` |
| ogg/OGG | `audio/ogg` |
| m4a/M4A | `audio/mp4` |
