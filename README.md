# Claude Code Skills

个人维护的 [Claude Code](https://claude.com/claude-code) Skills 集合。

## 是什么

Skills 是 Claude Code 的能力扩展——类似插件，它告诉 Claude 在特定场景下该怎么做。每个 Skill 就是一个包含 `SKILL.md` 文件的文件夹，里面用自然语言描述了工作流程和使用方法。

## 安装

将 Skill 文件夹复制到本地 skills 目录即可：

```bash
# 克隆仓库
git clone git@github.com:Zjrua/skills.git

# 复制到 Claude Code skills 目录
cp -r skills/obsidian-vault-manager ~/.claude/skills/
```

## Skills 列表

### obsidian-vault-manager

通过 Obsidian 官方 CLI 管理 Obsidian Vault 中的笔记。

**功能：**
- 创建、读取、搜索、编辑笔记
- 管理双向链接 `[[wikilinks]]` 和标签
- 查看 vault 结构、反向链接、孤儿笔记、断链检测

**触发条件：** 提到 Obsidian、vault、笔记、知识库，或需要对笔记进行任何操作时自动触发。

**依赖：** 需要安装 [Obsidian CLI](https://obsidian.md/cli)（Obsidian 1.12+ 内置）。

## 结构

```
skills/
└── obsidian-vault-manager/
    └── SKILL.md          # Skill 定义文件
```

## 如何编写自己的 Skill

1. 创建文件夹，放入 `SKILL.md`
2. 在 `SKILL.md` 的 YAML frontmatter 中填写 `name` 和 `description`
3. 正文部分用自然语言描述工作流程、命令用法和注意事项
4. 将文件夹复制到 `~/.claude/skills/` 即可生效

详细文档参考 [Claude Code Skills](https://docs.anthropic.com/en/docs/claude-code/skills)。
