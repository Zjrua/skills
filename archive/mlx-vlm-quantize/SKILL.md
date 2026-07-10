---
name: mlx-vlm-quantize
description: Quantize multimodal VLM models for Apple Silicon/oMLX preserving vision capabilities. Use when re-quantizing Qwen or other multimodal models for local inference.
triggers:
  - quantize
  - mlx quantization
  - vlm convert
  - vision model
---

# MLX VLM Quantization Workflow

Quantize multimodal (vision-language) models for Apple Silicon with oMLX, preserving vision capabilities.

## Key Rules

- **MUST use `mlx_vlm.convert`** — never `mlx_lm convert`, which strips `vision_config` and visual weights, producing a text-only model.
- After quantization, verify `config.json` contains `"vision_config"` key.

## Installation

```bash
uv tool install mlx-vlm --with torch --with torchvision
```

## PATH Conflict Warning

`uv tool` installs to `~/.local/bin/`, but Hermes' `hermes-agent/venv/bin` may shadow it. Check with `which mlx_vlm.convert`. If wrong venv, use absolute path:

```bash
~/.local/share/uv/tools/mlx-vlm/bin/python -c "
from mlx_vlm.convert import main
import sys
sys.argv = ['mlx_vlm.convert',
  '--hf-path', '/path/to/source',
  '--mlx-path', '/path/to/output',
  '-q', '--q-bits', '4', '--q-group-size', '64',
  '--trust-remote-code']
main()
"
```

## Verification

1. Check config.json has `vision_config`: `'vision_config' in cfg` must be True
2. Restart oMLX — model discovery should show `type: vlm`, not `type: llm`
3. Test vision via API — `prompt_tokens` should be ~3800+ (includes image), not ~28 (text only)

## oMLX VLM Detection Logic

oMLX checks in order:
1. `architectures` against VLM_ARCHITECTURES
2. `model_type` against VLM_MODEL_TYPES (has `qwen3_5_moe` but NOT `qwen3_5`)
3. `vision_config` presence (catch-all fallback)

For `qwen3_5` type, detection relies on step 3 — `vision_config` MUST be present.

## Benchmarking Local Models (TTFT + tok/s)

Test prefill (TTFT) and generation speed with different prompt lengths:

```bash
# Quick speed test (max_tokens=64)
python3 -c "
import subprocess, time, json
for label, prompt in [('9字', '一句话介绍'), ('500字', '长文本'*50), ('2000字', '长文本'*200)]:
    body = json.dumps({'model': 'MODEL_NAME', 'messages': [{'role':'user','content':prompt}], 'max_tokens': 64, 'stream': True})
    cmd = ['curl','-s','-N','http://localhost:8000/v1/chat/completions','-H','Content-Type: application/json','-H','Authorization: Bearer APIKEY','-d',body]
    start = time.time(); first = None; tokens = 0
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True)
    for line in proc.stdout:
        if not line.strip().startswith('data: '): continue
        if line[6:].strip() == '[DONE]': break
        try:
            d = json.loads(line[6:])
            delta = d['choices'][0]['delta']
            for k in ['content','reasoning_content']:
                if k in delta and delta[k]:
                    if not first: first = time.time()
                    tokens += 1
        except: pass
    proc.wait()
    ttft = (first or time.time()) - start
    gen_t = time.time() - first if first else 0
    tps = tokens / gen_t if gen_t > 0 else 0
    print(f'{label:6s} | TTFT={ttft:.2f}s | {tps:.1f} tok/s')
"
```

## oMLX Restart Procedure

```bash
# Kill and restart oMLX serve
pkill -f "omlx.cli serve"; sleep 2
nohup /Applications/oMLX.app/Contents/MacOS/omlx-cli serve \
  --model-dir ~/.cache/lm-studio/models \
  --base-path ~/.omlx --port 8000 > /tmp/omlx.log 2>&1 &
sleep 8 && grep "Discovered model" /tmp/omlx.log
```

## Pitfalls

- `mlx_lm convert` silently drops vision — no error, just text-only output
- `uv tool` executables may be shadowed by Hermes venv in PATH
- torch/torchvision required at convert time for Qwen3VL video processor
- oMLX must be restarted after re-quantizing for model re-discovery
- 4bit quantization of ~52GB model yields ~15GB output (4.695 bpw)
