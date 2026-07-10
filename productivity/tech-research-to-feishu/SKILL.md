---
name: tech-research-to-feishu
description: "Use when the user wants to systematically learn a new technology/framework/topic: research official sources, structure knowledge into a comprehensive Feishu document with cross-linking. Covers the full pipeline from authoritative information gathering → knowledge structuring → Feishu doc creation → cross-referencing."
version: 1.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [research, feishu, learning, documentation, lark-cli]
    related_skills: []
---

# 技术调研 → 飞书文档（快速学习）

## Overview

当用户想系统学习一个新技术/框架/主题时，按本 Skill 的工作流执行：
**多源调研 → 知识结构化 → 飞书文档创建 → 交叉引用**

核心原则：**官方优先、结构统一、可交叉引用**。

## When to Use

**适用**：
- 用户说"帮我了解一下 XXX"、"收集 XXX 的资料整理成文档"
- 用户想系统学习一个技术主题（LangChain、RAG、Docker 等）
- 需要将调研结果沉淀为飞书文档供后续学习参考
- 多份技术文档需要互相链接形成知识网络

**不适用**：
- 用户只想要一个简单解释（直接回答即可）
- 纯代码任务（用 code/terminal 相关 Skill）
- 纔研/论文深度阅读（用 arxiv 等研究类 Skill）

---

## 工作流总览

```
Phase 1: 多源调研（并行）     Phase 2: 结构化           Phase 3: 文档化
┌────────────────────┐    ┌──────────────────┐    ┌────────────────────┐
│ 官方文档 (curl)     │    │ 确定 7-9 个板块   │    │ write_file → .md   │
│ GitHub README      │ →  │ 每板块 3-5 要点   │ →  │ lark-cli +create   │
│ PyPI/NPM 元数据    │    │ 对比表格 + 代码   │    │ lark-cli +fetch 验证│
│ delegate_task 并行 │    │ 面试/实践角度     │    │ 交叉引用已有文档    │
└────────────────────┘    └──────────────────┘    └────────────────────┘
```

---

## Phase 1: 多源调研

### 1.1 信息源优先级

| 优先级 | 来源 | 获取方式 | 可靠度 |
|--------|------|---------|--------|
| ⭐⭐⭐⭐⭐ | 官方文档站 | `curl -sL <url>` + python3 提取 | 最高 |
| ⭐⭐⭐⭐⭐ | GitHub README/Docs | `curl -sL raw.githubusercontent.com/...` | 最高 |
| ⭐⭐⭐⭐ | PyPI/NPM 包元数据 | `curl -sL pypi.org/pypi/<pkg>/json` | 高 |
| ⭐⭐⭐ | 技术社区文章 | `delegate_task` + web search | 中（需交叉验证） |
| ⭐⭐ | 面经/博客 | `delegate_task` + web search | 中低 |

### 1.2 官方文档抓取技巧

大部分技术文档是 SPA（客户端渲染），直接 `curl` 可能只拿到空壳 HTML。

**策略链**（依次尝试）：

```bash
# Step 1: 直接 curl 抓取
curl -sL "https://docs.example.com/intro" \
  -H "User-Agent: Mozilla/5.0" -o /tmp/page.html

# Step 2: 提取 article/main 标签内容
python3 << 'PYEOF'
import re
with open('/tmp/page.html') as f:
    html = f.read()
# 尝试多种内容选择器
for pat in [r'<article[^>]*>(.*?)</article>',
            r'<main[^>]*>(.*?)</main>',
            r'<div class="markdown"[^>]*>(.*?)</div>']:
    m = re.search(pat, html, re.S)
    if m:
        text = re.sub(r'<script[^>]*>.*?</script>', '', m.group(1), flags=re.S)
        text = re.sub(r'<[^>]+>', ' ', text)
        print(re.sub(r'\s+', ' ', text).strip()[:3000])
        break
PYEOF

# Step 3: 如果 SPA 空壳，从 meta 标签提取
# <meta name="description" content="...">
# <meta property="og:description" content="...">

# Step 4: 尝试 raw.githubusercontent.com 获取 markdown 源文件
curl -sL "https://raw.githubusercontent.com/<org>/<repo>/main/README.md"

# Step 5: PyPI 元数据（版本、依赖、描述）
curl -sL "https://pypi.org/pypi/<package>/json" | python3 -m json.tool
```

**关键要点**：
- 即使只能拿到 meta description（200-300 字），也比没有强——官方的 meta description 通常是对该技术的精准定义
- 多页抓取：intro/overview 页面拿定义，concepts 页面拿核心概念，tutorials 页面拿代码示例
- 如果文档站点有 API（如 `/api/docs.json`），优先用 API
- **LangChain 系文档站（Mintlify/Docusaurus SSR）例外**：`<article>` 标签内通常包含完整渲染内容，curl 能直接提取数千字的正文和代码示例。其他纯 SPA 站点（如部分 RAGAS 页面）只能拿到 meta description。

### 1.3 并行调研（delegate_task）

对较大的主题，用 `delegate_task` 并行调研不同角度：

```
delegate_task(tasks=[
  {
    "goal": "搜索收集 XXX 的岗位需求和面试考点",
    "toolsets": ["web"]
  },
  {
    "goal": "搜索收集 XXX 的核心技术和知识体系",
    "toolsets": ["web"]
  }
])
```

**注意**：子代理搜索结果可能为空或不理想（搜索引擎反爬），需要结合官方文档抓取的结果综合判断。子代理的价值在于补充社区视角（面经、实践文章、对比分析），而非替代官方文档。

### 1.4 调研要点 Checklist

确保收集到以下信息：
- [ ] 官方定义（一句话概括这个技术是什么）
- [ ] 发展历程/版本演进（帮助理解技术变迁）
- [ ] 生态全景（核心库、配套工具、平台）
- [ ] 核心 API / 核心概念（5-9 个）
- [ ] 代码示例（官方 Quickstart 级别）
- [ ] 与竞品/相关技术的对比
- [ ] 最新版本号和系统要求
- [ ] 学习路径建议
- [ ] 常见面试/考点（如适用）

---

## Phase 2: 知识结构化

### 2.1 统一文档结构模板

> 💡 完整的可复制模板见 `references/doc-template.md`，直接填空使用。

```markdown
# {主题} 入门完全指南

> 🌐 信息来源声明（附官方文档链接）

---

## 一、什么是 {主题}？
### 1.1 官方定义（引用原文）
### 1.2 发展历程（时间线表格）
### 1.3 一句话总结

## 二、生态全景 / 整体架构
### 2.1 组件关系（ASCII 架构图）
### 2.2 与相关技术的关系

## 三、核心概念详解（⭐ 按学习顺序排列）
### 3.1 概念 A ⭐⭐⭐⭐⭐
- 定义 + 代码示例
- 面试要点
### 3.2 概念 B ⭐⭐⭐⭐
...

## 四、进阶 / 高级特性

## 五、入门路径（可执行的 Step-by-Step）
### Day 1: ...
### Day 2: ...

## 六、面试 / 考点（如适用）
### 概念题
### 手撕题（含完整代码）

## 七、核心资源清单
### 官方资源
### 推荐课程
### 关键概念速查卡
```

### 2.2 结构设计原则

| 原则 | 说明 |
|------|------|
| **官方优先** | 定义、概念、API 以官方文档原文为准 |
| **由浅入深** | What is → Ecosystem → Core Concepts → Advanced → Practice |
| **代码驱动** | 每个核心概念至少配一个可运行的最简代码示例 |
| **对比清晰** | 用表格对比相似概念/竞品/版本差异 |
| **面试导向** | 如果用户目的是面试，每节标注 ⭐ 重要度，附面试题 |
| **用户背景感知** | 根据用户背景调整侧重点（如统计背景→强调数学原理） |

### 2.3 架构图用 ASCII

用 ASCII 艺术画架构关系，飞书 Markdown 支持 ` ``` ` 代码块渲染：

```
┌─────────────────────────────────────────┐
│              用户应用代码                  │
├─────────────────────────────────────────┤
│         高层 API                         │  ← 最省事
├─────────────────────────────────────────┤
│         底层引擎                          │  ← 最灵活
└─────────────────────────────────────────┘
```

---

## Phase 3: 飞书文档创建

### 3.1 前置条件

```bash
# 确认 lark-cli 可用且已认证
lark-cli auth status
```

加载 lark-doc 技能获取最新 API 用法：
```bash
lark-cli skills read lark-doc
```

### 3.2 创建文档（完整流程）

```bash
# Step 1: 将内容写入本地 markdown 文件
# 用 write_file 工具写入 /root/.hermes/_doc.md

# Step 2: 创建飞书文档（用 @file 方式避免 shell 转义地狱）
lark-cli docs +create \
  --api-version v2 \
  --doc-format markdown \
  --content @_doc.md

# Step 3: 验证文档内容
lark-cli docs +fetch \
  --api-version v2 \
  --doc <document_id> \
  --doc-format markdown

# Step 4: 清理临时文件
rm /root/.hermes/_doc.md
```

**关键要点**：
- `@file` 路径限制：只接受**当前工作目录下的相对路径**，绝对路径会报 `unsafe file path`
- 解决方案：`workdir` 设为 `/root/.hermes`，文件写为 `_doc.md`，传 `@_doc.md`
- `--api-version v2` 是必填参数
- 标题规则：Markdown 格式下，开头唯一的 `# 标题` 自动成为文档标题

### 3.3 交叉引用已有文档

当新文档与已有文档有关联时，在已有文档中插入链接：

```bash
# Step 1: 获取已有文档的 block 结构
lark-cli docs +fetch \
  --api-version v2 \
  --doc <existing_doc_id> \
  --detail with-ids

# Step 2: 找到要插入链接的位置（某个 h3/h4 的 block_id）
# 用 python3 从输出中精确提取目标 heading 的 block_id：
python3 -c "
import sys, json, re
data = json.load(sys.stdin)
content = data['data']['document']['content']
blocks = re.findall(r'<([a-z0-9]+)\s+id=\"([^\"]+)\"[^>]*>(.*?)</\1>', content, re.S)
for tag, bid, text in blocks:
    if '<关键词>' in re.sub(r'<[^>]+>', '', text):
        print(f'{bid}: {re.sub(\"<[^>]+>\", \"\", text[:100])}')
" <<< '<fetch_output>'

# Step 3: 在该 block 后插入引用框（blockquote 格式最稳定）
lark-cli docs +update \
  --api-version v2 \
  --doc <existing_doc_id> \
  --command block_insert_after \
  --block-id <target_block_id> \
  --content '<blockquote><p>📖 <b>相关文档标题</b>：<a href="https://my.feishu.cn/docx/<new_doc_id>">点击查看</a> — 简要描述。</p></blockquote>'
```

### 3.4 超长文档处理

如果文档超过 15KB，采用**先骨架后填充**策略：

```bash
# Step 1: 创建骨架（只有标题层级）
lark-cli docs +create \
  --api-version v2 \
  --doc-format markdown \
  --content '# 标题\n\n## 一、...\n### 1.1 ...\n### 1.2 ...'

# Step 2: 获取骨架的 block IDs
lark-cli docs +fetch --api-version v2 --doc <id> --detail with-ids

# Step 3: 用 delegate_task 并行填充各章节
# 每个 Agent 用 block_insert_after 写入一个章节

# 或更简单：直接用 overwrite 一次性写入完整内容
# （实测 25KB 以内的 Markdown 可以一次性 +create 或 overwrite 成功）
```

---

## Phase 4: 质量保证

### 4.1 验证 Checklist

- [ ] 文档链接可正常打开
- [ ] `lark-cli docs +fetch` 验证内容完整（首尾内容都在）
- [ ] 代码块格式正确（飞书 Markdown 支持 ``` 语法）
- [ ] 表格渲染正确（GFM Markdown 表格语法）
- [ ] 如有交叉引用，目标 block_id 已正确插入
- [ ] 临时文件已清理（`_*.md`）

### 4.2 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| `@file` 报 unsafe file path | 用了绝对路径 | 文件放在 cwd 下，用相对路径 `@_doc.md` |
| 文档标题显示 Untitled | 开头没有 `# 标题` 或有多个一级标题 | 确保开头唯一的一级标题 |
| 代码块不渲染 | markdown 转义问题 | 确保用 ``` 包裹，且反引号未被转义 |
| 表格渲染为纯文本 | 表格语法错误 | 确保用 GFM 格式 `| col1 | col2 |` + 分隔行 |
| `--content` 超长报错 | 内容超过 shell 参数限制 | 用 `@file` 方式传参 |
| 内容被截断 | 文档太大 | 分段用 `block_insert_after` 写入 |

---

## 用户偏好适配

根据 memory 中的用户信息调整：

1. **输出语言**：用户用中文交流时，文档全部用中文
2. **飞书优先**：所有文档生成为飞书文档（用户明确偏好）
3. **面试导向**：用户如果是准备面试，增加面试考点和手撕题板块
4. **用户背景**：利用用户的学科背景（如统计学→强调数学原理，C++→强调算法实现）
5. **交叉引用**：创建新文档时主动检查是否与已有文档关联，有则双向链接
6. **搜索偏好**：使用 Bing 搜索（非 Google）

---

## 实战示例

### 示例 1：创建 LangChain 入门文档

```
1. curl 抓取 python.langchain.com 官方文档 → 提取 meta description + 页面摘要
2. 按模板结构化：定义→生态→核心概念(9个)→入门路径→面试考点→资源
3. write_file → _lc_doc.md
4. lark-cli docs +create --content @_lc_doc.md → 获得 doc_id
5. lark-cli docs +fetch 验证
6. 在备战手册文档的对应位置 block_insert_after 插入链接
7. 清理临时文件
```

### 示例 2：创建一组系列文档

```
1. 先创建总纲文档（如"AI Agent 实习备战手册"）
2. 再逐个创建子文档（LangChain 指南、LangGraph 指南等）
3. 每创建一个子文档，在总纲文档中插入交叉链接
4. 最终形成：总纲 ←→ 子文档 的知识网络
```

### 示例 3：用 Skill 创建 RAG 入门文档（实测验证）

```
Phase 1: 并行 curl 抓取 3 个官方源（LangChain RAG tutorial、LlamaIndex、RAGAS）
         → LangChain 返回 36K 字符完整正文（SSR 渲染好），其余取 meta description
Phase 2: 按模板结构化 10 个板块，填入官方定义+代码示例+对比表格
Phase 3: write_file → _rag_doc.md (23.8KB) → lark-cli docs +create → 验证完整
Phase 4: 在备战手册 2.2 节 RAG 标题后 block_insert_after 插入引用框链接
总耗时：约 5 分钟（Skill 加载后全程自动）
```
