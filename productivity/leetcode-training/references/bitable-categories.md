# Bitable 分类映射

PROBLEMS.txt 中的分类名和多维表格中的选项名不完全一致，写入前必须映射。

## 允许的分类值（21个）

BFS, 二分查找, 二叉树, 位运算, 前缀和, 动态规划, 双指针, 哈希表, 回溯, 图论, 堆, 字典树, 投票法, 拓扑排序, 排序, 栈, 滑动窗口, 矩阵, 设计, 贪心, 链表

## 映射表

| PROBLEMS.txt 原始值 | → 多维表格值 |
|---------------------|-------------|
| 二分 | 二分查找 |
| 二叉搜索树 | 二叉树 |
| 动态规划/栈 | 动态规划 |
| 单调栈 | 栈 |
| 单调队列 | 堆 |
| 双指针/栈 | 双指针 |
| 搜索 | 图论 |
| 数组 | 双指针 |
| 贪心/DP | 贪心 |
| 链表/堆 | 链表 |

## PROBLEMS.txt 中用 `/` 分隔的分类

如"双指针/栈"、"动态规划/栈"、"链表/堆"等，需要拆成多个标签写入 multi_select 字段。

## Bitable API 踩坑

- `+record-batch-create` 的 JSON 格式是 `{"fields": ["字段1","字段2"], "rows": [["值1","值2"], ...]}`，不是 `{"records": [{"fields": {...}}]}`。
- `+record-batch-update` 的 JSON 格式是 `{"record_id_list": ["recXXX"], "patch": {"字段": "值"}}`，同一个 patch 应用到所有记录。
- 日期字段值为毫秒时间戳：`int(datetime.strptime("2026-05-28", "%Y-%m-%d").timestamp()) * 1000`
- **URL 字段（type=15）**：必须用原始 API 创建（`+field-create` 会错误创建 text 字段）。写入时直接传纯字符串 `{"LeetCode": "https://..."}`，会自动识别为可点击链接。
- **multi_select 字段（type=4）**：`+field-create` 的 `{"type":"multi_select"}` 会错误创建 single_select！必须用原始 API + `type: 4`，创建后验证 `"multiple": true`。
- 删除字段会同时删除该字段的所有数据，迁移字段类型时必须先创建新字段、复制数据、再删旧字段。
