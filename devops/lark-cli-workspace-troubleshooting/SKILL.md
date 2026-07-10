---
name: lark-cli-workspace-troubleshooting
description: "lark-cli workspace/profile 隔离机制与认证故障排查。当 lark-cli 在 agent 环境和终端环境中行为不一致、用户授权不生效、'not configured' 或 'need_user_authorization' 或 'forbidden' 错误时使用。"
---

# lark-cli Workspace 隔离与认证故障排查

## 核心概念：双配置隔离

lark-cli 有 profile/workspace 机制。Hermes agent 使用独立的 **hermes workspace**，与终端用户的默认 profile 完全隔离。

| 环境 | 配置路径 | 说明 |
|------|----------|------|
| 终端直接执行 | `~/.lark-cli/config.json` | 默认 profile |
| Hermes Agent | `~/.lark-cli/hermes/config.json` | hermes workspace（agent 专用） |

可用 `lark-cli doctor` 查看当前 workspace（输出 `"workspace": "hermes"` 或 `"workspace": "default"`）。

## 关键差异

### App Secret 存储格式

- **主配置**（终端）：支持 `"source": "plain"` 明文和 `"source": "keychain"` 引用
- **hermes workspace**：必须使用 `"source": "keychain"` 格式。改为 plain 会导致 `"not configured"` 错误，即使 appId 和 appSecret 值完全正确

### 用户 Token 隔离

用户通过 `lark-cli auth login` 获取的 OAuth token 是 **workspace 级别**的：
- 在终端（默认 profile）完成 auth login，token 不会出现在 hermes workspace
- Hermes agent 执行 `lark-cli auth status` 会显示 "No user logged in"，即使终端已授权

## 常见问题排查

### 1. Bot 身份操作文档报 `forbidden`

```
No permission to operate on this document: the current user lacks view or edit access
```

**原因**：机器人账号失去了目标文档的编辑权限。

**解决方案**（二选一）：
- **方案 A（推荐）**：在飞书客户端打开文档 → 分享 → 重新添加机器人为「可编辑」协作者
- **方案 B**：以用户身份操作（需要先完成 hermes workspace 的用户授权）

### 2. `auth login` 报 strict mode 拒绝

```
strict mode is "bot", only bot identity is allowed
```

**解决**：在 hermes 配置中将 `strictMode` 改为 `"off"`：
```json
"strictMode": "off"
```

### 3. `auth login` 报 "not configured"

```
Error: "not configured", hint: "run lark-cli config init --new"
```

**原因**：
- 主配置缺少 `defaultAs` 字段 → 添加 `"defaultAs": "bot"` 和 `"strictMode": "off"`
- Hermes workspace 的 appSecret 格式不是 keychain → **不要改**，hermes workspace 要求 keychain 格式

### 4. Agent 中 `--as user` 报 `need_user_authorization`

```
Error: need_user_authorization (user: )
```

**原因**：hermes workspace 中没有用户 token。终端的 auth login 不会影响 hermes workspace。

**解决**：需要在 hermes workspace 上下文中完成 auth login：
```bash
# 在 agent 环境中用 background 方式发起
lark-cli auth login --recommend
```
将输出的验证 URL 发给用户，用户在浏览器中完成授权。授权完成后 agent 即可使用 `--as user`。

## 配置文件模板

### ~/.lark-cli/hermes/config.json（agent 环境）

```json
{
  "apps": [
    {
      "appId": "cli_a92edcfa23f8dbc9",
      "appSecret": {
        "source": "keychain",
        "id": "appsecret:cli_a92edcfa23f8dbc9"
      },
      "brand": "feishu",
      "lang": "zh",
      "defaultAs": "bot",
      "strictMode": "off",
      "users": []
    }
  ]
}
```

注意：`appSecret` 必须用 keychain 格式，不要改成 plain。

### ~/.lark-cli/config.json（终端用户）

```json
{
  "apps": [
    {
      "appId": "cli_a92edcfa23f8dbc9",
      "appSecret": {
        "source": "plain",
        "value": "实际密钥"
      },
      "brand": "feishu",
      "lang": "zh",
      "defaultAs": "bot",
      "strictMode": "off",
      "users": [
        {
          "userOpenId": "ou_xxx",
          "userName": "用户名"
        }
      ]
    }
  ]
}
```

## v1 vs v2 API

`docs +update` 有两个 API 版本：
- **v1**（默认，已 deprecated）：`--mode append --markdown "..."`，bot 权限操作文档可能报 forbidden
- **v2**：`--command append --content "..." --doc-format markdown`，需要 `--command` 参数

两者参数语法不同，注意区分。

### ⚠️ v1 `overwrite` 可能静默失败（2026-05-16 确认）

v1 API `docs +update --mode overwrite --markdown @file` 返回 `ok: true`，但文档内容可能**实际未更新**。原因未明，可能与 `@file` 相对路径解析有关。

**推荐做法**：始终使用 v2 API 进行 overwrite：
```bash
lark-cli docs +update --api-version v2 --doc "TOKEN" \
  --command overwrite --content @./daily_news.md --doc-format markdown
```

**必须在 overwrite 后验证**：用 API 读取文档前几个 block，确认内容是新的而非旧的：
```bash
lark-cli api GET "/open-apis/docx/v1/documents/TOKEN/blocks" --as bot --page-size 5
```

### ⚠️ `write_file` 与 `terminal` 工作目录可能不同（2026-05-16 确认）

`write_file` 工具写入文件到 hermes-agent 工作目录（通常 `/root/.hermes/hermes-agent/`），但文件可能**不会覆盖已存在的同名旧文件**（或写入到不同路径）。

**安全做法**：`write_file` 后，立即用 `terminal` 验证文件内容：
```bash
head -3 daily_news.md
```
如果内容是旧的，重新 `write_file` 或用 `terminal` 直接 `cat > file << 'EOF'` 写入。

## cron 日报完整工作流（验证版）

经过多次踩坑后的可靠流程：

```bash
# 1. 写入日报文件（write_file 或 terminal cat）
# 2. ⚠️ 验证文件内容是今天的！
head -3 daily_news.md

# 3. 用 v2 API overwrite（不要用 v1）
lark-cli docs +update --api-version v2 --doc "TOKEN" \
  --command overwrite --content @./daily_news.md --doc-format markdown

# 4. 更新文档标题（v1 append + --new-title）
lark-cli docs +update --doc "TOKEN" --mode append \
  --markdown " " --new-title "📰 YYYY年MM月DD日 新闻日报"

# 5. ⚠️ 验证文档内容（必须！）
lark-cli api GET "/open-apis/docx/v1/documents/TOKEN/blocks" --as bot --page-size 5
# 检查前几个 block 的文本是否为今天的内容
```

## 相关 Skills

- `lark-shared`（`~/.agents/skills/lark-shared/SKILL.md`）：认证、身份切换、权限管理的基础规则
- `lark-doc`（`~/.agents/skills/lark-doc/SKILL.md`）：文档创建和更新的详细用法
