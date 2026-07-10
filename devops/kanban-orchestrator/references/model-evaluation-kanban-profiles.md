# Multi-Agent Kanban Profile Model Selection (2026-05-27)

Data-driven model selection for kanban profiles using benchmark scores.

## Evaluated Models (API-verified names)

| Provider | Model | API Endpoint | Cost |
|----------|-------|-------------|------|
| zai (智谱) | `glm-5.1` | `open.bigmodel.cn/api/coding/paas/v4` | Coding plan (5h quota) |
| zai (智谱) | `glm-5-turbo` | same | Same plan |
| deepseek | `deepseek-v4-flash` | `api.deepseek.com/v1` | Per-token (cheap) |
| deepseek | `deepseek-v4-pro` | same | Per-token (expensive) |

**API verification command**: `curl -s <base_url>/models -H "Authorization: Bearer <key>"`

## Benchmark Scores (from BenchLM.ai, official docs, deepseekv4.wiki)

### GLM-5.1 (9/9 dimensions — most complete data)
| Dimension | Score | Source |
|-----------|-------|--------|
| Overall | 82 | BenchLM |
| Coding | 83.4 | BenchLM |
| Math | 89.7 | BenchLM |
| Knowledge | 84.4 | BenchLM |
| Agentic | 80.4 | BenchLM |
| Instruction Following | 91.7 | BenchLM |
| MMLU-Pro | 86.0 | deepseekv4.wiki |
| GPQA Diamond | 86.2 | deepseekv4.wiki |
| SWE-Bench Pro | 58.4 | 智谱官方 |
| Arena Elo | 1472 | BenchLM |

### DeepSeek-V4-Pro (7/9 dimensions)
| Dimension | Score | Source |
|-----------|-------|--------|
| MMLU | 89.7 | 腾讯云/官方报告 |
| GSM8K | 92.4 | 腾讯云/官方报告 |
| HumanEval | 85.2 | 腾讯云/官方报告 |
| GPQA Diamond | 90.1 | deepseekv4.wiki |
| LiveCodeBench | 93.5 | deepseekv4.wiki |
| Codeforces Rating | 3206 | deepseekv4.wiki |
| AgentBench | 76.8 | 腾讯云/官方报告 |
| MMLU-Pro | 87.5 | deepseekv4.wiki |

### DeepSeek-V4-Flash (6/9 dimensions)
| Dimension | Score | Source |
|-----------|-------|--------|
| MMLU | 82.1 | 腾讯云/官方报告 |
| GSM8K | 85.6 | 腾讯云/官方报告 |
| HumanEval | 76.8 | 腾讯云/官方报告 |
| MMLU (Base) | 88.7 | deepseekv4.wiki |
| MATH (Base) | 57.4 | deepseekv4.wiki |
| AgentBench | 68.5 | 腾讯云/官方报告 |

### GLM-5-Turbo — Insufficient data (closed-source, only Arena Elo 1456)

## Profile × Model Recommendations

| Profile | Best | Runner-up | Best for (reason) |
|---------|------|-----------|-------------------|
| Coder | DS-V4-Pro (84.5) | GLM-5.1 (84.1) | Coding + Agent strongest |
| Planner | GLM-5.1 (84.7) | DS-V4-Pro (84.5) | Data-complete, instruction following |
| Writer | GLM-5.1 (82.0) | DS-V4-Pro (77.0) | Chinese + instruction following |
| Researcher | GLM-5.1 (80.8) | DS-V4-Pro (78.4) | Data-complete, agentic |
| Reviewer | DS-V4-Pro (86.1) | GLM-5.1 (84.6) | Coding + reasoning |
| Doubter | DS-V4-Pro (85.8) | GLM-5.1 (84.8) | Math + science reasoning |

## Cost-Optimized Production Config

```
coder:      zai/glm-5.1 → deepseek/deepseek-v4-flash    (zai coding plan limited)
planner:    deepseek/deepseek-v4-flash → zai/glm-5-turbo (planning isn't demanding)
writer:     deepseek/deepseek-v4-flash → zai/glm-5-turbo
researcher: deepseek/deepseek-v4-flash → zai/glm-5-turbo
reviewer:   deepseek/deepseek-v4-flash → zai/glm-5-turbo
doubter:    deepseek/deepseek-v4-flash → zai/glm-5-turbo
```

Fallback principle: zai ↔ deepseek cross-cloud redundancy. omlx (local Mac) excluded from fallback chain (unreliable uptime).

## Key Data Sources
- BenchLM.ai: https://benchlm.ai/models/glm-5-1
- DeepSeek V4 Wiki: https://deepseekv4.wiki/
- 智谱官方: https://docs.bigmodel.cn/cn/guide/models/text/glm-5.1
- 腾讯云解析: https://cloud.tencent.com/developer/article/2663824
- DeepSeek官方PDF: https://huggingface.co/deepseek-ai/DeepSeek-V4-Pro/blob/main/DeepSeek_V4.pdf
