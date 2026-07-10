---
name: notion
description: Notion workspace integration - read, write, query pages and databases
metadata:
  {
    "openclaw": {
      "requires": {
        "env": ["NOTION_TOKEN"],
        "bins": ["python3"]
      },
      "primaryEnv": "NOTION_TOKEN",
      "install": [
        {
          "id": "pip",
          "kind": "pip",
          "package": "notion-client",
          "label": "Install Notion Python client"
        }
      ]
    }
  }
---

# Notion 技能

## 功能

此技能提供与 Notion 工作空间的深度集成，支持以下操作：

### 📄 页面操作
- 读取页面内容（包括子块）
- 创建新页面
- 更新页面属性和内容
- 删除页面

### 🗄️ 数据库操作
- 查询数据库记录
- 添加新记录
- 更新记录属性
- 删除记录
- 数据库过滤和排序

### 🔍 搜索
- 在工作空间内搜索内容
- 按标题、标签等条件过滤

### 📦 块管理
- 添加文本块
- 添加标题（H1/H2/H3）
- 添加列表、待办事项
- 添加代码块
- 添加图片、文件

## 配置

### 必需环境变量

在 `~/.openclaw/openclaw.json` 中配置：

```json
{
  "skills": {
    "entries": {
      "notion": {
        "enabled": true,
        "apiKey": "YOUR_NOTION_INTEGRATION_TOKEN",
        "env": {
          "NOTION_TOKEN": "YOUR_NOTION_INTEGRATION_TOKEN"
        }
      }
    }
  }
}
```

### 获取 Notion Integration Token

1. 访问 https://www.notion.so/my-integrations
2. 点击 "+ New integration"
3. 填写名称（如 "OpenClaw"）
4. 选择关联的工作空间
5. 提交后复制 "Internal Integration Token"
6. 将上面的 token 配置到 `openclaw.json`

### 分享页面给 Integration

对于每个需要访问的 Notion 页面：

1. 打开页面 → 点击右上角 `...`
2. 选择 "Add connections"
3. 选择你创建的 Integration
4. 确认添加

**重要：** 即使有 API token，必须显式分享页面才能访问。

## 使用示例

### 读取页面内容

用户：帮我读取这个 Notion 页面的内容 https://www.notion.so/your-workspace/Page-Title-xxxxxxxxxxxxxxxx

我会：
1. 从 URL 提取 Page ID
2. 调用 API 获取页面内容
3. 返回格式化的内容

### 创建新页面

用户：在数据库 Database-xxxxxxxxxxxxxxxx 中创建一个新记录，标题是"新任务"，状态是"进行中"

我会：
1. 获取数据库 schema
2. 创建新记录并填充属性
3. 返回新记录的链接

### 查询数据库

用户：查询数据库 Tasks-xxxxxxxxxxxxxxxx 中所有状态为"待办"的任务

我会：
1. 构建过滤条件
2. 查询数据库
3. 返回符合条件的记录列表

### 搜索工作空间

用户：在 Notion 中搜索包含"项目里程碑"的内容

我会：
1. 调用搜索 API
2. 返回匹配的页面和数据库记录

## 注意事项

- **权限：** 只能访问已分享给 Integration
- **速率限制：** Notion API 有速率限制，避免批量操作
- **数据类型：** 不同属性类型需要正确转换（日期、选择项等）
- **ID 格式：** Notion ID 是带连字符的 32 位字符串
- **安全：** 妥善保管 Integration Token，不要分享给他人

## 常见任务

### 从飞书消息创建 Notion 记录

配合 `feishu-bitable` 技能，可以自动将飞书表格数据同步到 Notion 数据库。

### 定期报告自动化

结合 cron/heartbeat，定期从 Notion 读取数据并生成报告发送到飞书。

### 知识库管理

使用搜索功能，快速定位 Notion 中的笔记和文档。
