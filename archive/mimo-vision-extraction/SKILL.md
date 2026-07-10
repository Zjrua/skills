---
name: mimo-vision-extraction
description: Use Xiaomi mimo-v2.5 vision model to extract structured data from images (handwritten tables, printed forms, etc.) via OpenAI-compatible API. Covers API config, image preprocessing, prompt design, and multi-image merge strategies.
version: 1.0.0
author: Hermes Agent
---

# mimo-v2.5 Vision Data Extraction

Extract structured data from images using Xiaomi's mimo-v2.5 multimodal model via OpenAI-compatible API.

## API Configuration

```python
from openai import OpenAI
client = OpenAI(
    api_key=os.environ.get("XIAOMI_API_KEY"),  # from ~/.hermes/.env
    base_url="https://token-plan-cn.xiaomimimo.com/v1"
)
MODEL = "mimo-v2.5"
```

## Image Preprocessing (Critical)

mimo-v2.5 accepts base64-encoded images. **Large images (5MB+) must be resized** or API calls take 60s+ and may timeout.

```python
from PIL import Image
import base64, io

def prepare_image(image_path, max_dim=2048):
    """Resize large images before API call. Returns (base64_str, mime_type)."""
    img = Image.open(image_path)
    if max(img.size) > max_dim:
        ratio = max_dim / max(img.size)
        img = img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    fmt = "PNG" if image_path.lower().endswith(".png") else "JPEG"
    img.save(buf, format=fmt, quality=85)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return b64, f"image/{fmt.lower()}"
```

- **max_dim=2048**: Good balance of quality vs speed (~0.8MB JPEG, ~60s API response)
- **Original 6-8MB images**: ~70s API response after resize; unresized may timeout
- **Cropped/zoomed images (<500px)**: Model often returns empty results — always prefer original full-size images

## API Call

```python
response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": "你是数据提取助手。只输出JSON，不要任何解释。"},
        {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}},
            {"type": "text", "text": PROMPT}
        ]}
    ],
    max_completion_tokens=16384,  # MUST be 16384+ for large tables
    temperature=0.1,
)
```

**Key parameters**:
- `max_completion_tokens=16384`: Default 4096 truncates large table output. Model regularly uses 8k-12k tokens.
- `temperature=0.1`: Low temperature for deterministic data extraction
- `response_format={"type": "json_object"}`: Use for reliable JSON parsing; set `max_completion_tokens=16384` to avoid truncation. Without it, model may output explanation text before JSON.

## Prompt Design for Structured Extraction

```python
PROMPT = """\
请逐行提取这张表格图片中的所有数据。

输出格式：
{"columns": ["列名1", "列名2", ...], "data": [["值1", "值2", ...], ...]}

注意：
- columns 写你看到的中文表头
- data 中每行是一个数组，按从左到右的顺序填值
- 只提取你确信看到的数字和文字，不确定的留空 ""
- 不要猜测或推断
- 忽略红色标注
- 被划掉的行跳过
- 只输出JSON"""
```

**Tips**:
- `data: [["值1", ...]]` (list of lists) works better than `data: [{"col1": "值1"}]` for positional alignment
- **For critical alignment**: enforce fixed-length arrays with explicit count:
  ```
  PROMPT = f"""提取数据。输出: {{"data":[[v1,v2,...,v{N}]]}}
  每行恰好{N}个元素，严格按列顺序。空值填""。不要跳过任何列。"""
  ```
- Keep prompt short — verbose prompts reduce extraction accuracy
- "只提取你确信看到的" reduces hallucination

## JSON Parsing (Robust)

```python
def clean_json(raw):
    cleaned = re.sub(r"```(?:json)?\s*", "", raw)
    cleaned = re.sub(r"```\s*$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    depth = start = 0
    for i, ch in enumerate(cleaned):
        if ch == '{':
            if depth == 0: start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(cleaned[start:i+1])
                except json.JSONDecodeError:
                    pass
    return None
```

## Multi-Image Merge Strategy

### Method A: Fixed Column Indices (Recommended for Known Schema)

When the table has a known column structure, **give the model fixed column indices** instead of letting it name columns. This avoids all naming inconsistencies.

```python
STD_HEADERS = ["序号", "姓名", "性别", "年龄", "出生年月", "仰卧起坐成绩", ...]
HEADERS_STR = ", ".join(f"{i+1}.{h}" for i, h in enumerate(STD_HEADERS))

PROMPT = f"""提取表格数据。有{len(STD_HEADERS)}列，从左到右依次是：
{HEADERS_STR}
输出：{{"rows": [{{"1": "值", "2": "值", ...}}]}}。用列序号做key，不确定的不写。"""
```

Merge by sequence number (col 1) — same schema guarantees alignment.

### Method B: Name-Based Merge (Unknown Schema)

1. **Each image independently** -> extract `{"columns": [...], "data": [[...]]}`
2. **Union all column names** (preserve order, first-seen wins)
3. **Concatenate rows** — map each image's columns to the unified set by name
4. **Drop empty columns**

**Do NOT match rows across images by sequence number** unless all images share the same fixed schema.

### Key Finding

Handwritten tables: model **cannot reliably identify column headers** (hallucinates or truncates names). Data VALUES are accurate, but column NAMES are not. Always prefer fixed-index approach for handwritten sources. User expectation: "不用管列名语义对齐，只要结构对齐" — structural consistency matters, not semantic accuracy.

## Thread-Based Timeout (Prevent Hangs)

API calls can hang indefinitely. Use a thread with timeout to skip unresponsive images:

```python
import threading

def extract_with_timeout(client, messages, timeout=120):
    result = [None]
    def _call():
        result[0] = client.chat.completions.create(
            model=MODEL, messages=messages,
            max_completion_tokens=16384, temperature=0.1,
        )
    t = threading.Thread(target=_call)
    t.start()
    t.join(timeout=timeout)
    if t.is_alive():
        return None  # timed out — skip this image
    return result[0]
```

## Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| Model returns `{"columns":[], "data":[]}` | Image too zoomed in or blurry | Use original full-size images |
| Output truncated (`finish_reason: length`) | max_completion_tokens too low | Set to 16384 |
| Duplicate columns after merge | Name differences ("仰卧起坐成绩" vs "仰卧起坐 成绩") | Strip whitespace from column names |
| API timeout (>60s) | Image too large | Resize to max 2048px; use thread timeout (120s) |
| `finish_reason: length` | Output truncated mid-JSON | Increase `max_completion_tokens`; detect via `resp.choices[0].finish_reason` |
| Hallucinated column names | Model guessing from data patterns | Prompt: "只提取你确信看到的" |
| Handwritten tables: columns misaligned | Model can't read fuzzy headers | Use fixed column indices (Method A) instead of letting model name columns |
| Different images have same data under different column names ("仰卧起坐成绩" vs "仰卧起坐 成绩") | Slight naming variance across images | Use positional index merge, not name-based merge |
| **Values appear in wrong columns (e.g. height in "姓名" column)** | **Forcing a single column mapping across images with different table structures** | **Survey images first, group by table type, extract each group separately** |
| **Model inserts extra values or shifts columns** | **Named-key JSON output lets model skip unreadable columns, shifting all subsequent values** | **Use fixed-length array output: `{"data": [[v1,v2,...,vN]]}` with explicit "每行恰好N个元素" in prompt** |
| **No output visible for minutes after background start** | **Python stdout buffering** | **Use `python3 -u script.py` or `PYTHONUNBUFFERED=1`** |
| **Script processes backup/cache dirs as data folders** | **Folder filter too loose (e.g. only excluding "output")** | **Explicitly exclude `__pycache__`, `output*`, `cropped`, `backup*` in folder iteration** |

## Performance Reference

| Image Size | Base64 | API Response | Tokens Used |
|------------|--------|-------------|-------------|
| 2048px (resized from 6MB) | ~1MB | ~60-70s | ~8k-12k |
| 500px crop | ~50KB | ~5-10s | ~1k-3k |

## CSV Output

```python
def write_csv(path, headers, rows):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(headers)
        for row in rows:
            w.writerow(row)
```

Use `utf-8-sig` encoding for Excel compatibility with Chinese characters.

## Verification Methodology

**Do NOT use vision model as ground truth for verification** — the vision model itself makes reading errors on handwritten tables. Instead, use domain knowledge:

```python
# Example: verify 60m run times are reasonable
for row in rows:
    t = float(row["60m_time"])
    assert 5 < t < 15, f"Unreasonable 60m time: {t}s"
```

**Better verification approaches:**
1. **Value range checks**: Each column should have values in a plausible range (e.g., 60m times: 5-15s, heights: 140-200cm)
2. **Cross-row consistency**: Check that ranks are integers, scores increase/decrease monotonically where expected
3. **Spot-check with human**: Pick 2-3 random rows per image, have user verify against original

**Why vision verification fails:** When you ask vision to "read row 5", it may misalign columns itself, producing different errors than the extraction model. Two wrong readings don't make a right.

## Background Process Tips

When running extraction scripts in background:
- **Always use `python3 -u script.py`** — without `-u`, Python buffers stdout and you see zero output for minutes
- `PYTHONUNBUFFERED=1` as env var also works
- `tee` can buffer; prefer writing directly to a log file
- Monitor progress via output file timestamps: `ls -lt output_dir/*.csv`
- For long-running batch jobs (20+ images), expect ~60-80s per image API response time
