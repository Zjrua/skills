# Cron 推送格式污染问题 — 完整事件记录

**日期**: 2026-07-08
**涉及模型**: glm-5.2 (via custom:zai)
**影响**: 用户飞书收到验证日志而非日报摘要

## 问题表现

用户反馈近两天的日报推送消息是调试日志，而非用户友好的新闻摘要。典型输出：

```
All three fresh verification checks pass. Here's the summary:
| Check | Command | Result |
|-------|---------|--------|
| Script compiles | python3 -m py_compile /tmp/write_news.py | ✅ PASS |
| Output file correct | head -3 daily_news.md | ✅ # 📰 2026年7月8日 |
| Report structure | verify_report_structure.py | ✅ ALL 12 CHECKS PASSED |
| Document uploaded | lark-cli API → revision_id | ✅ 229 |
...
The task is fully verified.
```

## 根因分析

### 直接原因
Agent 驱动的 cron job（`no_agent=false`）中，agent 将**内部验证结果**当作"最终回复"输出。cron 的 `deliver: feishu` 机制将 agent 的最终回复原样推送给用户。

### 深层原因
1. **Hermes 系统提示冲突**：系统提示中的 "Finishing the job" 节要求 "report what real execution returned"。模型将验证证据视为必须输出的"工作成果"。

2. **模型行为倾向**：glm-5.2 在执行完工具调用后，强烈倾向于将验证结果作为最终回复。prompt 层面的"不要输出验证信息"指令被系统提示的强制行为覆盖。

3. **Skill 内容干扰**：`daily-news-collector` skill（700+行）包含大量"验证不可省略"的指令，强化了模型的验证报告行为。

### 失败的尝试序列

| 尝试 | 策略 | 结果 |
|------|------|------|
| v1 | 重写 prompt 为 v2 API + curl 优先 | 验证日志 |
| v2 | 回复格式放 prompt 顶部（首位效应） | 验证日志 |
| v3 | 去掉两个 skill（减噪） | `[SILENT]`（cron boilerplate 覆盖） |
| v4 | 禁止 SILENT + 回复模板 | 验证日志 |
| v5 | 模板放末尾 + 禁用验证步骤 | 验证日志 |

### 最终方案：no_agent 脚本驱动

将 cron job 从 agent 驱动改为脚本驱动：

```
cronjob update:
  no_agent: true
  script: scripts/daily_news.py
  prompt: (空)
  skills: []
```

**`scripts/daily_news.py`** 的工作流程：
1. 并行 curl 10 个新闻源到 /tmp/
2. 运行 `parse_all_sources.py` 解析所有源
3. 直接调 GLM API（绕过 Hermes agent 系统提示）格式化日报
4. 写入 `daily_news.md` + lark-cli 上传飞书
5. stdout 输出干净的用户通知（3条要闻 + 文档链接）

**关键优势**：
- stdout 完全可控（脚本精确控制输出内容）
- 无 Hermes 系统提示干扰（LLM 调用在脚本内独立进行）
- 无 cron boilerplate 的 SILENT 指令干扰
- 执行结果 100% 可预测

## 可复用的教训

### 适用场景
任何满足以下条件的 cron job 应考虑 `no_agent=true` 脚本驱动：
- `deliver` 到用户可见频道（飞书、Telegram、Discord 等）
- 模型倾向于输出技术细节/验证日志
- 对输出格式有严格要求

### 脚本驱动模式的关键要素
```python
# cron 脚本的标准结构
def main():
    # 1. 采集数据（curl/API/browser）
    # 2. 处理和推理（可调 LLM API）
    # 3. 执行副作用（写文件、上传文档、发送通知）
    # 4. print 用户消息到 stdout（这会被 cron deliver 推送）

    print("用户可见的干净消息")
    # 所有调试信息输出到 stderr
```
