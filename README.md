# AI Agent Skills

个人维护的 AI Agent Skills 集合，适用于 Claude Code、OpenClaw 等支持 Skill/插件机制的 AI 工具。

## 是什么

Skill 本质上是一份**用自然语言编写的工作流指南**——告诉 AI Agent 在特定场景下该怎么做。每个 Skill 就是一个文件夹，核心文件是 `SKILL.md`，里面描述了工作流程、命令用法和注意事项。

因为本质就是结构化的 Markdown，所以不绑定特定平台，任何能读取并遵循指令的 AI Agent 都可以使用。

## 安装

克隆仓库后，将对应 Skill 文件夹放到你的 AI 工具指定的 skills 目录：

```bash
git clone git@github.com:Zjrua/skills.git
```

不同工具的目录位置可能不同，以下是常见配置：

| 工具 | Skills 目录 |
| ---- | ----------- |
| Claude Code | `~/.claude/skills/` |
| OpenClaw | 参考 OpenClaw 文档 |

## Skills 列表

### obsidian-vault-manager

通过 Obsidian 官方 CLI 管理 Obsidian Vault 中的笔记。

- 创建、读取、搜索、编辑笔记
- 管理双向链接 `[[wikilinks]]` 和标签
- 查看 vault 结构、反向链接、孤儿笔记、断链检测

**依赖：** [Obsidian CLI](https://obsidian.md/cli)（Obsidian 1.12+ 内置）

## 结构

```
├── obsidian-vault-manager/
│   └── SKILL.md
```

## 编写自己的 Skill

1. 新建文件夹，放入 `SKILL.md`
2. YAML frontmatter 填写 `name` 和 `description`（触发描述）
3. 正文用自然语言写清楚工作流程
4. 放到对应工具的 skills 目录即可生效
