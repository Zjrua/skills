---
name: ocr-and-documents
description: "Extract text from PDFs/scans (pymupdf, marker-pdf) and translate PDFs with layout preserved (pdf2zh)."
version: 2.4.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [PDF, Documents, Research, Arxiv, Text-Extraction, OCR]
    related_skills: [powerpoint]
---

# PDF & Document Extraction

For DOCX: use `python-docx` (parses actual document structure, far better than OCR).
For PPTX: see the `powerpoint` skill (uses `python-pptx` with full slide/notes support).
This skill covers **PDFs and scanned documents**.

## Step 1: Remote URL Available?

If the document has a URL, **always try `web_extract` first**:

```
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])
web_extract(urls=["https://example.com/report.pdf"])
```

This handles PDF-to-markdown conversion via Firecrawl with no local dependencies.

Only use local extraction when: the file is local, web_extract fails, or you need batch processing.

## Step 2: Choose Local Extractor

| Feature | pymupdf (~25MB) | marker-pdf (~3-5GB) |
|---------|-----------------|---------------------|
| **Text-based PDF** | ✅ | ✅ |
| **Scanned PDF (OCR)** | ❌ | ✅ (90+ languages) |
| **Tables** | ✅ (basic) | ✅ (high accuracy) |
| **Equations / LaTeX** | ❌ | ✅ |
| **Code blocks** | ❌ | ✅ |
| **Forms** | ❌ | ✅ |
| **Headers/footers removal** | ❌ | ✅ |
| **Reading order detection** | ❌ | ✅ |
| **Images extraction** | ✅ (embedded) | ✅ (with context) |
| **Images → text (OCR)** | ❌ | ✅ |
| **EPUB** | ✅ | ✅ |
| **Markdown output** | ✅ (via pymupdf4llm) | ✅ (native, higher quality) |
| **Install size** | ~25MB | ~3-5GB (PyTorch + models) |
| **Speed** | Instant | ~1-14s/page (CPU), ~0.2s/page (GPU) |

**Decision**: Use pymupdf unless you need OCR, equations, forms, or complex layout analysis.

If the user needs marker capabilities but the system lacks ~5GB free disk:
> "This document needs OCR/advanced extraction (marker-pdf), which requires ~5GB for PyTorch and models. Your system has [X]GB free. Options: free up space, provide a URL so I can use web_extract, or I can try pymupdf which works for text-based PDFs but not scanned documents or equations."

---

## pymupdf (lightweight)

```bash
pip install pymupdf pymupdf4llm
```

**Via helper script**:
```bash
python scripts/extract_pymupdf.py document.pdf              # Plain text
python scripts/extract_pymupdf.py document.pdf --markdown    # Markdown
python scripts/extract_pymupdf.py document.pdf --tables      # Tables
python scripts/extract_pymupdf.py document.pdf --images out/ # Extract images
python scripts/extract_pymupdf.py document.pdf --metadata    # Title, author, pages
python scripts/extract_pymupdf.py document.pdf --pages 0-4   # Specific pages
```

**Inline**:
```bash
python3 -c "
import pymupdf
doc = pymupdf.open('document.pdf')
for page in doc:
    print(page.get_text())
"
```

---

## marker-pdf (high-quality OCR)

```bash
# Check disk space first
python scripts/extract_marker.py --check

pip install marker-pdf
```

**Via helper script**:
```bash
python scripts/extract_marker.py document.pdf                # Markdown
python scripts/extract_marker.py document.pdf --json         # JSON with metadata
python scripts/extract_marker.py document.pdf --output_dir out/  # Save images
python scripts/extract_marker.py scanned.pdf                 # Scanned PDF (OCR)
python scripts/extract_marker.py document.pdf --use_llm      # LLM-boosted accuracy
```

**CLI** (installed with marker-pdf):
```bash
marker_single document.pdf --output_dir ./output
marker /path/to/folder --workers 4    # Batch
```

---

## Arxiv Papers

```
# Abstract only (fast)
web_extract(urls=["https://arxiv.org/abs/2402.03300"])

# Full paper
web_extract(urls=["https://arxiv.org/pdf/2402.03300"])

# Search
web_search(query="arxiv GRPO reinforcement learning 2026")
```

## Split, Merge & Search

pymupdf handles these natively — use `execute_code` or inline Python:

```python
# Split: extract pages 1-5 to a new PDF
import pymupdf
doc = pymupdf.open("report.pdf")
new = pymupdf.open()
for i in range(5):
    new.insert_pdf(doc, from_page=i, to_page=i)
new.save("pages_1-5.pdf")
```

```python
# Merge multiple PDFs
import pymupdf
result = pymupdf.open()
for path in ["a.pdf", "b.pdf", "c.pdf"]:
    result.insert_pdf(pymupdf.open(path))
result.save("merged.pdf")
```

```python
# Search for text across all pages
import pymupdf
doc = pymupdf.open("report.pdf")
for i, page in enumerate(doc):
    results = page.search_for("revenue")
    if results:
        print(f"Page {i+1}: {len(results)} match(es)")
        print(page.get_text("text"))
```

No extra dependencies needed — pymupdf covers split, merge, search, and text extraction in one package.

---

---

## PDF Translation (format-preserving)

When the user wants to **translate** a PDF while preserving its original layout, tables, math formulas, and images:

### pdf2zh (PDFMathTranslate) — best open-source option

- **GitHub**: https://github.com/Byaidu/PDFMathTranslate
- Preserves math formulas (LaTeX), tables, images, reading order
- Bilingual side-by-side output
- Multiple translation backends: Google, DeepL, OpenAI, Ollama, etc.
- CLI and GUI modes

```bash
# Install (HEAVY — depends on PyTorch ~2-3GB)
uv venv /root/.venvs/pdf2zh --python 3.12
/root/.venvs/pdf2zh/bin/pip install pdf2zh

# CLI usage
/root/.venvs/pdf2zh/bin/pdf2zh document.pdf                        # Google Translate (default)
/root/.venvs/pdf2zh/bin/pdf2zh document.pdf -li en -lo zh           # English → Chinese
/root/.venvs/pdf2zh/bin/pdf2zh document.pdf -s deepl                # Use DeepL
/root/.venvs/pdf2zh/bin/pdf2zh document.pdf -s openai               # Use OpenAI API
/root/.venvs/pdf2zh/bin/pdf2zh document.pdf -o output_dir           # Custom output dir
/root/.venvs/pdf2zh/bin/pdf2zh document.pdf --pages 1-5             # Translate specific pages
/root/.venvs/pdf2zh/bin/pdf2zh document.pdf -ot bilingual            # Bilingual output (default)
/root/.venvs/pdf2zh/bin/pdf2zh document.pdf -ot translated           # Translation only

# GUI mode
/root/.venvs/pdf2zh/bin/pdf2zh --gui                                # Starts web UI on port 7860
```

### Pitfalls

- **Install is very heavy**: pdf2zh pulls PyTorch + many ML deps. On low-memory servers (≤4GB RAM, no swap), `pip install` may take 10+ minutes or timeout. Use a **dedicated venv** (`/root/.venvs/pdf2zh/`) to avoid polluting system Python.
- **Externally-managed Python**: On Debian/Ubuntu with PEP 668, system pip refuses to install. Always use a venv or `uv venv`.
- **Server disk space**: Full install ~3-5GB. Check `df -h` before installing.
- **Translation API keys needed for non-Google**: DeepL, OpenAI, etc. need their respective API keys set as env vars. Google Translate works out of the box (free).
- **First run downloads models**: Even after pip install, the first run may download additional models for layout analysis.

### When to use pdf2zh vs extract-then-translate

- **pdf2zh**: User wants a translated PDF that looks like the original (same layout, fonts, images). Best for academic papers, reports.
- **Extract-then-translate**: User just wants the text content in another language. Extract with pymupdf/marker → translate text → present as markdown. Faster, no heavy deps.

---

## Image OCR Fallback (when vision_analyze fails)

When `vision_analyze` fails with "Connection error" or other issues, use **tesseract OCR** as a fallback for extracting text from images (screenshots, benchmark tables, charts, etc.):

```bash
# Install tesseract (one-time)
apt-get install -y tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-eng

# Install Python bindings
pip install pytesseract Pillow
```

**Workflow for large/tall images** (e.g. 1280×3195 benchmark tables):

```python
from PIL import Image
import pytesseract

img = Image.open('screenshot.jpg')
# 1. Crop into manageable sections (tesseract times out on huge images)
top = img.crop((0, 0, img.width, img.height // 2))
# 2. Optionally resize for speed
top_resized = top.resize((640, top.height // 2))
# 3. OCR with appropriate language
text = pytesseract.image_to_string(top_resized, lang='chi_sim+eng', config='--psm 6')
print(text)
```

**Pitfalls**:
- Tesseract **times out (>30s)** on full-resolution tall images (>2000px). Always crop/resize first.
- `--psm 6` (uniform block of text) works best for tables; default `--psm 3` may misparse columns.
- Chinese+English mixed: use `lang='chi_sim+eng'`. English-only: `lang='eng'` is faster.
- OCR quality on styled/colored tables is imperfect — expect ~80% accuracy on numbers. Cross-reference with known benchmarks if possible.
- `vision_analyze` "Connection error" typically means the vision provider is down, not a file path issue. Don't retry endlessly (3+ failures = stop and switch to OCR).

## Notes

- `web_extract` is always first choice for URLs
- pymupdf is the safe default — instant, no models, works everywhere
- marker-pdf is for OCR, scanned docs, equations, complex layouts — install only when needed
- Both helper scripts accept `--help` for full usage
- marker-pdf downloads ~2.5GB of models to `~/.cache/huggingface/` on first use
- For Word docs: `pip install python-docx` (better than OCR — parses actual structure)
- For PowerPoint: see the `powerpoint` skill (uses python-pptx)
- For **translating** PDFs with layout preserved: see "PDF Translation" section above (pdf2zh)
