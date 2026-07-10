# 模型评测多维表格设计参考

> 2026-06-08 实战总结：为 7+ 个 LLM 模型建立评测分数 Bitable。

## 项目资源

- **多维表格**: base_token=`SjdSbza4oahkF5sURFDcY47yn0f` → https://my.feishu.cn/base/SjdSbza4oahkF5sURFDcY47yn0f
  - 评测集分数表: 每列一个具体评测集（SWE-Bench Verified、BrowseComp 等）
  - Profile加权评分表: 按 Agent Profile (Coder/Planner/Writer/Researcher/Reviewer/Doubter) 加权
- **飞书文档**: doc_token=`V7S8dNHmYo89aDxF1URcg9Hsnmc` → https://www.feishu.cn/docx/V7S8dNHmYo89aDxF1URcg9Hsnmc

## 表结构设计原则

### ⚠️ 透明性第一：列名必须是具体评测集名

用户明确反馈：**各项目的分数对应哪个评测集不够透明**。

**❌ 错误做法**：用聚合维度名（D1综合、D2编程）作为列名，把具体评测集藏在备注里。

**✅ 正确做法**：每个评测集单独一列，列名就是评测集名：
```
| 模型 | SWE-Bench Verified | SWE-Bench Pro | BrowseComp | MMLU | ... |
```

加权评分可以另建一表，但原始分数表必须让人一眼看出"这个分数来自哪个评测集"。

### 推荐表结构

**表1: 评测集原始分数**
- 每列 = 一个具体评测集
- null/空 表示该模型未做该评测
- 最后一列"数据来源"标注 URL

**表2: Profile 加权评分**
- 每列 = 一个 Agent Profile (Coder, Planner, ...)
- 基于表1的评测集均值按维度加权
- 缺失维度自动归一化（按已有维度权重重新分配）

## 加权评分方法论

### 缺失数据处理

不是所有模型都做了相同的评测集。处理方式：

1. 将评测集映射到能力维度（D1综合、D2编程、...）
2. 每个维度取该维度下所有评测集的**均值**
3. 加权求和时，缺失维度的权重**按比例分配到已有维度**
4. 公式：`score = Σ(dim_avg × weight) / Σ(weight_of_covered_dims)`

### 权重矩阵（6 Profile × 9 维度）

| 维度 | Coder | Planner | Writer | Researcher | Reviewer | Doubter |
|------|-------|---------|--------|------------|----------|---------|
| 综合能力 | 15% | 25% | 20% | 20% | 20% | 20% |
| 编程 | 30% | 8% | 5% | 2% | 25% | 5% |
| 数学推理 | 5% | 10% | 5% | 8% | 10% | 20% |
| 科学推理 | 3% | 5% | 3% | 10% | 10% | 20% |
| 长文本 | 1% | 2% | 15% | 15% | 3% | 4% |
| 指令遵循 | 15% | 20% | 15% | 5% | 15% | 10% |
| 工具调用 | 20% | 15% | 2% | 25% | 5% | 8% |
| 中文理解 | 10% | 10% | 25% | 10% | 10% | 10% |
| 多轮对话 | 1% | 5% | 10% | 5% | 2% | 3% |

## 数据来源

- BenchLM.ai: 类别聚合分（Coding/Reasoning/Knowledge/Math/IF）
- 官方 GitHub/技术报告: Kimi K2 (arXiv:2507.20534), DeepSeek V4
- 第三方: deepseekv4.wiki, 腾讯云开发者社区
- 官网对比表: minimaxi.com (MiniMax M3 vs Opus 4.7 vs GPT 5.5 vs Gemini 3.1 Pro)
