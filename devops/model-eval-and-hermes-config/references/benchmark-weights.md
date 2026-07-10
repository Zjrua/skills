# Benchmark Weights Reference

评测集的详细权重设定。主 SKILL.md 中有概览，这里列出全部维度。

## D1 综合能力 (total 10.0)

| Benchmark | Weight | Reason |
|-----------|--------|--------|
| MMLU-Pro | 3.0 | 经典权威基准，最广泛使用 |
| GPQA Diamond | 2.5 | 博士级科学推理 |
| Chinese SimpleQA | 2.0 | 中文事实问答 |
| SimpleQA | 1.5 | 事实性验证 |
| HLE | 1.0 | 极难前沿挑战，低权重保留 |

## D2 编程 (total 12.0)

| Benchmark | Weight | Reason |
|-----------|--------|--------|
| SWE-Bench Verified | 2.5 | 公认标准，最广泛评测 |
| SWE-Bench Pro | 2.0 | 标准高难度版 |
| LiveCodeBench | 2.0 | 竞赛编程标准 |
| Terminal Bench | 1.5 | 终端 Agent 编码 |
| NL2Repo | 1.0 | 代码库生成 |
| VIBE-V2 | 1.0 | Vibe 编码 |
| PaperBench | 1.0 | 论文复现 |
| SVG-Bench | 0.5 | SVG 生成，较专项 |
| KernelBench Hard | 0.5 | CUDA 优化，极专项 |

## D3 数学推理 (total 7.0)

| Benchmark | Weight | Reason |
|-----------|--------|--------|
| AIME 2026 | 2.5 | 顶级竞赛，极权威 |
| IMOAnswerBench | 2.5 | IMO 级别，极权威 |
| HMMT Feb 2026 | 2.0 | 高水平数学竞赛 |

## D5 长文本

| Benchmark | Weight | Reason |
|-----------|--------|--------|
| LongBench-V2 | 2.0 | 长文本综合评测 |
| MRCR 1M | 1.5 | 100 万 token 上下文 |
| CorpusQA 1M | 1.5 | 大语料库问答 |

## D6 指令遵循 (total 3.0)

| Benchmark | Weight | Reason |
|-----------|--------|--------|
| GDPval rubrics | 2.0 | 指令遵循标准评测 |
| SpreadSheetBench | 1.0 | 表格操作，较专项 |

## D7 工具调用/Agent (total 11.0)

| Benchmark | Weight | Reason |
|-----------|--------|--------|
| BrowseComp | 2.0 | 浏览器 Agent 标准 |
| MCP Atlas | 2.0 | MCP 工具调用标准 |
| Toolathlon | 2.0 | 工具调用综合评测 |
| τ²-Bench | 1.5 | Agent 协作评测 |
| Claw-Eval | 1.5 | Agent 评测 |
| OSWorld-verified | 1.0 | GUI/OS Agent |
| CyberGym | 0.5 | 网络安全，较专项 |
| BankerToolBench | 0.5 | 银行工具，极专项 |

## Weight Tuning Guidelines

- **Standard/widely-tested benchmarks** get ×2.0-2.5 (SWE-Bench, AIME, BrowseComp)
- **Specialized but representative** get ×1.0-1.5 (Terminal Bench, NL2Repo)
- **Very specialized/niche** get ×0.5 (KernelBench CUDA, CyberGym)
- When a new benchmark appears, place it relative to existing ones
- Total per dimension doesn't matter (normalization handles it)
- Relative ratios matter: SWE-Bench Verified should always be 5× KernelBench

## Pitfalls

### ⚠️ 低分评测集的权重策略
当评测集普遍分数很低（如 HLE 28-44 分），不应排除，而应给低权重保留。理由：低分说明 AI 在该方面有待突破，保留但降权既全面又合理。

### ⚠️ D1 扩展后的分数变化
D1 从 MMLU-Pro + GPQA Diamond 扩展到 5 个评测集后，由于 HLE（28-44）和 SimpleQA（34-76）的加入，D1 整体下降约 10-16 分。这是正常的。

### ⚠️ 非百分比分数过滤
Codeforces Rating (3206)、GDPval Elo (1554)、YC-Bench ($5,634.41) 不在 0-100 范围。计算时必须过滤 `val > 100` 的值。

### ⚠️ Chinese SimpleQA 从 D8 移到 D1
Chinese SimpleQA 原来在 D8（中文理解），但 D8 只有一个评测集。已移到 D1（综合能力），D8 暂空。
