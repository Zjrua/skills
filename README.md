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

### 数据科学

| Skill | 说明 |
| ----- | ---- |
| [chinese-ecommerce-data](data-science/chinese-ecommerce-data/) | 淘宝/京东/拼多多商品数据采集 |

### DevOps / 工具链

| Skill | 说明 |
| ----- | ---- |
| [lark-cli-bitable-workflow](devops/lark-cli-bitable-workflow/) | lark-cli 操作飞书多维表格实战踩坑 |
| [lark-cli-workspace-troubleshooting](devops/lark-cli-workspace-troubleshooting/) | lark-cli workspace/profile 认证故障排查 |
| [model-benchmark-evaluation](devops/model-benchmark-evaluation/) | 模型评测分数收集 → 加权评分 → 飞书表格发布 |
| [playwright-manual-install](devops/playwright-manual-install/) | 国内网络 Playwright chromium 手动安装 |
| [xiaomi-token-plan](devops/xiaomi-token-plan/) | 小米 MiMo Token Plan 作为 Hermes provider 配置 |
| [zhipu-coding-plan](devops/zhipu-coding-plan/) | 智谱编码套餐用量查询与配置 |

### 创意 / 媒体

| Skill | 说明 |
| ----- | ---- |
| [heartmula](media/heartmula/) | HeartMuLa 歌词转歌曲生成 |

### 效率工具

| Skill | 说明 |
| ----- | ---- |
| [feishu-doc-to-tracking-bitable](productivity/feishu-doc-to-tracking-bitable/) | 飞书文档结构化内容转多维表格追踪 |
| [leetcode-training](productivity/leetcode-training/) | LeetCode Hot 100 训练计划 + 飞书进度追踪 |
| [tech-research-to-feishu](productivity/tech-research-to-feishu/) | 技术调研 → 结构化知识 → 飞书文档 |

### 研究

| Skill | 说明 |
| ----- | ---- |
| [chinese-university-english-sites](research/chinese-university-english-sites/) | 中国高校英文网站内容采集 |
| [research-paper-writing](research-paper-writing/) | ML论文写作全流程（NeurIPS/ICML/ICLR等），含模板 |

### 软件开发

| Skill | 说明 |
| ----- | ---- |
| [plan](software-development/plan/) | Plan 模式：写可执行 Markdown 计划 |
| [requesting-code-review](software-development/requesting-code-review/) | 提交前审查：安全扫描 + 质量门禁 |

### 其他

| Skill | 说明 |
| ----- | ---- |
| [obsidian-vault-manager](obsidian-vault-manager/) | Obsidian CLI 管理 Vault 笔记 |
| [wechat-article-scraping](wechat-article-scraping/) | 微信公众号文章元数据/正文提取 |

### 归档

已不再使用或被内置 skill 取代：

| Skill | 说明 |
| ----- | ---- |
| archive/handwritten-table-ocr | 手写表格 OCR |
| archive/image-pdf-to-latex-cheatsheet | 图片PDF转LaTeX速查表 |
| archive/lark-whiteboard-cli | 飞书画板图表设计 |
| archive/lark-workflow-meeting-summary | 飞书会议纪要汇总 |
| archive/lark-workflow-standup-report | 飞书日程待办摘要 |
| archive/latex-to-feishu-review | LaTeX复习材料转飞书文档 |
| archive/mimo-vision-extraction | mimo-v2.5 视觉数据提取 |
| archive/mlx-vlm-quantize | Apple Silicon VLM 量化 |
| archive/pdf-doc-update | PDF数据提取补充飞书文档 |
| archive/xitter | X/Twitter CLI 交互 |

## 结构

```
├── obsidian-vault-manager/
├── research-paper-writing/
│   ├── SKILL.md
│   ├── references/
│   └── templates/
├── wechat-article-scraping/
├── data-science/
├── devops/
├── media/
├── productivity/
├── research/
├── software-development/
├── archive/
└── README.md
```
