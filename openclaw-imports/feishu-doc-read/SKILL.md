---
name: feishu-doc-read
description: 读写飞书文档：通过 lark-cli 获取文档内容、提取文本、用 Markdown 覆盖/追加/更新文档。适用于读取、搜索、总结、修复飞书文档。
version: 2.0.0
author: Hermes Agent
---

# 飞书文档读写操作

通过 lark-cli 操作飞书文档（docx）：读取内容、Markdown 写入/更新。

## 前置条件

- lark-cli 已全局安装并配置（`/usr/bin/lark-cli`）
- 飞书 App 有文档的读写权限（`docx:document`）

## 读取文档

### 1. 快速读取（docs +fetch，推荐）

```bash
lark-cli docs +fetch --doc {TOKEN} --api-version v2 --as bot --format pretty
```

输出为 HTML-like 格式，可直接查看文档结构和内容。也可用 `--keyword` 搜索特定内容。

### 2. 获取文档元信息

```bash
lark-cli api GET /open-apis/docx/v1/documents/{document_id} --as bot
```

返回标题、revision_id 等。`document_id` 是 URL 中 `/docx/` 后面的 token。

### 2. 获取文档所有内容块

```bash
lark-cli api GET /open-apis/docx/v1/documents/{document_id}/blocks --as bot --page-all > /tmp/feishu_doc.json
```

**关键参数：**
- `--as bot`：使用应用身份（确保 App 有文档权限）；如果文档未授权给 App，可尝试 `--as user`
- `--page-all`：自动翻页获取所有块（API 默认每页 50 个块，文档通常有数百到数千个块）
- 输出重定向到文件，避免终端截断

### 3. Python 解析文档内容

文档块结构是树形的：根块是 Page（block_type=1），children 是子块 ID 字符串列表。需要构建 block_map 后递归遍历。

```python
import json, re

with open('/tmp/feishu_doc.json') as f:
    data = json.load(f)

items = data.get('data', {}).get('items', [])

# 构建 block_id -> block 的映射
block_map = {item['block_id']: item for item in items}

def extract_text(block):
    """从块中提取纯文本"""
    texts = []
    for key in ['text', 'heading1', 'heading2', 'heading3', 'heading4',
                'heading5', 'heading6', 'heading7', 'heading8', 'heading9',
                'bullet', 'ordered']:
        if key in block:
            for t in block[key].get('elements', []):
                texts.append(t.get('text_run', {}).get('content', ''))
    if 'table_cell' in block:
        for t in block['table_cell'].get('elements', []):
            texts.append(t.get('text_run', {}).get('content', ''))
    return ''.join(texts)

def get_all_text(block_id, depth=0):
    """递归获取块及其所有子块的文本"""
    if depth > 20:
        return []
    block = block_map.get(block_id)
    if not block:
        return []
    results = []
    text = extract_text(block)
    if text:
        results.append(text)
    for child_id in block.get('children', []):
        if isinstance(child_id, str):
            results.extend(get_all_text(child_id, depth + 1))
    return results

root = items[0]  # 第一个 item 是根 Page 块
all_texts = get_all_text(root['block_id'])
```

## 创建文档（v2 API）

### 从零创建飞书文档

```bash
# 创建到云空间根目录（Markdown 格式）
lark-cli docs +create --api-version v2 --doc-format markdown --content @skeleton.md

# 创建到指定文件夹
lark-cli docs +create --api-version v2 --parent-token fldcnXXXX --content @doc.md
```

**返回值示例**：
```json
{
  "ok": true,
  "data": {
    "document": {
      "document_id": "L74CdnRfQoWUFExMLPec7ScXn7c",
      "url": "https://my.feishu.cn/docx/L74CdnRfQoWUFExMLPec7ScXn7c"
    }
  }
}
```

### 推荐的"先骨架后填充"工作流

长文档建议分两步，避免一次性写入超长内容触发字符/参数限制：

**步骤一：创建骨架**（只有标题和段落大纲）
```bash
# 骨架 Markdown 示例：只有 # 标题、## 二级标题、### 三级标题，没有正文
lark-cli docs +create --api-version v2 --doc-format markdown --content @skeleton.md
```

**步骤二：获取 block ID，然后覆盖完整内容**
```bash
# Fetch 获取带 block_id 的结构，确认文档创建成功
lark-cli docs +fetch --api-version v2 --doc {TOKEN} --detail with-ids

# 用完整内容覆盖骨架
lark-cli docs +update --api-version v2 --doc {TOKEN} \
  --command overwrite --doc-format markdown --content @full_content.md
```

也可以使用 `block_insert_after --block-id <标题block_id>` 分段写入各章节（适合多人并行写作场景）。

## 写入/更新文档（v2 API）

### 覆盖整篇文档（Markdown）

```bash
cd /tmp && lark-cli docs +update \
  --doc {TOKEN} --as bot --api-version v2 \
  --command overwrite \
  --doc-format markdown \
  --content @your_file.md \
  --revision-id -1
```

**⚠️ v2 vs v1 关键差异（必读）：**

| 项目 | v1（已弃用） | v2（当前） |
|------|-------------|-----------|
| 必需参数 | `--mode overwrite` | **`--command overwrite`** |
| 内容参数 | `--markdown "..."` | **`--content @file`** |
| 格式参数 | 无 | **`--doc-format markdown`** |
| 错误表现 | 正常工作 | 报 `--command is required` |

### v2 `--command` 操作类型

- `overwrite` — 用 Markdown 全量替换文档内容
- `append` — 在文档末尾追加内容
- `str_replace` — 正则替换（需 `--pattern`）
- `block_delete` — 删除指定块（需 `--block-id`）
- `block_insert_after` — 在指定块后插入（需 `--block-id`）
- `block_replace` — 替换指定块内容
- `block_move_after` — 移动块位置
- `block_copy_insert_after` — 复制并插入块

### v2 写入注意事项

1. **`--content @file` 必须用相对路径**：不能 `/tmp/file.md`，必须先 `cd /tmp` 再用 `@file.md`
2. **`--revision-id -1`** 表示基于最新版本，省略也可（默认就是 -1）
3. **Markdown 中的 `\n` 字面量问题**：如果 Markdown 源文件中包含字面 `\n`（而非真实换行），飞书文档会原样渲染。写入前先做 `content.replace('\\n', '\n')` 清洗
4. **`docs +update --help` 显示的是 v1 flags**，必须加 `--api-version v2` 才能看到正确的 v2 参数

## 坑点

1. **`docs fetch` 子命令可能不工作**：直接用 `lark-cli api GET` 调原始 API 更可靠。`docs fetch` 需要特定的参数格式，尝试多次失败后建议直接走 API。

2. **`--as bot` vs `--as user`**：bot 身份需要 App 被授权访问文档。如果报 `need_user_authorization`，说明文档未对 App 开放，需要用 user 身份或让文档所有者授权。

3. **children 是 ID 字符串，不是对象**：根块和嵌套块的 `children` 字段是 `["doxcn...", "doxcn..."]`，不是完整块对象。必须通过 block_map 解析。

4. **分页很重要**：默认只返回 50 个块。长文档可能有 1000+ 个块，必须用 `--page-all`。

5. **块类型多样**：文本可能藏在 `text`、`heading1-9`、`bullet`、`ordered`、`table_cell` 等不同 key 中，`extract_text` 需要全部覆盖。

6. **表格内容**：表格块的 `property.table_rows` 只有行数信息，实际单元格内容在 `table_cell` 类型的子块中。

7. **`docs +update` v1 flags 在 v2 下报错**：v1 的 `--mode` 和 `--markdown` 在 v2 下不被识别，报 `"--command is required"`。**必须用 `--help --api-version v2` 查看正确的 v2 参数**。

8. **`lark-cli api POST ... batch_update` 返回 404**：直接调飞书 batch_update API 会 404（可能需要特定的 gateway 路由）。推荐用 `docs +update --command` 代替原始 API。

9. **`--page-all` 和 `-o` 互斥**：`lark-cli api GET ... --page-all -o file.json` 报 "mutually exclusive"，应改用 shell 重定向 `> file.json`。

10. **`block_insert_after` 必须用 XML 格式**：即使文档是用 Markdown 创建的，`block_insert_after --content` 的内容必须是 XML 格式的块（`<p>`, `<blockquote>`, `<ul>` 等），不能直接写 Markdown。因为底层存储是 block-based，`block_insert_after` 直接操作 block 层级。示例：`--content '<blockquote><p>📖 <b>标题</b>：<a href="https://...">链接文字</a></p></blockquote>'`

11. **创建带链接的飞书文档后，用 `block_insert_after` 做交叉引用**：如果多个飞书文档互相关联（如主文档引用子文档），在子文档创建完成后，从主文档 fetch with-ids 找到目标 section 的 block_id，用 `block_insert_after` 插入引用段落。这比 `overwrite` 全量替换更优雅，不会覆盖已存在的内容。

## 典型用途

- 读取飞书文档内容并分析、总结
- 用 Markdown 全量更新/修复飞书文档（如修复 `\n` 转义问题）
- 搜索文档中的关键词
- 提取文档结构（标题层级、列表项）
- 追加内容到已有文档

## 参考资料

- `references/lark-cli-docs-update-v2-migration.md` — v2 `docs +update` 迁移笔记（v1→v2 breaking changes、404 排查、@file 路径陷阱）
