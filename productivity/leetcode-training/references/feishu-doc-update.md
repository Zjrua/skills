# Feishu 题解文档更新流程

## 文档信息
- **Doc Token**: `EZfodeviXosNJLxuZWFcKCwonyg`
- **URL**: https://my.feishu.cn/docx/EZfodeviXosNJLxuZWFcKCwonyg
- **格式**: Markdown (Lark-flavored)

## 更新方式：gen_doc.py（推荐）

自动生成完整题解文档并上传，从 `problems/` + `code/` + `PROGRESS.md` 读取数据：
```bash
cd /root/projects/leetcode-hot100 && python3 scripts/gen_doc.py
```

脚本会：
1. 读取 PROGRESS.md 判断哪些题已完成
2. 遍历 PROBLEMS.txt 中所有题目
3. 从 `problems/` 读取题面，从 `code/` 读取已完成题的代码
4. 生成完整 markdown → 写入 `/tmp/lc100_doc.md`
5. 用 `lark-cli docs +update --mode overwrite` 上传到飞书

**⚠️ gen_doc.py 的 `get_completed()` 正则必须匹配题号列（第2列），不是序号列（第1列）** — 见主 SKILL.md pitfall。

## 手动更新方式

### 全量覆盖（推荐用于批量更新）
```bash
cd /tmp
lark-cli docs +update --doc EZfodeviXosNJLxuZWFcKCwonyg --mode overwrite --markdown @./lc100_doc_final.md --as bot
```

### 追加新题
```bash
lark-cli docs +update --doc EZfodeviXosNJLxuZWFcKCwonyg --mode append --markdown @./new_problem.md --as bot
```

## ⚠️ 文件路径必须是相对路径
`@./file.md` 而不是 `@/tmp/file.md`。先 `cd /tmp` 再用相对路径。

## ⚠️ 更新前必须清理 HTML 标签
LeetCode 题面文件含 HTML 标签（`<strong>`, `<span>`, `<meta>`），飞书不支持。
生成文档后必须运行清理脚本（见主 SKILL.md 的 HTML cleanup pitfall）。

## 文档格式要求

每道题的格式：
```markdown
## {题号}. {题名} ({难度}) {✅/⏳}

🔗 [原题链接](https://leetcode.cn/problems/{slug}/) ｜ 📊 进度记录  ← 仅已完成

{完整题目描述}

{所有示例（输入/输出/解释）}

{数据范围约束}

**思路**：{一句话概括}                            ← 仅已完成
**复杂度**：时间 O(x)，空间 O(y)                  ← 仅已完成

```python                                           ← 仅已完成
class Solution:
    def method(self, ...):
        ...
```
```

## 生成脚本模板

```python
import os, re, glob

problems_dir = "/root/projects/leetcode-hot100/problems"
code_dir = "/root/projects/leetcode-hot100/code"

# Build maps
prob_map = {}
for f in sorted(glob.glob(os.path.join(problems_dir, "*.md"))):
    m = re.match(r"(\d+)_", os.path.basename(f))
    if m: prob_map[int(m.group(1))] = f

code_map = {}
for f in sorted(glob.glob(os.path.join(code_dir, "*.py"))):
    m = re.match(r"(\d+)_", os.path.basename(f))
    if m: code_map[int(m.group(1))] = f

def read_problem_body(filepath):
    with open(filepath) as f:
        content = f.read()
    m = re.search(r"## 题目描述\s*\n(.+)", content, re.DOTALL)
    return m.group(1).strip() if m else "\n".join(content.split("\n")[1:]).strip()

def read_code(filepath):
    with open(filepath) as f:
        content = f.read()
    m = re.search(r"(class Solution:.+?)(?=\n# ---- Tests|\ndef test|\nif __name__)", content, re.DOTALL)
    return m.group(1).strip() if m else content.split("# ---- Tests")[0].strip()

# Generate doc markdown, clean HTML, write to /tmp, then:
# cd /tmp && lark-cli docs +update --doc EZfodeviXosNJLxuZWFcKCwonyg --mode overwrite --markdown @./output.md --as bot
```
