---
name: latex-to-feishu-review
description: Convert LaTeX study/review materials (ctexart with tcolorbox definitions/theorems/proofs) into structured Feishu documents with colored callout boxes and rendered equations.
category: productivity
triggers:
  - User has LaTeX review/study notes and wants a Feishu document version
  - Converting LaTeX theorem/proof/definition environments to Feishu format
  - Building exam cheat-sheet documents on Feishu from LaTeX sources
---

# LaTeX to Feishu Review Document

Convert LaTeX course review materials into structured Feishu docx documents.

## Quick Workflow

1. Read the LaTeX source files (gather all .tex files in the directory)
2. Plan the document structure — map LaTeX `\section`/`\subsection` to Feishu `h1`/`h2`
3. Build XML content with `lark-cli docs +create --api-version v2 --as bot`
4. Use `overwrite` for full content replacement (more efficient than block-by-block insertion)

## Color Mapping: tcolorbox → Feishu callout

| LaTeX environment | Feishu callout | emoji |
|---|---|---|
| `defbox` (定义) | `background-color="light-blue" border-color="blue"` | 📘 |
| `thmbox` (定理) | `background-color="light-blue" border-color="blue"` | 🔷 |
| `propbox` (性质) | `background-color="light-green" border-color="green"` | ✅ |
| `corbox` (推论) | `background-color="light-purple" border-color="purple"` | 💜 |
| `proofbox` (证明) | `background-color="light-gray" border-color="gray"` | 📝 |
| `exbox` (例题) | `background-color="light-yellow" border-color="yellow"` | 📝 |

## Equation Rendering

All formulas go inside `<latex>...</latex>` tags (NOT `<equation>` — that's for Feishu UI editor, not the API). The LaTeX math syntax is preserved verbatim.

```xml
<p><latex>\varphi(t) = \mathbb{E}(e^{itX})</latex></p>
```

### Known Incompatible LaTeX Commands

Feishu's KaTeX renderer does NOT support all LaTeX commands. When formulas fail to render, suspect these:

| ❌ Command | ✅ Replacement | Notes |
|---|---|---|
| `\operatorname{l.i.m}` | `\mathrm{l.i.m}` | `\operatorname` not recognized |
| `\underset{...}{\mathrm{l.i.m}}` | `\mathop{\mathrm{l.i.m}}\limits_{...}` | `\underset` with custom op unreliable |

General rules:
- `\mathrm`, `\mathbb`, `\text`, `\mathcal` → supported
- `\frac`, `\int`, `\sum`, `\prod`, `\lim` → supported
- `\left`, `\right`, `\langle`, `\rangle` → supported
- `\underset`, `\overset` → supported for standard operators (e.g. `\underset{n\to\infty}{\lim}`), unreliable for custom operators
- `\operatorname{...}` → **NOT supported**, use `\mathrm{...}` instead

### Issue Diagnosis Workflow

### User feedback via comments

When the user reports rendering problems, fetch their doc comments to find exactly which blocks are broken:

```bash
lark-cli drive file.comments list --as bot --params '{"file_type":"docx","file_token":"DOC_TOKEN"}'
```

The `quote` field in each comment shows the exact text the user highlighted. Parse it to identify the problematic pattern (Unicode symbol, `<sup>` tag, formula syntax, etc.).

### Formula Diagnostics Workflow

When formulas don't render in the Feishu doc, DON'T guess — test systematically:

1. Create a small test doc with ~10 isolated formulas covering different LaTeX constructs
2. Have the user visually check which render and which don't
3. Identify the incompatible commands and replace them

Test template:
```xml
<title>公式兼容性测试</title>
<h2>测试1: 基础</h2>
<p><latex>\varphi(t) = \mathbb{E}(e^{itX})</latex></p>
<h2>测试2: 分数</h2>
<p><latex>f(x) = \frac{1}{(2\pi)^{n/2}|B|^{1/2}}</latex></p>
<h2>测试3: 极限</h2>
<p><latex>\lim_{n\to\infty} X_n = X</latex></p>
<h2>测试4: mathrm</h2>
<p><latex>\mathrm{l.i.m}_{n\to\infty} X_n = X</latex></p>
<h2>测试5: mathop+limits</h2>
<p><latex>\mathop{\mathrm{l.i.m}}\limits_{n\to\infty} X_n = X</latex></p>
<h2>测试6: langle/rangle</h2>
<p><latex>\langle X(t)\rangle = \frac{1}{2T}\int_{-T}^T X(t)\mathrm{d}t</latex></p>
<h2>测试7: 积分</h2>
<p><latex>\int_0^{2T} R_X(\tau)\mathrm{d}\tau</latex></p>
<h2>测试8: 花括号</h2>
<p><latex>\exp\left\{-\frac{1}{2}(x-a)B^{-1}(x-a)^T\right\}</latex></p>
<h2>测试9: 偏导</h2>
<p><latex>\frac{\partial V}{\partial t} + \frac{g^2}{2}\frac{\partial^2 V}{\partial x^2}</latex></p>
<h2>测试10: 求和</h2>
<p><latex>\sum_{k\in S} p_{ik}^{(n)} p_{kj}^{(m)}</latex></p>
```

## PITFALLS

### #1: ALL math notation MUST be inside `<latex>` tags

**This is the cardinal rule.** HTML named entities AND Unicode math symbols BOTH fail to render in Feishu outside `<latex>` tags. The only reliable approach is `<latex>` for every piece of mathematical notation — even single symbols.

| ❌ Approach | Problem |
|---|---|
| `&sigma;` (HTML entity) | Shows literal `&sigma;` text |
| `σ` (Unicode U+03C3) | Missing glyph in Feishu font, shows tofu □ or wrong spacing |
| `ℱ` (Unicode U+2131) | Letterlike Symbols block — not in Feishu's font stack |
| `𝔼` (Unicode U+1D53C) | Mathematical Alphanumeric Symbols — definitely missing |
| `<latex>\sigma</latex>` | ✅ The only reliable way |

**When converting LaTeX to Feishu, replace ALL math Unicode with `<latex>` equivalents:**

| Source symbol | Feishu XML |
|---|---|
| `σ` | `<latex>\\sigma</latex>` |
| `Ω` / `ω` | `<latex>\\Omega</latex>` / `<latex>\\omega</latex>` |
| `τ` / `φ` / `λ` / `μ` / `π` / `δ` | `<latex>\\tau</latex>` / `<latex>\\varphi</latex>` etc. |
| `ℱ` (script F) | `<latex>\\mathcal{F}</latex>` |
| `𝔼` (double-struck E) | `<latex>\\mathbb{E}</latex>` |
| `∈` / `∉` | `<latex>\\in</latex>` / `<latex>\\notin</latex>` |
| `∪` / `∩` / `∅` | `<latex>\\cup</latex>` / `<latex>\\cap</latex>` / `<latex>\\emptyset</latex>` |
| `∑` / `∏` | `<latex>\\sum</latex>` / `<latex>\\prod</latex>` |
| `≥` / `≤` / `≠` | `<latex>\\ge</latex>` / `<latex>\\le</latex>` / `<latex>\\neq</latex>` |
| `∞` / `→` / `⇔` / `∀` | `<latex>\\infty</latex>` / `<latex>\\to</latex>` / `<latex>\\Leftrightarrow</latex>` / `<latex>\\forall</latex>` |
| `⟨` / `⟩` / `∼` / `′` | `<latex>\\langle</latex>` / `<latex>\\rangle</latex>` / `<latex>\\sim</latex>` / `<latex>\\prime</latex>` |

**Replacement technique**: use placeholder-protection to avoid nesting `<latex>` inside existing `<latex>` blocks:
```python
# 1. Extract existing <latex> blocks, replace with placeholders
latex_blocks = re.findall(r'<latex>.*?</latex>', content, re.DOTALL)
for i, block in enumerate(latex_blocks):
    content = content.replace(block, f'__LATEX_{i}__', 1)
# 2. Replace Unicode symbols with <latex> equivalents
for old, new in replacements:
    content = content.replace(old, new)
# 3. Restore original <latex> blocks
for i, block in enumerate(latex_blocks):
    content = content.replace(f'__LATEX_{i}__', block, 1)
```

### #2: `<sup>` and `<sub>` HTML tags are NOT supported

Feishu DocxXML does NOT recognize `<sup>` or `<sub>` as formatting tags. They display as literal angle-bracket text (`<sup>T</sup>` visible to the reader). Replace them:

| ❌ HTML | ✅ Feishu |
|---|---|
| `X<sup>2</sup>` | `X<latex>^{2}</latex>` |
| `p<sub>k</sub>` | `p<latex>_{k}</latex>` |
| `A<sup>T</sup>` | `A<latex>^{T}</latex>` |

For complex expressions like `∑<sub>i=1</sub><sup>∞</sup>`, put the entire thing in one `<latex>` tag: `<latex>\\sum_{i=1}^{\\infty}</latex>`.

> **Warning**: after replacing `<sub>` and `<sup>` with `<latex>` fragments, watch for residue like `<sup><latex>\\infty</latex></sup>` where the old `<sup>` wrapped a `<latex>`. Fix these manually.

### #3: Merge fragmented `<latex>` blocks into complete expressions

After replacing Unicode symbols and `<sup>`/`<sub>` with `<latex>` equivalents, the document will have many fragmented blocks like `A<latex>^{c}</latex> <latex>\in</latex> <latex>\mathcal{F}</latex>`. These cause visual gaps and should be merged into complete expressions: `<latex>A^{c} \in \mathcal{F}</latex>`.

**Merge workflow:**

```python
import re
# Pass 1: merge adjacent <latex> blocks repeatedly
for _ in range(5):
    prev = content
    content = re.sub(r'</latex>\s*<latex>', ' ', content)
    if content == prev:
        break

# Pass 2: absorb leading math characters into <latex>
# A<latex>^{c}</latex> → <latex>A^{c}</latex>
content = re.sub(
    r'([A-Za-z0-9])<latex>(\^|_|\\[a-zA-Z]+)',
    r'<latex>\1\2',
    content
)

# Pass 3: absorb parenthesized patterns
# P(<latex>\Omega</latex>) → <latex>P(\Omega)</latex>
content = re.sub(r'P\(<latex>([^<]+)</latex>\)', r'<latex>P(\1)</latex>', content)
# = <latex>X</latex> → <latex>= X</latex>
content = re.sub(r'= <latex>([^<]+)</latex>', r'<latex>= \1</latex>', content)

# Verify: should be 0
assert not re.search(r'</latex>\s*<latex>', content)
```

### #4: Complete expressions — wrap surrounding context too

Don't just wrap the operator symbols. When a mathematical statement spans surrounding text, wrap everything in one `<latex>`:

| ❌ Fragmented | ✅ Complete |
|---|---|
| `dX(t) = f(t,X(t))dt + g(t,X(t))dB(t)，V(t,x)` (not in latex) | `<latex>dX(t) = f(t,X(t))dt + g(t,X(t))dB(t)</latex>，<latex>V(t,x)</latex>` |
| `{B(t), t ≥ 0}` (not in latex) | `<latex>\{B(t), t \ge 0\}</latex>` |
| `{g(t)}` (not in latex) | `<latex>\{g(t)\}</latex>` |
| `(dB)^2 = dt` (fragmented) | `<latex>(dB)^2 = dt</latex>` |
| `D⟨X(t)⟩ = 0` (fragmented) | `<latex>D\langle X(t)\rangle = 0</latex>` |
| `映射 P: ℱ → [0,1]` (fragmented) | `映射 <latex>P: \mathcal{F} \to [0,1]</latex>` |

Pattern: variables in Chinese prose (如 `正整数 m,n 和状态 i,j`, `随机变量 X`) should be wrapped: `正整数 <latex>m,n</latex> 和状态 <latex>i,j</latex>`.

### #5: `\operatorname` → `\mathrm` for compatibility

Feishu's KaTeX renderer has issues with `\operatorname`:

| ❌ | ✅ |
|---|---|
| `\operatorname{l.i.m}` | `\mathrm{l.i.m}` |
| `\underset{...}{\operatorname{l.i.m}}` | `\mathop{\mathrm{l.i.m}}\limits_{...}` |

### #6: `<equation>` is NOT an API tag — use `<latex>`

The Feishu DocxXML API uses `<latex>`. `<equation>` is a UI-editor concept not recognized by `lark-cli docs`. Using `<equation>` will strip/mangle formula content, making rendering worse than `<latex>`. Always use `<latex>` even if user memory references `<equation>`.

### lark-cli requires relative paths for @file

When using `--content @filename`, the path MUST be relative to the current directory:

```bash
# ✅ Correct
cd /tmp && lark-cli docs +update ... --content @stochastic-review-full.xml

# ❌ Wrong — absolute path rejected
lark-cli docs +update ... --content @/tmp/stochastic-review-full.xml
```

Error message: `--file must be a relative path within the current directory`

### Use --as bot to avoid auth login

Creating docs with `--as bot` works without `auth login`. The document is auto-granted `full_access` to the CLI user.

### Use overwrite for full content replacement

When replacing the entire document content, `--command overwrite` is more efficient than multiple `block_insert_after` calls.

### <latex> is the API tag, NOT <equation>

The Feishu DocxXML API uses `<latex>...</latex>` for formulas. The `<equation>` tag exists in the Feishu UI editor but is NOT recognized by the `lark-cli docs` API. Using `<equation>` will cause the API to strip or mangle the formula content, resulting in far worse rendering. Always use `<latex>` regardless of user memory referencing `<equation>`.
