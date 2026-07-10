---
name: pdf-doc-update
version: 1.0.0
description: "从PDF习题中提取数据并补全飞书文档。适用于飞书文档已有文字描述但缺表格数据、且原始数据在PDF中的场景。使用终端Python (pymupdf) 提取PDF，用subprocess调用lark-cli覆盖更新。"
---

# PDF习题提取 + 飞书文档更新工作流

## 触发条件
- 飞书文档有题目描述但缺少实际数据表格
- 原始数据在本地PDF文件中
- 需要修复公式错误

## 步骤

### 1. 用终端提取PDF内容
`execute_code` 沙箱**没有** `pymupdf`（fitz），必须用 `terminal`：

```bash
cd /path/to/pdf-dir && python3 << 'PYEOF'
import fitz
import json
import os

results = {}
for pdf in os.listdir('.'):
    if pdf.endswith('.pdf'):
        doc = fitz.open(pdf)
        text = ''.join([page.get_text() for page in doc])
        results[pdf] = text
        doc.close()

with open('/Users/zjrua/tmp/pdf_all_extracted.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print(f"Saved {len(results)} PDFs")
PYEOF
```

### 2. 读取当前文档
```bash
lark-cli docs +fetch --doc "TOKEN" --as bot 2>&1 | python3 -c "
import sys, json
data = json.load(sys.stdin)
md = data['data']['markdown']
# ... process content
"
```

### 3. 构建更新内容
- 对比PDF表格与文档现有内容，确定缺失部分
- 用 `execute_code` 或终端写完整的Markdown文档到 `/tmp/lark-update.md`

**关键规则：**

| 规则 | 说明 |
|------|------|
| 公式标签 | 必须用 `<equation>...</equation>`，禁止 `$...$` 或 `$$...$$` |
| 多字符下标 | `_{MLE}`、`_{p×p}` 等多字符下标会截断！改用 `x_1, x_2` 等数字下标，在正文注释变量含义 |
| 表格 | 用 `<lark-table>` 语法，列宽控制 `column-widths` |
| callout内嵌 | 表格**不能**放在 `<callout>` 内部，会报错 `Callout does not support Table block type` |

### 4. 覆盖更新文档
**不要用 inline markdown 或 `echo`**，LaTeX 会被 shell 转义。用 subprocess：

```python
import subprocess, json

# Write content to temp file
with open('/tmp/lark-update.md', 'w', encoding='utf-8') as f:
    f.write(md_content)

# Call lark-cli via subprocess
cmd = 'lark-cli docs +update --doc "TOKEN" --mode overwrite --markdown "$(cat /tmp/lark-update.md)" --as bot 2>&1'
result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
data = json.loads(result.stdout)
```

### 5. 验证更新
再次 fetch 确认内容正确：
```bash
lark-cli docs +fetch --doc "TOKEN" --as bot 2>&1 | python3 -c "..."
```

## 常见陷阱

1. **沙箱无pymupdf**：`execute_code` 不会报错，但没有fitz。必须在 `terminal` 工具中调用Python。

2. **公式损坏**：LaTeX公式如果编写错误（如 `\tilde{x}{12}` 而非 `\tilde{x}_1`），飞书渲染会截断。修复时用数字下标 + 文字说明变量对应关系。

3. **shell转义**：文档含LaTeX时，`echo` 或 `--markdown "..."` 会被shell转义字符。用 `$(cat file)` 或 `--markdown-file` 间接传入。

4. **callout+table冲突**：飞书 `<callout>` 块不支持内嵌 `<lark-table>`，表格必须放在callout外。

5. **覆盖模式危险**：`--mode overwrite` 会完全替换内容，操作前备份原文。