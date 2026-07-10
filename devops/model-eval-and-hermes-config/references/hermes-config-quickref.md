# Hermes Config Quick Reference

模型配置相关的 Hermes CLI 和配置速查。完整文档见 `hermes-agent` skill。

## CLI 命令

```bash
hermes model                    # 交互式模型/Provider 选择
hermes config set KEY VAL       # 设置配置值
hermes config edit              # 编辑 config.yaml
hermes config check             # 检查配置完整性
hermes doctor [--fix]           # 检查依赖和配置
hermes auth add                 # 添加 Credential
hermes auth list                # 查看已存 Credential
hermes profile list             # 列出所有 Profile
hermes profile create NAME      # 创建 Profile (--clone, --clone-all)
```

## Slash Commands (会话内)

```
/model [name]       # 查看/切换模型
/config             # 显示当前配置
/reload             # 重载 .env 变量
/stop               # 终止后台进程
/new                # 新会话
```

## Providers 与环境变量

| Provider | 环境变量 | base_url 示例 |
|----------|---------|--------------|
| DeepSeek | `DEEPSEEK_API_KEY` | `https://api.deepseek.com` |
| OpenAI | `OPENAI_API_KEY` | `https://api.openai.com/v1` |
| Anthropic | `ANTHROPIC_API_KEY` | `https://api.anthropic.com` |
| Google Gemini | `GEMINI_API_KEY` | `https://generativelanguage.googleapis.com` |
| 智谱 Z.AI | `GLM_API_KEY` | `https://open.bigmodel.cn/api/paas/v4` |
| 小米 MiMo | `XIAOMI_API_KEY` | `https://api.xiaomimimo.com/v1` |
| 方舟 Ark | 方舟 API Key | `https://ark.cn-beijing.volces.com/api/coding/v3` |
| OpenRouter | `OPENROUTER_API_KEY` | `https://openrouter.ai/api/v1` |
| Kimi / Moonshot | `KIMI_API_KEY` | `https://api.moonshot.cn/v1` |
| xAI / Grok | `XAI_API_KEY` | `https://api.x.ai/v1` |

## 关键配置路径

```
~/.hermes/config.yaml              # 主配置
~/.hermes/.env                     # API Keys
~/.hermes/skills/                  # Skills
~/.hermes/profiles/<name>/config.yaml  # Profile 级配置
```

## 验证模型名称

```bash
source ~/.hermes/.env
curl -s <provider-base-url>/models \
  -H "Authorization: Bearer *** output)
```

## Fallback 配置

```yaml
fallback_providers:
  - model: <model>
    provider: <provider>
```

## Auxiliary 配置

```yaml
auxiliary:
  vision:
    provider: <provider>
    model: <model>
  compression:
    provider: auto
  summary:
    model: <model>
    summary_provider: auto
```

## 变更生效规则

| 变更类型 | 生效方式 |
|---------|---------|
| model/provider | CLI 退出重进，Gateway `/restart` |
| tools/skills | `/reset` 启动新会话 |
| config.yaml | `hermes config check` 验证后重启 |

## Troubleshooting

- **Voice not working**: `stt.enabled: true` + 检查 provider/安装
- **Tool not available**: `hermes tools` 检查 + 检查 env vars
- **Model issues**: `hermes doctor` + `.env` API Key
- **Gateway dies on SSH logout**: `sudo loginctl enable-linger $USER`
