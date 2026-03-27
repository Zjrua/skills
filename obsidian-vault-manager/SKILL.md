---
name: obsidian-vault-manager
description: >-
  Manage Obsidian vault via the official Obsidian CLI. Use this skill whenever the user wants to
  create, read, search, edit, organize, or manage notes in their Obsidian vault — including
  creating knowledge point notes, adding content to existing notes, searching for topics,
  managing tags and links, listing vault structure, or any vault-related operation. Also trigger
  when the user mentions "vault", "笔记", "知识库", "Obsidian", or wants to add/link/organize
  academic knowledge.
---

# Obsidian Vault Manager

Use the Obsidian CLI (`obsidian vault=Study`) to manage the Study vault. All commands target the
Study vault by default.

## Core Concepts

- **MOC (Map of Content)**: Navigation hub for each course, links to all knowledge points
- **Knowledge point notes**: Atomic notes for individual concepts, linked bidirectionally
- **Templates**: Located at `00-模板/` — knowledge point template, exercise template, course template
- **Structure**: `01-数学基础/` (undergrad), `02-研究生课程/` (grad), `03-交叉关联/` (cross-links)

## Available Operations

### Read & Search

```bash
# Read a note by filename (like wikilinks)
obsidian vault=Study read file="特征值与特征向量"

# Search vault content
obsidian vault=Study search query="矩阵分解"

# Search with line context
obsidian vault=Study search:context query="Black-Scholes"

# Show outgoing links from a note
obsidian vault=Study links file="主成分分析PCA"

# Show backlinks (who links to this note)
obsidian vault=Study backlinks file="主成分分析PCA" counts

# List all files in a folder
obsidian vault=Study files folder="01-数学基础/线性代数"

# Get vault stats
obsidian vault=Study files total
obsidian vault=Study tags total
```

### Create Notes

When creating a new knowledge point note, follow this structure:

```bash
obsidian vault=Study create path="<folder>/<NoteName>.md" content="<content>"
```

The content should include:
1. YAML frontmatter with tags, course name, prerequisites, difficulty
2. Core definitions with LaTeX formulas ($...$ for inline, $$...$$ for display)
3. Theorems and properties
4. Intuitive explanation in plain language
5. A `## 相关知识点` section with `[[links]]` to related notes

Example — creating a new knowledge point:

```
obsidian vault=Study create path="02-研究生课程/多元统计分析/典型相关分析.md" content="---
tags:
  - 知识点
课程: 多元统计分析
前置知识: [\"主成分分析PCA\"]
难度: ⭐⭐⭐
---

# 典型相关分析

## 核心定义

...

## 核心公式

$$
...
$$

## 相关知识点

- [[主成分分析PCA]]
- [[多元正态分布]]
"
```

### Edit Notes

```bash
# Append content (with newline)
obsidian vault=Study append file="特征值与特征向量" content="\n## 新增章节\n..."

# Prepend content
obsidian vault=Study prepend file="特征值与特征向量" content="<!-- 新内容 -->\n"

# Append inline (no trailing newline)
obsidian vault=Study append file="特征值与特征向量" content="inline text" inline
```

**Important**: The CLI's `append` and `prepend` only add content. For editing existing content
(read-modify-write), use the Read/Edit file tools directly on the markdown files in the vault
directory instead.

### Manage Structure

```bash
# Move/rename a note (preserves links in Obsidian)
obsidian vault=Study move file="OldName" to="new-folder/NewName"

# Rename a note
obsidian vault=Study rename file="OldName" name="NewName"

# Delete a note (moves to trash)
obsidian vault=Study delete file="UnwantedNote"

# List folders
obsidian vault=Study folders

# List orphan notes (no backlinks)
obsidian vault=Study orphans

# List dead-end notes (no outgoing links)
obsidian vault=Study deadends

# List unresolved links
obsidian vault=Study unresolved
```

### Tags & Properties

```bash
# List all tags with counts
obsidian vault=Study tags counts sort=count

# List tags for a specific note
obsidian vault=Study tags file="特征值与特征向量"

# Read a property from a note
obsidian vault=Study property:read name="课程" file="特征值与特征向量"

# Set a property on a note
obsidian vault=Study property:set name="难度" value="⭐⭐⭐" file="特征值与特征向量"
```

## Folder Structure Reference

```
Study/
├── 首页.md
├── 00-模板/
│   ├── 知识点模板.md
│   ├── 习题模板.md
│   └── 课程笔记模板.md
├── 01-数学基础/
│   ├── MOC-数学基础.md
│   ├── 高等数学/
│   ├── 线性代数/
│   └── 概率论与数理统计/
├── 02-研究生课程/
│   ├── MOC-研究生课程.md
│   ├── 数值代数/
│   ├── 多元统计分析/
│   ├── 数理金融/
│   └── 时间序列分析/
└── 03-交叉关联/
    └── 知识网络.md
```

## Workflow Tips

1. **Before creating a new note**, check if a related note already exists:
   `obsidian vault=Study search query="<keyword>"`

2. **After creating a note**, verify it has backlinks from relevant MOC pages. If a MOC doesn't
   link to it yet, update the MOC to include the new note.

3. **When adding links**, always use `[[exact filename]]` format matching the file name without
   the .md extension.

4. **For bulk operations** (e.g., adding a link to multiple notes), iterate and use `append`
   rather than reading/editing each file individually.

5. **The vault files live at**:
   `/Users/zjrua/Library/Mobile Documents/iCloud~md~obsidian/Documents/Study/`
   For complex edits (read-modify-write), use the Read/Edit tools on these files directly.
