---
name: feishu-doc-formula-pitfalls
description: Rules for writing math formulas in Feishu documents via lark-cli to avoid rendering failures.
---

# Feishu Document Formula Pitfalls (lark-cli)

When writing math formulas in Feishu documents via `lark-cli docs +update --markdown`, several LaTeX constructs that work fine in normal renderers will **break the `<equation>` tag parser**.

## Core Rule: Always Use `<equation>` Tags

**lark-cli does NOT recognize `$...$` inline math.** All math must be wrapped in `<equation>...</equation>` tags, including inline expressions.

```markdown
❌  定义 $r = \max(p, P)$，$s = \max(q, Q)$
✅  定义 <equation>r = \max(p, P)</equation>，<equation>s = \max(q, Q)</equation>
```

## Forbidden Patterns Inside `<equation>`

These LaTeX constructs break the parser because `}_{`, `]_{`, `^{\`, or similar brace sequences are misinterpreted as closing the `<equation>` tag:

### 1. `\underbrace{...}_{text}`

```markdown
❌  <equation>Z_{t-1} = \underbrace{(X_{t-1}, \ldots)}_{r \text{ 个}}</equation>
✅  <equation>Z_{t-1} = (X_{t-1}, \ldots, X_{t-r})</equation>（前 r 个分量）
```

**Fix**: Use the expression without `\underbrace`, then explain the grouping in plain Chinese text.

### 2. Matrix element subscripts `[A]_{i,j}`

```markdown
❌  <equation>[A]_{1,j} = b_j + \sum_{k=1}^{Q} c_{jk}</equation>
✅  <equation>\alpha_j = b_j + \sum_{k=1}^{Q} c_{jk}</equation>
```

**Fix**: Name the elements with Greek letters (α_j, β_k) and define them separately. Do NOT use bracket-then-subscript notation.

### 3. Nested `_{...}` inside `\underbrace`

Same root cause as #1. The `}_{` between the brace content and the subscript is parsed as closing the tag.

### 4. `\overbrace{...}^{text}`

Same issue as `\underbrace` but with `}^{`.

### 5. Multiple `_{` in sequence

```markdown
❌  <equation>c_{jk}X_{t-j}\varepsilon_{t-k}</equation>  — usually fine
✅  But avoid patterns like }_{  at boundaries
```

Single `_{` inside an equation is usually OK. The problem specifically occurs when `}_{` or `]_{` appears (closing brace/bracket immediately followed by underscore-brace).

## Safe Patterns

These work reliably inside `<equation>`:

- Single subscripts/superscripts: `X_t`, `A^\top`, `\varepsilon_{t-1}`
- `\begin{pmatrix} ... \end{pmatrix}` with `\\` line breaks
- `\sum`, `\prod`, `\int` with limits
- `\frac{a}{b}`
- `\boxed{...}`
- `\left( ... \right)`, `\left[ ... \right]`
- `\begin{pmatrix} a & b \\ c & d \end{pmatrix}`
- `\\ldots`, `\\cdots`, `\\vdots`, `\\ddots`
- `\\text{...}` for text inside math
- `\\iint`, `\\iiint` (double/triple integrals)
- `\\sup`, `\\inf` operators

## lark-cli File Path Requirement

`--markdown @file` requires the file to be a **relative path from the CWD** (`/root/.hermes/hermes-agent/`). Absolute paths or `/tmp/` paths are rejected.

```bash
❌  --markdown @/tmp/content.md
❌  --markdown @~/content.md
✅  cp /tmp/content.md ./content.md && --markdown @content.md
```

## Verification After Update

Always fetch the document after updating to check for parse errors:

```bash
lark-cli docs +fetch --doc TOKEN --offset <prev_total_length>
```

Look for patterns like `*{...` or truncated equation text in the fetched markdown — these indicate broken `<equation>` tags.

## Reading Document Comments

To read user comments on a document (e.g., review feedback):

```bash
# Method 1: lark-cli command
lark-cli drive file.comments list --params '{"file_type":"docx"}'

# Method 2: direct API
lark-cli api GET "/open-apis/drive/v1/files/TOKEN/comments?page_size=50" --params '{"file_type":"docx"}'
```

**Note**: The docx-specific comment endpoint (`/open-apis/docx/v1/documents/.../comments`) returns 404. Use the Drive comment API instead.

## `delete_range` Mode

`--selection-by-title` requires the **exact full title text**, including all content after `##`:

```bash
❌  --selection-by-title "## 附录"
✅  --selection-by-title "## 附录：双线性模型 → 状态空间形式的完整推导"
```

Use `+fetch` first to see the actual title text if unsure.

## Batch Edit Workflow (Multiple Targeted Changes)

When making 5+ targeted edits across a document, the `replace_all` / `replace_range` modes are fragile (ellipsis matching is picky). It's often more reliable to:

1. **Fetch the full document**:
   ```bash
   lark-cli docs +fetch --doc TOKEN 2>&1 | python3 -c "
   import sys, json
   md = json.load(sys.stdin)['data']['markdown']
   with open('orig.md', 'w') as f: f.write(md)
   "
   ```

2. **Modify in Python** — load `orig.md`, make all edits with `str.replace()`, save to `new.md`

3. **Overwrite**:
   ```bash
   lark-cli docs +update --doc TOKEN --mode overwrite --markdown @new.md
   ```

This avoids ellipsis-matching failures and gives you full control. Downside: the entire document is replaced, so formatting precision depends on the fetch round-trip being faithful.

## Typical Fix Workflow (Single/Broken Equation)

If formulas break after an update:

1. Fetch the broken section with `+fetch --offset`
2. Identify which `<equation>` blocks are malformed
3. Rewrite without forbidden patterns (`\\underbrace`, `[A]_{i,j}`, etc.)
4. Delete the broken section with `--mode delete_range --selection-by-title`
5. Append the corrected version with `--mode append`
