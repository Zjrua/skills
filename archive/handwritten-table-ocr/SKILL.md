---
name: handwritten-table-ocr
description: Extract structured data from photos of handwritten tables using vision LLMs. Covers batch processing, prompt engineering for clean CSV output, and common pitfalls.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [OCR, vision, handwritten, tables, CSV, data-extraction]
    related_skills: [ocr-and-documents, batch-image-ocr]
---

# Handwritten Table OCR via Vision Models

Extract structured data from photos of handwritten paper tables (体测数据, exam scores, handwritten records, etc.) using vision LLMs.

## When to Use

- Photos of handwritten paper tables (not digital/scanned PDFs)
- Old handwritten records, physical logbooks, paper forms
- Tables with irregular handwriting, varying ink colors, fold marks
- When pymupdf/marker-pdf can't handle the format (these are for PDFs, not photos)

## Key Findings (Do / Don't)

| Do | Don't |
|-----|-------|
| Send full uncropped image to vision model | Try programmatic cropping (brightness/edge detection fails on uneven lighting) |
| **Survey ALL images first, group by table type** | Assume all images in a folder have the same column structure |
| Ask for specific columns only (focused prompt) | Ask model to extract "all data" (produces garbled column confusion) |
| Request CSV format directly in prompt | Ask for "table format" (model adds verbose reasoning text) |
| Process 1-3 images per vision call | Send 5+ images at once (model loses track) |
| Use mimo-v2.5 or similar multimodal model | Assume text-only models can do this |
| **Use `python3 -u script.py` for background runs** | Run without `-u` — stdout buffers silently, no progress visible for minutes |

## Workflow

### Step 1: Survey the images (MANDATORY — do not skip)

**Critical**: Look at 1-2 sample images from EACH subfolder. Different folders (and even images within the same folder) may have completely different table structures.

```
vision_analyze(image_url="path/to/sample.jpg",
    question="这是一张什么类型的表格？请列出从左到右所有列名。")
```

Group images by table type before extraction. Common patterns in 体测数据:
- **个人成绩表** (18列): 序号,姓名,性别,年龄,出生年月,仰卧起坐(绩/名),60米跑(...),屈臂悬垂(...),立定跳远(...),400米跑(...),总分,全能名次,备注
- **按年汇总表** (21列): 出生年, 身高(人数/总/最/最/均), 体重(...), 血压(...), 脉搏(...)
- **体质统计表** (21+列): 年令, 身高(总/均/最/最), 体重(...), 坐高(...), 肺活量(...), 背肌力(...)
- **8列汇总表**: 序号,年份,人数,总分,最高分,最低分,平均分,备注

**If you skip this step and force a single column mapping across all images, the model will silently misalign data** — e.g., putting height values in the "姓名" column because it can't find the right column to put them in.

### Step 2: Extract data with focused prompts

**Critical**: Don't ask for everything. Pick the most important columns and ask specifically:

```python
# GOOD: Focused prompt — specific columns, CSV output
vision_analyze(
    image_url="path/to/table.jpg",
    question="""这是一张手写表格。请只提取以下列的数据，输出为CSV格式（不要解释）：
列1,列2,列3,列4
只输出有数据的行。格式：每行用逗号分隔。"""
)

# BAD: Vague prompt — model produces verbose garbage
vision_analyze(
    image_url="path/to/table.jpg",
    question="请提取表格中所有数据"
)
```

### Step 3: Save and iterate

Save each batch immediately to `output/` directory. If a batch produces poor results, re-process with an even more focused prompt or try individual images.

### Step 4: Handle remaining images

For folders with 5+ images, process in batches of 3:
- Batch 1: images 1-3
- Batch 2: images 4-5 (+ any remaining)

## Prompt Templates

### Five-item sports test (五项比赛报名单)
```
这是哈工大"身体素质五项"比赛报名单。请只提取以下列的数据，输出为CSV格式（不要解释）：
序号,出生年月,仰卧起坐成绩,60米跑成绩,屈臂悬垂成绩,立定跳远成绩,400米跑成绩
只输出有数据的行。
```

### Physical test statistics (体测统计表)
```
这是手写体测统计表格。请提取所有数据为CSV格式。只输出CSV内容（表头+数据行），不要解释。空单元格留空。
```

### Generic table extraction
```
这是一张手写表格的图片。请将表格中所有数据提取为CSV格式。
要求：先识别表头，然后逐行输出数据，用逗号分隔。空单元格留空。只输出CSV内容，不要解释。
```

## Why Programmatic Cropping Fails

Attempted approach: PIL/numpy brightness projection to find white paper region.
Result: Failed on most images because:
1. Uneven lighting creates bright spots that aren't the paper
2. Shadows from fold lines confuse threshold-based detection
3. Dark backgrounds with small bright regions get misidentified
4. Photos taken at angles have gradient brightness

**Conclusion**: Vision models handle uncropped images well — just send the full photo.

## Model Requirements

- Must support multimodal/vision input (image + text)
- Tested: mimo-v2.5 (Xiaomi API), Qwen3.6-35B-A3B (local omlx)
- Quality varies: complex handwritten tables with many columns are harder
- Red ink annotations on blue/black ink can confuse the model

## Output Format

Save as CSV with header comment indicating source:
```csv
# 数据来源: 文件名.jpg
列1,列2,列3
值1,值2,值3
```

## Pitfalls

1. **Verbose model responses**: Vision models often output reasoning text before/after the CSV. Parse carefully or use a stricter prompt ("只输出CSV内容，不要解释").
2. **Column confusion**: When tables have 15+ columns, models mix up adjacent columns. Focus on fewer columns per call.
3. **Red ink**: Annotations in red ink on top of blue/black data confuse the model. Mention this in the prompt if applicable.
4. **Fold marks**: Paper fold lines can be interpreted as table borders. The model usually handles this but may skip rows near folds.
5. **Partial data**: Some rows may have missing values. Use empty strings in CSV rather than guessing.
6. **Varying table structures across folders** (CRITICAL): A project may contain multiple table types (个人成绩表 vs 汇总统计表). If you force all images into one column mapping, the model silently misaligns data — values end up in wrong columns with no error. Symptom: "姓名" column contains height-like numbers (169.0, 167.0). Fix: survey first, group by table type, extract each group with its own column definition.
7. **PYTHONUNBUFFERED**: When running extraction scripts via `terminal(background=true)`, use `python3 -u script.py` or `PYTHONUNBUFFERED=1`. Without it, Python buffers stdout and you see zero output for minutes, making it impossible to monitor progress.
8. **Script folder filter too loose**: If iterating `base_dir.iterdir()`, exclude `__pycache__`, `output*`, `cropped` explicitly — backup dirs created during cleanup will be processed as data folders.
9. **Column shift across merged rows**: When multiple images are merged into one CSV, row N in the CSV doesn't correspond to row N in any single image. To verify a specific row, search the entire CSV for matching values, not by row index.

## Quality Verification Workflow

After extraction, always spot-check 2-3 random rows per folder against original images.

### Method

1. **Pick random rows** from the CSV (use `random.sample` on data lines)
2. **Read the corresponding image** with vision (resize to 2048px first if >2MB):
   ```python
   sips -Z 2048 -s formatOptions 85 input.jpg --out /tmp/check.jpg
   ```
3. **Ask vision to read that specific row**:
   ```
   手写表格，忽略表头。找到序号N那一行，从左到右列出每列值，逗号分隔。
   ```
4. **Search the CSV** for matching values (not by row index — CSV is merged across images):
   ```python
   vision_vals = set("值1,值2,...".split(","))
   for i, line in enumerate(csv_lines[1:], 1):
       csv_vals = set(line.strip().split(","))
       common = vision_vals & csv_vals - {""}
       if len(common) >= threshold:
           print(f"CSV行{i}: {line.strip()}")
   ```

### Interpreting Results

- **All values match** → ✅ correct
- **Partial match (50%+ values)** → ⚠️ column shift — values present but in wrong columns
- **No match** → ❌ data not captured or wrong image
- Column names don't matter — only check if the **data values** from the image appear in the CSV
