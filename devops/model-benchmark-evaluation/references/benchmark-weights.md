# Benchmark Weights Reference

## D2 编程 (total 12.0)

| Benchmark | Weight | Reason |
|-----------|--------|--------|
| SWE-Bench Verified | 2.5 | 公认标准，最广泛评测 |
| SWE-Bench Pro | 2.0 | 标准高难度版 |
| LiveCodeBench | 2.0 | 竞赛编程标准 |
| Terminal Bench | 1.5 | 终端Agent编码 |
| NL2Repo | 1.0 | 代码库生成 |
| VIBE-V2 | 1.0 | Vibe编码 |
| PaperBench | 1.0 | 论文复现 |
| SVG-Bench | 0.5 | SVG生成，较专项 |
| KernelBench Hard | 0.5 | CUDA优化，极专项 |

## D3 数学 (total 7.0)

| Benchmark | Weight | Reason |
|-----------|--------|--------|
| AIME 2026 | 2.5 | 顶级竞赛，极权威 |
| IMOAnswerBench | 2.5 | IMO级别，极权威 |
| HMMT Feb 2026 | 2.0 | 高水平数学竞赛 |

## D6 指令遵循 (total 3.0)

| Benchmark | Weight | Reason |
|-----------|--------|--------|
| GDPval rubrics | 2.0 | 指令遵循标准评测 |
| SpreadSheetBench | 1.0 | 表格操作，较专项 |

## D7 工具调用 (total 11.0)

| Benchmark | Weight | Reason |
|-----------|--------|--------|
| BrowseComp | 2.0 | 浏览器Agent标准 |
| MCP Atlas | 2.0 | MCP工具调用标准 |
| Toolathlon | 2.0 | 工具调用综合评测 |
| τ²-Bench | 1.5 | Agent协作评测 |
| Claw-Eval | 1.5 | Agent评测 |
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
