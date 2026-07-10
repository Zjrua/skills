---
name: model-benchmark-evaluation
description: "Collect model benchmark scores, map to capability dimensions, compute weighted scores per Agent profile, publish to Feishu Bitable."
triggers:
  - model evaluation
  - benchmark
  - 模型评测
  - 评测集
  - 模型对比
  - model comparison
  - weighted scoring
---

# Model Benchmark Evaluation System

Collect benchmark scores for LLMs, map them to 9 capability dimensions, compute weighted scores for 6 Agent profiles, and publish results to Feishu Bitable.

## Overview

Two-layer weighted normalization:

**Layer 1: Benchmarks → Dimension scores**
- Each benchmark maps to one of 9 dimensions (D1-D9)
- Benchmarks have intra-dimension weights (e.g., SWE-Bench Verified ×2.5 vs KernelBench ×0.5)
- Dimension score = Σ(benchmark_score × benchmark_weight) / Σ(benchmark_weight) for available benchmarks only

**Layer 2: Dimension scores → Profile weighted scores**
- 6 profiles: Coder, Planner, Writer, Researcher, Reviewer, Doubter
- Each profile has weights for 9 dimensions (totaling 100%)
- Profile score = Σ(dim_score × dim_weight) / Σ(dim_weight) for available dimensions only

**Key principle**: Missing data does NOT lower scores. Weights are normalized proportionally among available items. Relative weight ratios are always preserved.

## 9 Capability Dimensions

| Dim | Name | Representative Benchmarks |
|-----|------|--------------------------|
| D1 | 综合能力 | MMLU-Pro (30%), GPQA Diamond (25%), Chinese SimpleQA (20%), SimpleQA (15%), HLE (10%) |
| D2 | 编程 | SWE-Bench Verified/Pro, LiveCodeBench, Terminal Bench, NL2Repo, VIBE-V2, SVG-Bench, KernelBench |
| D3 | 数学推理 | AIME 2026, HMMT Feb 2026, IMOAnswerBench |
| D4 | 科学推理 | GPQA Diamond (also D1), ARC-Challenge |
| D5 | 长文本 | LongBench-V2, MRCR 1M, CorpusQA 1M |
| D6 | 指令遵循 | IFEval, GDPval rubrics, SpreadSheetBench |
| D7 | 工具调用/Agent | BrowseComp, MCP Atlas, Toolathlon, τ²-Bench, Claw-Eval, OSWorld, CyberGym |
| D8 | 中文理解 | C-Eval, CMMLU, Chinese SimpleQA |
| D9 | 多轮对话 | MT-Bench, AlpacaEval |

## Intra-Dimension Benchmark Weights

Weights reflect authority × representativeness × generality.

**D1 综合能力** (total 10.0, 低分评测集低权重保留):
- ×3.0: MMLU-Pro (经典权威基准)
- ×2.5: GPQA Diamond (博士级科学推理)
- ×2.0: Chinese SimpleQA (中文事实问答)
- ×1.5: SimpleQA (事实性验证)
- ×1.0: HLE (极难前沿挑战，象征性保留)

**D2 编程** (total 12.0):
- ×2.5: SWE-Bench Verified (公认标准)
- ×2.0: SWE-Bench Pro, LiveCodeBench
- ×1.5: Terminal Bench
- ×1.0: NL2Repo, VIBE-V2, PaperBench
- ×0.5: SVG-Bench, KernelBench Hard (极专项)

**D3 数学** (total 7.0):
- ×2.5: AIME 2026, IMOAnswerBench (顶级竞赛)
- ×2.0: HMMT Feb 2026

**D6 指令遵循** (total 3.0):
- ×2.0: GDPval rubrics
- ×1.0: SpreadSheetBench

**D7 工具调用** (total 11.0):
- ×2.0: BrowseComp, MCP Atlas, Toolathlon
- ×1.5: τ²-Bench, Claw-Eval
- ×1.0: OSWorld-verified
- ×0.5: CyberGym, BankerToolBench

## Profile Weights (D1-D7, normalized at runtime)

Weights are stored as integers, normalized proportionally among available dimensions at calculation time. D8/D9 have no data and are not used.

| Dimension | Coder | Planner | Writer | Researcher | Reviewer | Doubter |
|-----------|-------|---------|--------|------------|----------|---------|
| D1 综合 | 1 | 0.5 | 1 | 2 | 2 | 2 |
| D2 编程 | 2 | 0.5 | 0 | 0 | 0.5 | 0 |
| D3 数学 | 0 | 1 | 0 | 1 | 1 | 1 |
| D5 长文本 | 1 | 0 | 1 | 1 | 1 | 1 |
| D6 指令遵循 | 1.5 | 2 | 0 | 1 | 1 | 1 |
| D7 工具调用 | 0.5 | 1 | 2 | 1 | 0.5 | 1 |

## Feishu Bitable

- **Base token**: `SjdSbza4oahkF5sURFDcY47yn0f`
- **URL**: https://my.feishu.cn/base/SjdSbza4oahkF5sURFDcY47yn0f
- **Table 1**: `tblob3Y2j2tfrHPr` — "评测集原始分数" — each column is a specific benchmark name (not aggregated dimension). ~53 fields including new benchmarks from MiniMax M3 release (IMO 2025, USAMO 2026, DRACO, OmniDocBench, MMMU-Pro, etc.)
- **Table 2**: `tblGJYoefcl33VIS` — "Profile加权评分" — weighted scores per profile + D1-D7 dimension averages (18 models). Fields: `D1综合均值`, `D2编程均值`, `D3数学均值`, `D5长文本均值`, `D6指令均值`, `D7工具均值`, `Coder`, `Planner`, `Writer`, `Researcher`, `Reviewer`, `Doubter`, `平均分`
- **Table 3**: `tbl6OMC6xGHj5cI2` — "维度定义与评测集映射" — reference table: dimension → benchmark → weight → data status

## Feishu Document

- **Doc token**: `V7S8dNHmYo89aDxF1URcg9Hsnmc`
- **URL**: https://www.feishu.cn/docx/V7S8dNHmYo89aDxF1URcg9Hsnmc
- **Content**: Raw score matrix, weight system, weighted scores, coverage analysis, conclusions

## Data Collection Workflow

1. **Search for benchmark data**: Use web_search for "model_name benchmark MMLU HumanEval" etc.
2. **Check official sources**: GitHub repos, official blog posts, technical reports
3. **Check aggregator sites**: benchlm.ai, deepseekv4.wiki, minimaxi.com
4. **Cross-reference**: Compare scores across sources for consistency
5. **Note source type**: 官方 / 第三方评测平台 / 第三方社区

### Common data sources by model family
- **DeepSeek**: deepseekv4.wiki, 官方 HuggingFace 技术报告, minimaxi.com 对比表
- **GLM/智谱**: docs.bigmodel.cn, benchlm.ai, 智谱官方基准测试表（Image: img_cfeec208fc2f.jpg）
- **MiniMax**: minimaxi.com/models/text/m3, minimaxi.com/blog/minimax-m3
- **Kimi**: github.com/MoonshotAI/Kimi-K2 (arXiv:2507.20534)
- **MiMo/小米**: 官方 benchmark 图表（Image: img_39d8021f45ae.jpg）
- **Doubao/豆包**: 闭源，无公开数据
- **Gemini/GPT/Claude**: minimaxi.com 对比表, DeepSeek 官方基准测试表（Image: img_b35f85a64856.jpg）
- **Qwen**: 智谱官方基准测试表（作为对比模型出现）

## Bitable Operations (lark-cli)

### Create table
```bash
lark-cli base +table-create --base-token <token> --name "表名" --as bot --format json
```

### Create field (--json required, not --name/--type)
```bash
lark-cli base +field-create --base-token <token> --table-id <id> --json '{"name":"字段名","type":"number"}' --as bot --format json
```

### Batch insert records
```bash
# Write JSON to temp file, use relative path
cd /tmp && lark-cli base +record-batch-create --base-token <token> --table-id <id> --json @./data.json --as bot --format json
```

### Find record IDs for updates
```bash
lark-cli api GET "/open-apis/bitable/v1/apps/<token>/tables/<id>/records" --params '{"page_size":50}' --as bot
```

### Update record
```bash
lark-cli base +record-upsert --base-token <token> --table-id <id> --record-id <rec_id> --json '{"field":"value"}' --as bot --format json
```

### Delete table (--yes required)
```bash
lark-cli base +table-delete --base-token <token> --table-id <id> --as bot --yes
```

## Pitfalls

### ⚠️ lark-cli base +field-create requires --json, not --name/--type
Use `--json '{"name":"FieldName","type":"number"}'`. The `--name` and `--type` flags don't exist for this command.

### ⚠️ --json @file requires relative path and matching workdir
`--json @./data.json` with `cd /tmp` as workdir. Absolute paths like `@/tmp/data.json` are rejected.

### ⚠️ Table delete requires --yes flag
Without `--yes`, the command returns "confirmation_required" error.

### ⚠️ Search for record IDs: use API directly
`lark-cli base +record-search` may not return record_id in all formats. Use `lark-cli api GET .../records` for reliable record_id extraction.

### ⚠️ Benchmark data availability varies wildly
- Closed-source models (Doubao, MiniMax older versions) often have zero public benchmarks
- Some models only report on curated subsets (e.g., MiniMax M3 focuses on coding/agent benchmarks)
- Cross-model comparison requires finding overlapping benchmarks
- D8 中文 and D9 多轮 data is almost universally missing

### ⚠️ Non-percentage scores need special handling
- Codeforces Rating (e.g., 3206) is not on 0-100 scale
- GDPval-AA Elo scores (e.g., 1554) are not percentages
- YC-Bench uses monetary values ($5,634.41)
- Filter these out when computing dimension averages (threshold: > 200 = not percentage)

### ⚠️ Feishu LaTeX doesn't render
Feishu messages don't support `$$...$$` or `$...$` LaTeX. Use plain text/ASCII for formulas:
`D_k = Σ(score × weight) / Σ(weight)` instead of LaTeX.

### ⚠️ Bitable field names must match exactly
When using `+record-batch-create`, field names in JSON must exactly match existing names. "D1综合" won't match "D1综合均值". Always check with `+field-list` first.

### ⚠️ Record-list field order is NOT creation order
`+record-list --format json` returns fields in Bitable's internal order (alphabetical by field ID). Use `--format markdown` to see actual field→column mapping, or use raw API for record_id extraction.

### ⚠️ Deleting all records reliably
`+record-batch-delete` with all IDs sometimes returns 0 deleted silently. Safer: get IDs via `lark-cli api GET .../records`, then delete one by one via `DELETE .../records/{id}`. Alternatively, delete and recreate the entire table.

### ⚠️ MiniMax M3 data characteristics
MiniMax M3's official page (minimaxi.com) has a comprehensive cross-model comparison table covering D2/D6/D7 heavily. Traditional academic benchmarks (MMLU-Pro, AIME 2026, MRCR 1M) are NOT publicly disclosed for M3. M3 also reports IMO 2025 (35/42=83.3%) and USAMO 2026 (36/42=85.7%) which are NOT in D3 (D3 uses AIME 2026/HMMT/IMOAnswerBench).

### ⚠️ Chinese SimpleQA moved from D8 to D1
Chinese SimpleQA was originally in D8 (中文理解) but D8 had only one benchmark. It has been moved to D1 (综合能力) with weight 2.0 to broaden D1 beyond MMLU-Pro/GPQA. D8 is now empty/unused.

### ⚠️ Coverage threshold — models with <4/6 dimensions produce unreliable rankings
When a model has data in fewer than 4 of 6 dimensions (D1-D7, excluding D4), its weighted scores become unreliable because too few dimensions participate in the calculation. GPT 5.5 with only D2=82.9 ranked #1 (82.9) because all other dimensions were missing. Consider:
- Minimum coverage threshold: 4/6 dimensions required for main ranking
- Or separate rankings: full-data models vs partial-data models
- Always display dimension count alongside scores (e.g., "75.2 (6/6)")

### ⚠️ Non-percentage scores must be filtered with val <= 100
When computing dimension averages, filter out values > 100 that are clearly not percentages. Codeforces Rating (3206), GDPval-AA Elo (1554), YC-Bench ($2.1M) will explode dimension scores if not filtered:
```python
if val is not None and val > 0 and val <= 100:  # filter garbage
    wv += val * weight
    ws += weight
```

### ⚠️ Profile table dimension field names
The Profile table uses specific Chinese field names for each dimension. When updating via API, these must match exactly:
- D1 → `D1综合均值`, D2 → `D2编程均值`, D3 → `D3数学均值`
- D5 → `D5长文本均值`, D6 → `D6指令均值`, D7 → `D7工具均值`
- Passing `None` for a dimension field clears its old value (important when removing stale data)

### ⚠️ New models from MiniMax M3 release image (June 2026)
The cross-model comparison image from MiniMax M3 release added these models with D2/D6/D7 data but typically missing D1/D3/D5:
- Claude Opus 4.7, GPT 5.5, Claude Sonnet 4.6, GLM 5.1 Thinking
- These models need D1/D3/D5 data from other sources before full ranking is meaningful

### ⚠️ 低分评测集的权重策略
当评测集普遍分数很低（如 HLE 28-44 分），不应排除，而应给低权重保留。理由：低分说明 AI 在该方面有待突破，保留但降权既全面又合理。D1 中 HLE 权重仅 10%，不会过度拉低整体分数。

### ⚠️ D1 从 2 个评测集扩展到 5 个后的分数变化
D1 原来只用 MMLU-Pro + GPQA Diamond（均值 ~88 分），扩展到 5 个评测集后，由于 HLE（28-44）和 SimpleQA（34-76）的加入，D1 整体下降约 10-16 分。这是正常的，因为现在 D1 更全面地反映了模型的综合能力。

### ⚠️ Bitable 字段名可能在不同表之间不一致
评测集原始分数表和 Profile 加权评分表中，同一维度可能使用不同字段名：
- 原始分数表：无 D1 字段（D1 需从多个评测集实时计算），评测集直接用原始列名（如 `MMLU-Pro`）
- Profile 表：`D1综合均值`, `D2编程均值`, `D3数学均值`, `D5长文本均值`, `D6指令均值`, `D7工具均值`
- Profile 表的 Profile 名称：`Coder`, `Planner`, `Writer`, `Researcher`, `Reviewer`, `Doubter`

### ⚠️ Adding new benchmarks requires creating Bitable fields first
New benchmark columns (e.g., `IMO 2025`, `USAMO 2026`, `DRACO`) must be created in the scores table before writing records, otherwise `FieldNameNotFound` error or silent empty response:
```bash
lark-cli api POST "/open-apis/bitable/v1/apps/$BASE/tables/$TABLE/fields" \
  --data '{"field_name":"IMO 2025","type":2,"property":{"formatter":"0.0"}}'
```

### ⚠️ Doubao Seed models completely opaque
字节跳动闭源模型（doubao-seed-2-0, doubao-seed-1-6）未发布技术报告或评测分数，无法定量比较。
