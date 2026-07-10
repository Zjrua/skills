# LeetCode GraphQL API — 抓取题面

## Endpoint

```
POST https://leetcode.cn/graphql/
Content-Type: application/json
User-Agent: Mozilla/5.0 (compatible; LeetCodeBot/1.0)
```

## Query

```graphql
query questionData($titleSlug: String!) {
  question(titleSlug: $titleSlug) {
    questionId
    translatedTitle
    difficulty
    translatedContent
  }
}
```

## Slug

Extract from PROBLEMS.txt URL: `https://leetcode.cn/problems/{slug}/`

Slugs are lowercase English with hyphens (e.g. `two-sum`, `longest-consecutive-sequence`).

## Rate Limiting

LeetCode API is tolerant but returns garbled responses if hit too fast. Safe: **1.5s delay** between requests. Total time for 100 problems: ~2.5 minutes.

## urllib vs curl

**Problem**: Python's `urllib.request` returns HTTP 400 for valid queries that curl handles fine. Likely encoding/header issue with certain slugs.

**Solution**: Use `subprocess` + `curl` instead of `urllib`. The fetch_problems.py script uses this approach.

### Working curl invocation

```python
result = subprocess.run(
    ["curl", "-s", "--max-time", "15",
     "https://leetcode.cn/graphql/",
     "-H", "Content-Type: application/json",
     "-H", "User-Agent: Mozilla/5.0 (compatible; LeetCodeBot/1.0)",
     "-d", json.dumps(payload)],
    capture_output=True, text=True, timeout=20
)
```

## HTML Cleanup

`translatedContent` is HTML with tags: `<p>`, `<pre>`, `<strong>`, `<em>`, `<code>`, `<ul>`, `<li>`, `<sup>`, `<sub>`, HTML entities.

`clean_html()` in fetch_problems.py converts to markdown-like text. Some residual tags (`<span>`, `<div>`, `<b>`) may survive — they're harmless in Feishu markdown rendering.

## Output Format

Each problem → `problems/NNNN_name.md`:

```markdown
# {id}. {title}

**难度**: {difficulty}
**分类**: {category}

## 题目描述

{cleaned body}
```

## Duplicate Problems

PROBLEMS.txt has 3 duplicate LeetCode IDs: 200 (岛屿数量, lines 43 & 94), 207, 155.  
These map to 97 unique problems, not 100. The duplicates appear in different categories (e.g. 200: "搜索" vs "图论").
