# AI Agent Skills

个人维护的 AI Agent Skills 集合，适用于 Hermes Agent、Claude Code、OpenClaw 等支持 Skill/插件机制的 AI 工具。

## 是什么

Skill 本质上是一份**用自然语言编写的工作流指南**——告诉 AI Agent 在特定场景下该怎么做。每个 Skill 就是一个文件夹，核心文件是 `SKILL.md`，里面描述了工作流程、命令用法和注意事项。

## 安装

```bash
git clone git@github.com:Zjrua/skills.git
```

将对应 Skill 文件夹放到你的 AI 工具指定的 skills 目录：

| 工具 | Skills 目录 |
| ---- | ----------- |
| Hermes Agent | `~/.hermes/skills/` |
| Claude Code | `~/.claude/skills/` |

## Skills 列表

### 活跃 Skills

| Skill | 说明 |
| ----- | ---- |
| [obsidian-vault-manager](obsidian-vault-manager/) | 通过 Obsidian CLI 管理 Vault 笔记 |
| [research-paper-writing](research-paper-writing/) | ML 论文写作全流程（NeurIPS/ICML/ICLR 等），含模板 |
| [smart-home/openhue](smart-home/openhue/) | Philips Hue 灯光控制 |

### 归档 Skills

已不再使用或被内置 skill 取代的旧版本：

| Skill | 说明 |
| ----- | ---- |
| [archive/handwritten-table-ocr](archive/handwritten-table-ocr/) | 手写表格 OCR 提取 |
| [archive/image-pdf-to-latex-cheatsheet](archive/image-pdf-to-latex-cheatsheet/) | 图片PDF转LaTeX速查表 |
| [archive/lark-whiteboard-cli](archive/lark-whiteboard-cli/) | 飞书画板图表设计 |
| [archive/lark-workflow-meeting-summary](archive/lark-workflow-meeting-summary/) | 飞书会议纪要汇总 |
| [archive/lark-workflow-standup-report](archive/lark-workflow-standup-report/) | 飞书日程待办摘要 |
| [archive/latex-to-feishu-review](archive/latex-to-feishu-review/) | LaTeX复习材料转飞书文档 |
| [archive/mimo-vision-extraction](archive/mimo-vision-extraction/) | mimo-v2.5 视觉数据提取 |
| [archive/mlx-vlm-quantize](archive/mlx-vlm-quantize/) | Apple Silicon VLM 量化 |
| [archive/pdf-doc-update](archive/pdf-doc-update/) | PDF数据提取补充飞书文档 |
| [archive/xitter](archive/xitter/) | X/Twitter CLI 交互 |

## 结构

```
├── obsidian-vault-manager/
│   └── SKILL.md
├── research-paper-writing/
│   ├── SKILL.md
│   ├── references/
│   └── templates/          # 各会议 LaTeX 模板
├── smart-home/
│   └── openhue/
│       └── SKILL.md
├── archive/                # 已归档的旧 skills
│   └── ...
└── README.md
```

## 编写自己的 Skill

1. 新建文件夹，放入 `SKILL.md`
2. YAML frontmatter 填写 `name` 和 `description`
3. 正文用自然语言写清楚工作流程
4. 放到对应工具的 skills 目录即可生效
