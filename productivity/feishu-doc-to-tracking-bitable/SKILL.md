---
name: feishu-doc-to-tracking-bitable
description: "将飞书文档中的结构化内容（如分镜、清单、任务列表）提取并转换为飞书多维表格（Bitable），用于进度追踪、状态管理和协作。当用户有文档中的列表/表格内容需要变成可交互的追踪表时使用。"
---

# 飞书文档 → 多维表格（Bitable）进度追踪

将飞书文档中提取的结构化条目（镜头、任务、清单项等）批量导入为多维表格，支持勾选确认和状态管理。

## 前置条件

- 已安装 `lark-cli` 并完成认证
- 已安装 lark-base skill（`~/.agents/skills/lark-base/`）
- 有目标文档的读取权限

## 工作流

### 1. 读取并解析文档内容

```bash
lark-cli docs +fetch --doc "DOC_TOKEN" --format pretty
```

从输出中提取结构化条目。常见模式：
- `## 场景 X.X — 名称` + `### 镜头 N` → 分镜场景+镜头
- `## 章节` + 列表项 → 任务清单
- 表格内容 → 记录行

用 Python `execute_code` 解析更可靠：`grep` + 正则提取场景/镜头/任务条目。

### 2. 创建 Base

```bash
lark-cli base +base-create --name "项目名 — 进度追踪表" --time-zone "Asia/Shanghai"
```

从返回的 JSON 中提取 `base_token`。

### 3. 创建数据表 + 字段

常用字段组合（进度追踪场景）：

| 字段 | 类型 | 用途 |
|------|------|------|
| 分组/场景 | `text` | 条目所属的分组 |
| 编号 | `number` | 条目序号 |
| 描述 | `text` | 条目详细描述 |
| 已完成 | `checkbox` | 勾选确认 |
| 状态 | `select` | 未开始/进行中/已完成/需重做 |
| 备注 | `text` | 补充说明 |

```bash
lark-cli base +table-create \
  --base-token BASE_TOKEN \
  --name "条目清单" \
  --fields '[{"type":"text","name":"场景"},{"type":"number","name":"编号"},{"type":"text","name":"描述"},{"type":"checkbox","name":"已完成"},{"type":"select","name":"状态","multiple":false,"options":[{"name":"未开始","hue":"Gray","lightness":"Lighter"},{"name":"进行中","hue":"Blue","lightness":"Light"},{"name":"已完成","hue":"Green","lightness":"Light"},{"name":"需重做","hue":"Orange","lightness":"Light"}]},{"type":"text","name":"备注"}]'
```

从返回中获取 `table_id`。

### 4. 删除默认空表

创建 Base 时会自动生成一个默认空表（"数据表"），需删除：

```bash
lark-cli base +table-list --base-token BASE_TOKEN  # 先确认默认表 ID
lark-cli base +table-delete --base-token BASE_TOKEN --table-id tblDEFAULT_ID --yes
```

### 5. 批量写入记录

**⚠️ 关键坑点**：`--json @file` 中的文件路径必须是**相对路径**（相对于 cwd），绝对路径会报错！

```bash
cd /tmp  # 先切到文件所在目录
# 准备 JSON 文件
lark-cli base +record-batch-create \
  --base-token BASE_TOKEN \
  --table-id TABLE_ID \
  --json @./batch_data.json
```

batch_data.json 格式：
```json
{
  "fields": ["场景", "编号", "描述", "已完成", "状态", "备注"],
  "rows": [
    ["场景1", 1, "描述1", false, "未开始", null],
    ["场景1", 2, "描述2", false, "未开始", null]
  ]
}
```

- 单次最多 200 行
- checkbox 字段值用 `false`/`true`（布尔值）
- select 字段值用字符串（单选）或字符串数组（多选）
- 空值用 `null`

### 6. 在原文档中添加跳转链接（可选）

在原始文档末尾追加多维表格链接：

```bash
cd /tmp
cat > append.md << 'EOF'
---
<callout emoji="📊" background-color="light-green">
**进度追踪**：[点击查看多维表格](BASE_URL)
</callout>
EOF

lark-cli docs +update --api-version v2 \
  --doc "DOC_TOKEN" \
  --command append \
  --content @./append.md \
  --doc-format markdown
```

## 关键坑点

| 坑点 | 说明 | 解决 |
|------|------|------|
| `@file` 路径 | 必须用相对路径，`/tmp/file.json` 会报 validation 错误 | `cd` 到文件目录后用 `@./file.json` |
| 命令是 `base` 不是 `bitable` | 旧名叫 bitable，CLI 命令是 `lark-cli base` | 不要用 `lark-cli bitable` |
| 默认空表 | `+base-create` 会自动创建一个"数据表"含空记录 | 创建后 `+table-list` 确认并删除 |
| checkbox 字段值 | 写入时用布尔值 `true`/`false`，不是字符串 | `+record-batch-create` 的 rows 中直接用 `false` |
| `--as user` | Base 写操作默认用 user 身份 | 如权限不足可显式加 `--as bot` |

## 执行前必读

- `~/.agents/skills/lark-base/SKILL.md` — lark-cli base 完整指南
- `~/.agents/skills/lark-base/references/lark-base-shortcut-field-properties.md` — 字段 JSON 格式
- `~/.agents/skills/lark-base/references/lark-base-shortcut-record-value.md` — 记录值格式
- `~/.agents/skills/lark-base/references/lark-base-record-batch-create.md` — 批量写入
