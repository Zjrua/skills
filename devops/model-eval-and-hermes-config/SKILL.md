---
name: model-eval-and-hermes-config
description: "评估模型能力 + 配置 Hermes 主模型、fallback 链、辅助模型。从评测数据到配置落地的一站式工作流。自包含 benchmark-weights 和 hermes-config-quickref 参考。"
triggers:
  - 模型评估
  - 配置模型
  - fallback链
  - 模型选择
  - benchmark
  - model evaluation
  - model configuration
  - set model
  - change provider
  - configure fallback
  - 辅助模型
  - auxiliary model
---

# 模型评估与 Hermes 配置一体化

从「评测模型能力」到「配置 Hermes 主模型、fallback 链、辅助模型」的完整闭环。

**自包含打包**：本 skill 内嵌了 `references/benchmark-weights.md`（评测集权重详细参考）和 `references/hermes-config-quickref.md`（Hermes 配置速查）。拷贝整个 skill 目录即可在新环境使用，无需额外依赖。

## 工作流概览

```
收集评测数据 → 计算维度分数 → 计算 Profile 加权分 → 选择最佳模型 → 配置 Hermes
     ↓               ↓                ↓                  ↓              ↓
  9 维度基准     加权平均        6 个角色 profile     主模型 + fallback   config.yaml
```

---

## 第一步：评估模型能力

### 9 维度体系

| Dim | 名称 | 代表评测集 |
|-----|------|-----------|
| D1 | 综合能力 | MMLU-Pro (×3.0), GPQA Diamond (×2.5), Chinese SimpleQA (×2.0), SimpleQA (×1.5), HLE (×1.0) |
| D2 | 编程 | SWE-Bench Verified (×2.5), LiveCodeBench (×2.0), Terminal Bench (×1.5) |
| D3 | 数学推理 | AIME 2026 (×2.5), IMOAnswerBench (×2.5), HMMT Feb 2026 (×2.0) |
| D4 | 科学推理 | GPQA Diamond, ARC-Challenge |
| D5 | 长文本 | LongBench-V2, MRCR 1M, CorpusQA 1M |
| D6 | 指令遵循 | GDPval rubrics (×2.0), SpreadSheetBench (×1.0) |
| D7 | 工具调用 | BrowseComp (×2.0), MCP Atlas (×2.0), Toolathlon (×2.0), τ²-Bench (×1.5) |
| D8 | 中文理解 | C-Eval, CMMLU (目前数据少，暂不使用) |
| D9 | 多轮对话 | MT-Bench, AlpacaEval (目前数据少，暂不使用) |

完整评测集权重详见 `references/benchmark-weights.md`。

### 计算方法

**维度分数** = Σ(评测集分数 × 评测集权重) / Σ(权重) — 仅对有数据的评测集求和

**Profile 分数** = Σ(维度分数 × 维度权重) / Σ(权重) — 仅对有数据的维度求和

关键原则：**缺失数据不拉低分数**，权重在有数据的项之间按比例归一化。

### 6 个角色 Profile 的维度权重

| 维度 | Coder | Planner | Writer | Researcher | Reviewer | Doubter |
|------|-------|---------|--------|------------|----------|---------|
| D1 综合 | 1 | 0.5 | 1 | 2 | 2 | 2 |
| D2 编程 | 2 | 0.5 | 0 | 0 | 0.5 | 0 |
| D3 数学 | 0 | 1 | 0 | 1 | 1 | 1 |
| D5 长文本 | 1 | 0 | 1 | 1 | 1 | 1 |
| D6 指令遵循 | 1.5 | 2 | 0 | 1 | 1 | 1 |
| D7 工具调用 | 0.5 | 1 | 2 | 1 | 0.5 | 1 |

### 数据收集来源

- DeepSeek: 官方 HuggingFace 技术报告, deepseekv4.wiki
- GLM/智谱: docs.bigmodel.cn, benchlm.ai
- MiniMax: minimaxi.com/models/text/m3
- Kimi: github.com/MoonshotAI/Kimi-K2
- Qwen: 官方 GitHub benchmark 图表
- GPT/Claude/Gemini: minimaxi.com 对比表, 各官方技术报告
- 其他: benchlm.ai, Papers With Code, 各模型技术报告/ArXiv 论文

### Bitable 存储（可选）

如需持久化评测数据，可在飞书 Bitable 中建立 3 张表：

- **表 1 — 评测集原始分数**: 每列一个评测集名（如 `MMLU-Pro`, `SWE-Bench Verified`），每行一个模型
- **表 2 — Profile 加权评分**: `D1综合均值` ~ `D7工具均值` + `Coder`, `Planner`, `Writer`, `Researcher`, `Reviewer`, `Doubter`，每行一个模型
- **表 3 — 维度定义与评测集映射**: 维度名 → 评测集名 → 权重 → 数据状态（参考表）

使用 `lark-cli` 或飞书 API 操作 Bitable。首次使用时需要创建表并录入字段。

**示例表结构**（参考模板，实际使用时需创建自己的 Bitable）：

```yaml
# 示例 Bitable 配置
bitable:
  base_token: "SjdSbza4oahkF5sURFDcY47yn0f"   # 创建后替换为自己的
  tables:
    raw_scores: "tblob3Y2j2tfrHPr"               # 表1: 评测集原始分数
    profiles:   "tblGJYoefcl33VIS"                # 表2: Profile 加权评分
    dimensions: "tbl6OMC6xGHj5cI2"                # 表3: 维度定义与评测集映射
```

**Bitable 操作命令速查**：
```bash
# 创建表
lark-cli base +table-create --base-token <token> --name "表名" --as bot --format json

# 创建字段 (--json 必须, 不支持 --name/--type)
lark-cli base +field-create --base-token <token> --table-id <id> \
  --json '{"name":"字段名","type":"number"}' --as bot --format json

# 批量写入记录
cd /tmp && lark-cli base +record-batch-create --base-token <token> --table-id <id> \
  --json @./data.json --as bot --format json

# 查询记录
lark-cli api GET "/open-apis/bitable/v1/apps/<token>/tables/<id>/records" \
  --params '{"page_size":50}' --as bot
```

---

## 第二步：从评估到配置的决策框架

### Profile → 配置映射

| 角色 | 最看重的维度 | 推荐用途 |
|------|------------|---------|
| **Coder** | D2编程 > D6指令 > D1,D5 | 编写和调试代码 |
| **Planner** | D6指令 > D3,D5,D7 | 任务规划和拆解 |
| **Writer** | D7工具 > D1,D5 | 文档撰写、内容创作 |
| **Researcher** | D1,D3 > D5,D6,D7 | 深度研究、论文分析 |
| **Reviewer** | D1 > D3,D5,D6 | 代码/文档审查 |
| **Doubter** | D1,D3 > D5,D6,D7 | 红队测试、挑战假设 |

### 模型选择矩阵

根据角色需求选主模型：

1. **全能型** (所有维度 70+): 适合所有角色
2. **编码型** (D2 高): 适合 Coder
3. **推理型** (D1/D3 高): 适合 Researcher, Reviewer, Doubter
4. **性价比** (各维度 60+, 价格低): 适合日常辅助、fallback
5. **工具型** (D7 高): 适合 Writer, Planner

具体模型名称随市场变化，以评测数据为准。

---

## 第三步：配置 Hermes 主模型

### 配置路径

```bash
# 交互式选择
hermes model

# 直接设置
hermes config set model.default <model_name>
hermes config set model.provider <provider>
```

### 配置文件位置

`~/.hermes/config.yaml` — 主配置文件

```yaml
model:
  default: <your-model>        # 主模型，如 deepseek-v4-pro
  provider: <your-provider>    # 提供商，如 deepseek
  api_key: sk-xxx              # API Key（推荐放在 .env 中）
  base_url:                    # 可选，自定义端点
  context_length: 64000        # 上下文长度
```

完整 Provider 列表和环境变量名详见 `references/hermes-config-quickref.md`。

---

## 第四步：配置 Fallback 链

### Provider 三级分类

通过 `base_url` 和 provider 类型判断所属级别，不同级别有不同优先级策略：

| 级别 | 特征 | base_url 示例 | 典型场景 |
|------|------|--------------|---------|
| **A. 计费 API** | 按 token 付费，无时间窗口 | `api.deepseek.com`, `api.openai.com`, `open.bigmodel.cn` | DeepSeek, OpenAI, 智谱, Anthropic |
| **B. Coding Plan** | 包月/包时段，有调用配额 | `ark.cn-beijing.volces.com/api/coding` | 方舟 Coding Plan, 智谱 Coding Plan |
| **C. 本地模型** | 自建部署，依赖硬件 | `localhost:*`, `192.168.*`, `10.*`, ZeroTier 内网 | vLLM, llama.cpp, Ollama |

### 识别规则

```python
def classify_provider(base_url: str, provider: str) -> str:
    """通过 URL 判断 provider 级别"""
    if not base_url or any(k in base_url for k in ['api.deepseek.com', 'api.openai.com', 
        'open.bigmodel.cn', 'api.anthropic.com', 'generativelanguage.googleapis.com']):
        return 'A'  # 计费 API
    
    if '/coding/' in base_url or 'coding' in provider.lower():
        return 'B'  # Coding Plan
    
    if any(k in base_url for k in ['localhost', '127.0.0.1', '192.168.', '10.', '172.']):
        return 'C'  # 本地模型
    
    # 其他商业 API 默认为 A
    if 'api.' in base_url or '.com/' in base_url:
        return 'A'
    
    return 'C'  # 兜底为本地
```

### Fallback 优先级规则

```
主模型                    fallback 1              fallback 2（可选）
─────────────────────────────────────────────────────────────────
B (Coding Plan, 强模型) → A (计费 API, 经济版) → A (计费 API, 另一云)
A (计费 API, 强模型)    → A (计费 API, 经济版) → B (Coding Plan, 备选)
A (计费 API)            → A (另一云的计费 API)  → 不需要
C (本地模型)            → A (计费 API)          → B (Coding Plan)
```

**核心原则**：
1. **Coding Plan 做主模型** — 性价比最高时优先用，但不可靠时不要做 fallback
2. **计费 API 做 fallback** — 永远可用，按量付费
3. **本地模型不做 fallback** — 硬件不保证在线
4. **跨云冗余** — 主和 fallback 在不同云厂商上
5. **配额互补** — 有窗口限制的 + 无限制的搭配

### 配置方法

```yaml
# config.yaml 中的 fallback 配置
fallback_providers:
  - model: <fallback-model>       # 备选模型
    provider: <fallback-provider> # 备选提供商
  - model: <fallback-model-2>     # 可选第二级 fallback
    provider: <fallback-provider-2>
```

每个 Profile 有独立的 fallback 设置：`~/.hermes/profiles/<name>/config.yaml`

---

## 第五步：配置辅助模型（Auxiliary）

辅助模型处理：视觉分析、网页提取、上下文压缩、session 搜索等轻量任务。不需要最强模型，用快速便宜的即可。

```yaml
auxiliary:
  vision:
    provider: <provider>          # 视觉分析，需支持图像输入
    model: <vision-model>         # 如 gemini-2.5-flash, qwen-vl 等
  web_extract:
    provider: auto                # 网页提取（自动选择可用 provider）
  compression:
    provider: auto                # 上下文压缩
  summary:
    model: <fast-model>           # 会话摘要，便宜快速即可
    summary_provider: auto
```

辅助模型选择原则：
- **视觉**: 需要支持图像输入的模型（Qwen-VL, Gemini Flash, Claude Sonnet 等）
- **压缩/摘要**: 快速便宜的模型即可（Gemini Flash, DeepSeek Flash 等）
- **auto**: Hermes 自动选择可用的提供商

如果辅助模型任务静默失败，手动指定 provider 和 model：
```bash
hermes config set auxiliary.vision.provider <provider>
hermes config set auxiliary.vision.model <model>
```

---

## 第六步：Profile 级别配置

每个 Kanban Profile 有独立的 config.yaml：

```
~/.hermes/profiles/<name>/config.yaml
```

各 Profile 根据角色选不同模型：
- **planner** → 重 D6(指令遵循), 选综合强的模型
- **coder** → 重 D2(编程), 选代码强的模型
- **writer** → 重 D7(工具调用), 选工具使用强的模型
- **researcher** → 重 D1(综合), 选知识丰富的模型
- **reviewer** → 重 D1(综合), 选准确的模型

---

## 完整流程 Checklist

- [ ] 收集候选模型的评测数据（官方报告、第三方平台）
- [ ] （可选）在 Bitable 中录入原始分数
- [ ] 计算维度分数和 Profile 加权分
- [ ] 根据用途选择主模型
- [ ] 用 `classify_provider()` 判断 provider 级别
- [ ] 按优先级规则配置 fallback 链
- [ ] `hermes config set model.default <model>`
- [ ] 配置辅助模型（vision, compression, summary）
- [ ] 为各 Profile 配置独立模型
- [ ] `hermes doctor` 检查配置完整性
- [ ] `/model` 验证当前生效的模型

---

## Pitfalls

### ⚠️ 非百分比分数需要特殊处理
Codeforces Rating (3206)、GDPval Elo (1554) 等不在 0-100 范围内的分数，计算维度平均时必须过滤：
```python
if val is not None and val > 0 and val <= 100:
    wv += val * weight
    ws += weight
```

### ⚠️ 覆盖度阈值 — 维度 < 4/6 时排名不可靠
当模型只有 <4 个维度有数据时，加权分数因维度太少而失真。建议：
- 主排名要求 ≥ 4/6 维度有数据
- 分开排名：全数据模型 vs 部分数据模型

### ⚠️ 配置变更需重启
- 模型/提供商更改: CLI 退出重进，Gateway `/restart`
- 工具/skills: `/reset` 启动新会话
- config.yaml 直接编辑后: `hermes config check` 验证

### ⚠️ Credential Pool 策略
多 API Key 时可用 credential pool 自动轮转：
```bash
hermes auth add          # 交互式添加
hermes auth list         # 查看已有凭据
```

### ⚠️ Profile 间配置隔离
修改 default profile 不影响其他 profile。每个 profile 有独立的 `~/.hermes/profiles/<name>/config.yaml`。不要直接复制 default 的 fallback 配置到其他 profile——它们可能需要不同的模型组合。

### ⚠️ 模型名称必须验证，不可猜测
Provider API 频繁变动——模型可能被重命名、弃用或替换。配置前必须用 API 验证：
```bash
source ~/.hermes/.env
curl -s <provider-base-url>/models -H "Authorization: Bearer *** | python3 -m json.tool
```
常见错误：`deepseek-chat` → 不存在，实际为 `deepseek-v4-flash` / `deepseek-v4-pro`。

### ⚠️ /models 列表可能不完整——新模型需用 chat 接口实测
`/models` 端点有时不会列出最新上线的模型。如果怀疑某模型已上线但列表里没有，直接发一个 chat completions 请求验证：
```bash
curl -s <base_url>/chat/completions \
  -H "Authorization: Bearer ***  -H "Content-Type: application/json" \
  -d '{"model":"glm-5.2","messages":[{"role":"user","content":"hi"}],"max_tokens":10}'
```
如果返回正常响应（`"model":"glm-5.2"` in response），说明模型可用，即使 `/models` 没列出来。实际案例：glm-5.2 上线后 `/models` 仍只有到 glm-5.1，但 chat 接口已可用。

### ⚠️ 切换主模型 Provider 时清理残留字段
`model` 段中的 `api_key`、`base_url` 属于之前的 provider。切换到 `custom:<name>` 后，这些字段应移除——凭据由 `custom_providers` 段提供，model 段只保留 `default`、`provider`、`context_length`。残留旧字段可能导致认证冲突。

### ⚠️ Bitable 字段名必须精确匹配
`+record-batch-create` 中的字段名必须与已有字段完全一致。"D1综合" 不会匹配 "D1综合均值"。操作前先用 `+field-list` 检查。

### ⚠️ Coding Plan 配额窗口
Coding Plan 通常有时间窗口（如每日 5 小时高峰窗口）。窗口用完后 API 会 429。确保 fallback 是无限制的计费 API。

### ⚠️ lark-cli base +field-create 必须用 --json
`--name` 和 `--type` 不存在，必须 `--json '{"name":"字段名","type":"number"}'`。

### ⚠️ --json @file 需要相对路径
`--json @./data.json` 配合 `cd /tmp` 作为 workdir。绝对路径会被拒绝。
