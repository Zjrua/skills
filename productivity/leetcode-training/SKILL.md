---
name: leetcode-training
description: Manage LeetCode Hot 100 training plan — push problems, track progress, write and test solutions in Python.
triggers:
  - leetcode
  - 刷题
  - hot 100
  - algorithm practice
  - 数据结构
  - 算法
---

# LeetCode Hot 100 Training Plan — 闪击战 (Blitz Mode)

Zjrua's daily algorithm training system for interview prep. **5 problems/day blitz**, ~20 days to finish Hot 100. Python language.

## 飞书文档 & 多维表格

- **题解文档**: `EZfodeviXosNJLxuZWFcKCwonyg` → https://my.feishu.cn/docx/EZfodeviXosNJLxuZWFcKCwonyg （做完题后用 `docs +update --command append` 追加：题意+数据规格+示例+思路+复杂度+代码）
- **进度多维表格**: base_token=`S2iLbvRetaPEiXsDOsQcWhBHnyd` → https://my.feishu.cn/base/S2iLbvRetaPEiXsDOsQcWhBHnyd
  - **刷题进度表** `tblgIezE2dgQ7ntK`：序号、题号、题名、难度、**标签(multi_select)**、状态、完成日期、备注
  - 标签是多选字段，一个题可以有多个分类（如"图论"+"搜索"）
  - 仪表盘需要用户手动在 UI 创建（API 不支持）

做完一道题后同步更新：
1. **题解文档**：用 `lark-cli docs +update --command append` 追加新题内容
2. **多维表格**：用 `+record-upsert` 更新对应记录的状态为"✅ 已完成"

## User Preferences (MUST follow)

- **Include data constraints when pushing problems** — must show `n` range, value range, etc. so user can judge time complexity.
- **No hints or tags** — only give problem title + description + constraints. User will ask for hints if needed.
- **Spread problems across the day** — do NOT push all 5 in one message. User explicitly corrected this: "你别都堆在早上呗，分散开". Space them out with reviews in between.
- **LeetCode standard code format** — ALL code files MUST use `class Solution:` with `self` parameter, matching LeetCode's submission format. Test functions use `Solution().method()`. Example:
  ```python
  class Solution:
      def moveZeroes(self, nums: List[int]) -> None:
          ...
  
  def test():
      s = Solution()
      s.moveZeroes(a)
  ```
  Do NOT write standalone functions like `def moveZeroes(nums):` — they work locally but can't be submitted to LeetCode.
- User describes algorithm logic in natural language → agent writes code → test → mark complete.
- Competitive programming background (C++), refreshing skills for internship interviews.
- **No hints or tags when presenting problems** — user explicitly said "不要给我提示和题目的标签，只给我题干，我想不出来问你再给提示". Only give the problem statement + examples. If user asks for a hint, give one hint at a time.
- **Show full code on request** — user wants to see complete code (including tests) when they ask "给我看看代码". Don't summarize.
- **Step-by-step example walkthrough** — after solving, walk through the example input step by step in a table showing pointer positions, array state, and decisions made. User finds this very helpful for understanding.
- **Validate user's approach by testing** — when user proposes an algorithm, implement it and run tests. If it fails, trace through the failing test case step by step to show exactly where the logic breaks, then suggest the fix. Don't just say "this won't work" — show WHY with a concrete example.

## Project Structure

```
/root/projects/leetcode-hot100/
├── PROGRESS.md       # Progress tracker (markdown table)
├── PROBLEMS.txt      # Master problem index (pipe-delimited, 100 problems)
├── STATE.json        # Daily push offset tracker (auto-reset at midnight)
├── problems/         # Problem descriptions (markdown, NNNN_name.md)
│   ├── 0001_two_sum.md           # Full description: title, examples, constraints
│   └── ...                       # 97 files, fetched from LeetCode GraphQL API
├── code/             # Runnable Python solutions with inline tests
│   └── 0001_two_sum.py
├── notes/            # Post-solve notes (insights, pitfalls, extensions)
└── scripts/
    ├── push_new.py       # Core: push N new problems with FULL problem descriptions
    ├── push_review.py    # Core: spaced-repetition review
    ├── push_summary.py   # Core: daily progress report
    ├── fetch_problems.py # Utility: batch-fetch problem descriptions via LeetCode GraphQL API
    ├── run_morning1.py   # Wrapper: 1 new problem (09:00)
    ├── run_morning2.py   # Wrapper: 1 new problem (11:00)
    ├── run_noon_review.py  # Wrapper: review
    ├── run_afternoon.py    # Wrapper: 1 new problem (15:00)
    ├── run_eve_push1.py    # Wrapper: 1 new problem (17:00)
│   ├── run_eve_push2.py    # Wrapper: 1 new problem (19:00)
│   ├── run_eve_review.py   # Wrapper: review (17:00)
│   └── run_eve_summary.py  # Wrapper: summary
│   └── gen_doc.py           # Generate full 题解文档 from problems/ + code/ + PROGRESS.md
```



## Cron Job Chain (7 jobs, 1题/次 + 完整题面)

```
09:00  ⚡ 早题① (1题+题面)
11:00  ⚡ 早题② (1题+题面)
13:00  🔄 午间复习
15:00  ⚡ 午题   (1题+题面)
17:00  ⚡ 晚题① (1题+题面)
19:00  ⚡ 晚题② (1题+题面)
20:00  🌙 今日战报
```

**核心改动**: 用户要求每道题附完整题面 + 一道一道推（不批量）。

| Time | Job Name | Wrapper Script | Job ID | Purpose |
|------|----------|----------------|--------|---------|
| 09:00 | LC100 ⚡ 早题① (1题) | `scripts/run_morning1.py` | `de97613c7576` | 今日第1题 + 完整题面 |
| 11:00 | LC100 ⚡ 早题② (1题) | `scripts/run_morning2.py` | `46e0b5198bc9` | 今日第2题 + 完整题面 |
| 13:00 | LC100 🔄 午间复习 | `scripts/run_noon_review.py` | `3e523f8b7514` | Spaced-repetition review |
| 15:00 | LC100 ⚡ 午题 (1题) | `scripts/run_afternoon.py` | `bf2ea7326e5f` | 今日第3题 + 完整题面 |
| 17:00 | LC100 ⚡ 晚题① (1题) | `scripts/run_eve_push1.py` | `cc57612763dd` | 今日第4题 + 完整题面 |
| 19:00 | LC100 ⚡ 晚题② (1题) | `scripts/run_eve_push2.py` | `cff1f59482d7` | 今日第5题 + 完整题面 |
| 20:00 | LC100 🌙 今日战报 | `scripts/run_eve_summary.py` | `ecc37a05aaa7` | Daily progress report |

All use `no_agent: true`, `deliver: feishu`, `workdir: /root/projects/leetcode-hot100`.

### ⚠️ All Push Scripts MUST Include Full Problem Descriptions

**User explicitly complained**: "cronjob发送的消息很莫名其妙，起不到太大的作用。你起码发消息的时候把题面带上吧"

Every script that pushes problems to the user (new problems AND reviews) MUST read the full problem description from `problems/NNNN_name.md` and output it. The format must include:
1. Problem title + difficulty + URL
2. **Complete problem statement** (from `## 题目描述` section)
3. **All examples** with input/output
4. **Constraints** (data range)

Do NOT just show a one-liner hint or problem number. The user cannot solve problems without seeing the actual question.

The shared pattern for reading problem descriptions:
```python
PROBLEMS_DIR = os.path.join(BASE_DIR, "problems")

def find_problem_file(prob_id):
    prefix = f"{prob_id:04d}_"
    pattern = os.path.join(PROBLEMS_DIR, prefix + "*.md")
    matches = glob.glob(pattern)
    return matches[0] if matches else None

def read_problem_body(filepath):
    with open(filepath, "r") as f:
        content = f.read()
    m = re.search(r"## 题目描述\s*\n(.+)", content, re.DOTALL)
    if m:
        return m.group(1).strip()
    lines = content.split("\n")
    return "\n".join(lines[1:]).strip()
```

### ⚠️ Old `scripts/leetcode_push.py` is Deprecated

The linked file `scripts/leetcode_push.py` is the OLD version with a hardcoded `HINTS` dict and no problem descriptions. The actual scripts are in the project directory:

| Script | Purpose | Full description? |
|--------|---------|-------------------|
| `scripts/push_new.py` | Push new problems with STATE.json tracking | ✅ Yes |
| `scripts/push_review.py` | Spaced-repetition review from completed pool | ✅ Yes (fixed in this session) |
| `scripts/push_summary.py` | Daily progress report | N/A (stats only) |
| `scripts/run_morning1.py` | Wrapper: 1 new problem (09:00) | Calls push_new.py |
| `scripts/run_morning2.py` | Wrapper: 1 new problem (11:00) | Calls push_new.py |
| `scripts/run_noon_review.py` | Wrapper: review (13:00) | Calls push_review.py |
| `scripts/run_afternoon.py` | Wrapper: 1 new problem (15:00) | Calls push_new.py |
| `scripts/run_eve_push1.py` | Wrapper: 1 new problem (17:00) | Calls push_new.py |
| `scripts/run_eve_push2.py` | Wrapper: 1 new problem (19:00) | Calls push_new.py |
| `scripts/run_eve_summary.py` | Wrapper: summary (20:00) | Calls push_summary.py |

### STATE.json — Daily Push Offset Tracker

Each `push_new.py` call increments a per-day counter so consecutive pushes don't repeat problems:

```json
{"date": "2026-05-27", "pushed_today": 4}
```

- On each push: reads `completed` from PROGRESS.md + `pushed_today` from STATE.json → skips already-pushed problems
- Auto-resets when `date` ≠ today (new day detected)
- This is what enables distributing 5 problems across 3 separate cron runs without overlap

### Wrapper Script Pattern

`no_agent: true` cron jobs cannot pass CLI arguments. Solution: wrapper scripts that `chdir` to project root and call the core script with args:

```python
#!/usr/bin/env python3
import subprocess, sys, os
os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
subprocess.run([sys.executable, "scripts/push_new.py", "2", "早题①"])
```

### New Problem Push (push_new.py)
- Args: `count` (number of problems, default 1), `label` (display name like "早题①")
- Reads PROGRESS.md completed count + STATE.json pushed_today → computes offset
- **Reads full problem description from `problems/NNNN_name.md`** (fetched via LeetCode GraphQL API, see `fetch_problems.py`)
- Outputs: problem title + difficulty + category + URL + **complete description with examples and constraints**
- Increments STATE.json pushed_today after each batch
- **Backlog check**: if pushed_today ≥ backlog of ≥5, pauses; otherwise warns and continues

### Spaced Repetition Review (push_review.py)
- Picks 2 problems from completed pool:
  - 1 from most recent 3 (short-term consolidation)
  - 1 from older problems (long-term recall)
- Each gets: **full problem description** (from `problems/NNNN_name.md`) + a random challenge prompt from `CHALLENGES` list
- Reads LeetCode URL from PROBLEMS.txt for each problem

### Daily Summary (push_summary.py)
- Reads STATE.json for today's push count
- ASCII progress bar `[████░░░░] 5/100`
- Estimated days remaining

## Interactive Workflow

### Solving a Problem
1. User describes their approach/algorithm in natural language
2. Agent writes Python code to `code/NNNN_name.py` with inline tests
3. Run `python code/NNNN_name.py` to verify
4. If all tests pass → update `PROGRESS.md`
5. If user asks for "完整代码", show the full Solution class in chat (not just file path)

### Marking Complete (agent does this manually — NOT automated by cron)
When user finishes a problem, update these **in order**:

1. **`PROGRESS.md`** — two patches:
   - Row status: `⏳ 待推送` → `✅ 已完成`, add date and note
   - Count: `完成: N/100` → `完成: N+1/100`, percentage updated
2. **题解文档**: `lark-cli docs +update --command append` with 题意+数据规格+示例+思路+复杂度+代码 (use `gen_doc.py` for full regeneration)
3. **多维表格**: `+record-upsert` to update status to `✅ 已完成` (need API call to get record_id first)
3. **题解文档**: run `python3 scripts/gen_doc.py` to regenerate full doc with ✅ status and code

All three must be updated immediately when user completes a problem. Do NOT defer to the evening cron job.
   - See `references/lark-cli-bitable-pitfalls.md` for exact commands
3. **题解文档**: run `python3 scripts/gen_doc.py` to regenerate full doc (reads PROGRESS.md + problems/ + code/)
   - This overwrites the entire document with current state
   - See `references/lark-cli-bitable-pitfalls.md` for gen_doc.py details

**⚠️ The 20:00 战报 cron job does NOT write progress.** It only reads PROGRESS.md to generate a summary message. Progress must be updated by the agent when the user completes each problem — don't defer to the cron job.

### ⚠️ Three-way sync is MANDATORY, not optional
When user completes a problem, update ALL THREE places (user explicitly required this):
1. **PROGRESS.md** — status + date + notes
2. **多维表格** (Bitable `S2iLbvRetaPEiXsDOsQcWhBHnyd` / `tblgIezE2dgQ7ntK`) — use `+record-upsert` with record_id from `+record-search` by 题号 field
3. **题解文档** (`EZfodeviXosNJLxuZWFcKCwonyg`) — run `scripts/gen_doc.py` to regenerate full doc (overwrite mode)

### ⚠️ gen_doc.py regex bug — PROGRESS.md has TWO numeric columns
The PROGRESS.md table format is `| 序号 | 题号 | 题名 | ...`. The regex to find completed problems MUST skip the first column (序号) and capture the second (题号):
```python
# WRONG — captures 序号 (1,2,3...) instead of 题号 (1,49,283...)
re.finditer(r'\| (\d+) \| .+? \| ✅ 已完成', content)
# CORRECT — skips 序号, captures 题号
re.finditer(r'\| \d+ \| (\d+) \| .+? \| .+? \| ✅ 已完成', content)
```
This bug caused #49 to show as ⏳ in the 题解文档 even after being marked complete. Always verify the regex captures the correct column.

## PROGRESS.md Format

```markdown
| # | 题号 | 题名 | 难度 | 状态 | 完成日期 | 备注 |
|---|------|------|------|------|----------|------|
| 1 | 1 | 两数之和 | Easy | ✅ 已完成 | 2026-05-25 | 哈希表经典入门 |
| 2 | 49 | 字母异位词分组 | Medium | ⏳ 待推送 | - | 下一次推送 |

**完成: 1/100** | **进度: 1%**
```

## PROBLEMS.txt Format

Pipe-delimited: `序号|题号|题名|难度|分类|LeetCode链接`
- Difficulty codes: `E`=Easy, `M`=Medium, `H`=Hard
- First line is comment (`#`), skip when parsing

## References

- `references/cron-architecture.md` — Cron job architecture details
- `references/bitable-categories.md` — PROBLEMS.txt → Bitable 分类映射 + API 踩坑
- `references/bitable-api-patterns.md` — Bitable record operations: getting real record IDs, upsert, datetime format
- `references/complexity-guide.md` — 根据数据规模反推时间/空间复杂度速查表
- `references/feishu-doc-update.md` — 题解文档更新流程、lark-cli 命令、HTML 清理、生成脚本模板
- `references/lark-cli-bitable-pitfalls.md` — Bitable API 踩坑（record_id 格式、flag 名、gen_doc.py 用法、PROGRESS.md 正则列偏移 bug）
- `references/leetcode-graphql-api.md` — LeetCode GraphQL API 抓取题面（urllib vs curl, rate limiting, HTML cleanup）

## Scripts

- `scripts/gen_doc.py` — Generate full 题解文档 from problems/ + code/ + PROGRESS.md, upload to Feishu. Run `python3 scripts/gen_doc.py` after updating PROGRESS.md. Supports `--local` flag to skip upload.

## Pitfalls

### ⚠️ Code must use LeetCode's standard class format
All code files in `code/` MUST use `class Solution:` with `self` as the first parameter. LeetCode's online judge expects this exact format. A standalone function `def moveZeroes(nums):` passes local tests but fails on LeetCode with a syntax error or wrong answer. Test wrappers should instantiate: `s = Solution(); s.moveZeroes(a)`.

### Python urllib returns HTTP 400 for valid LeetCode GraphQL queries
`urllib.request` mysteriously returns 400 for many LeetCode API calls that work fine via curl. Always use `subprocess` + `curl` for LeetCode API requests. See `references/leetcode-graphql-api.md`.

### ⚠️ Cron `script` path is relative to `workdir`
The `script` field is resolved relative to `workdir`. Since `workdir` is `/root/projects/leetcode-hot100` and scripts live in `scripts/` under that, the correct path is `scripts/run_morning1.py`. If you omit the `scripts/` prefix (just `run_morning1.py`), the job **silently produces no output** — `last_status` still shows "ok" but nothing is delivered. Always verify: `ls $workdir/$script`.

**Root-level duplicate wrappers**: If old wrapper scripts exist at the project root (e.g. `/root/projects/leetcode-hot100/run_morning1.py`), a misconfigured cron job (missing `scripts/` prefix) will pick up the root copy instead of failing. The root copies had a `chdir("..")` bug that changed to the wrong directory, causing the subprocess to fail or run stale code. **After any script reorganization, check for and remove stale root-level wrappers**: `ls /root/projects/leetcode-hot100/*.py`. Only `scripts/run_*.py` should exist.

### Silent failure when script path is wrong
A `no_agent` cron job with an invalid `script` path still shows `last_status: "ok"` — the scheduler considers "no output" a success. **Check delivery by looking for the actual message in Feishu**, not by trusting the status field. To debug: run the script manually `cd $workdir && python3 $script` and check for output.

### no_agent cron jobs cannot pass arguments
Use wrapper scripts (run_*.py) that `chdir` + call the core script with `subprocess.run`. Each wrapper is a tiny 4-line script that encodes the specific args.

### Counting completed problems in PROGRESS.md
Do NOT use `content.count('✅')` — the markdown body may contain ✅ in non-table text (e.g., workflow step descriptions like `✅ 测试验证`). Always use a specific table-row pattern:
```python
completed = len(re.findall(r'\| ✅ 已完成', content))
```

### Push scripts must track daily state across runs
Multiple cron jobs push new problems throughout the day. Without STATE.json, they'd all read the same `completed` count and push the same problems. The STATE.json offset is essential — without it, the 09:00 and 11:00 pushes would be identical.

### ⚠️ Problem files contain HTML tags from LeetCode API

The `problems/*.md` files fetched via LeetCode's GraphQL API contain HTML tags that don't render in Feishu or terminal output:
- `<strong class="example">示例 1：</strong>` → should be `**示例 1：**`
- `<span data-keyword="anagram">字母异位词</span>` → should be `字母异位词`
- `<meta charset="UTF-8" />` → should be removed
- `<b>`, `<code>`, `<em>` → convert to markdown equivalents

**Always clean HTML before:**
1. Updating the Feishu 题解文档
2. Outputting problem descriptions in cron messages

Cleaning regex (be careful NOT to match `<=` as HTML):
```python
content = re.sub(r'<strong\s+class="[^"]*">', '**', content)
content = re.sub(r'</strong>', '**', content)
content = re.sub(r'<span[^>]*>', '', content)
content = re.sub(r'</span>', '', content)
content = re.sub(r'<meta[^>]*/?>', '', content)
# Only remove actual HTML tags (start with <letter), NOT <= or >=
content = re.sub(r'<(/?)([a-zA-Z][a-zA-Z0-9]*)[^>]*>', '', content)
```

### ⚠️ __pycache__ causes stale code in cron jobs

After modifying scripts in `/root/projects/leetcode-hot100/scripts/`, Python's `__pycache__` may contain stale `.pyc` bytecode. The cron system (running `python3 scripts/run_*.py`) may load the cached bytecode instead of the updated source.

**After any script modification, always clear __pycache__:**
```bash
find /root/projects/leetcode-hot100 -name "__pycache__" -type d -exec rm -rf {} +
```

This is especially important for the review scripts — if `push_review.py` was updated to include full descriptions but the __pycache__ has the old version (without descriptions), the cron job will still send the old format.

### Review scripts MUST include full problem descriptions
`push_review.py` was originally written to only show problem name + number + a random challenge prompt (e.g. "🧠 这道题的变种/相关题？"). User feedback: "cronjob发送的消息很莫名其妙，起不到太大的作用。你起码发消息的时候把题面带上吧". The review script must read the full problem description from `problems/NNNN_name.md` (same as `push_new.py` does), not just show the title. Both push and review scripts should output: title + difficulty + URL + **full description with examples and constraints** + (for review) a challenge prompt.

### Keep wrapper scripts in sync with core scripts
Authoritative copies live in the project `scripts/` dir. The cron jobs reference `scripts/run_*.py` relative to `workdir`, so there's no need to mirror to `~/.hermes/scripts/`. Just ensure the project dir has all scripts.

### ⚠️ gen_doc.py 正则匹配错位 bug（已修复）
`scripts/gen_doc.py` 的 `get_completed()` 函数曾用 `\| (\d+) \| .+? \| ✅ 已完成` 匹配，但这会捕获第一列（序号）而非第二列（题号），导致已完成的题在飞书文档中仍显示 ⏳。
**修复**：改为 `\| \d+ \| (\d+) \| .+? \| .+? \| ✅ 已完成`，跳过序号列，捕获题号列。

### ⚠️ Agent must update ALL THREE progress locations immediately
The 20:00 战报 cron job (`push_summary.py`) only **reads** PROGRESS.md to generate a daily summary message (progress bar, push count, days remaining). It does **NOT** write to PROGRESS.md, Bitable, or 题解文档. When the user completes a problem during a conversation, the agent must update **all three** immediately — don't defer to the evening cron.

**The three locations (in order):**
1. **`PROGRESS.md`** — update row status + date + note + count/percentage
2. **多维表格 Bitable** — use `lark-cli base +record-upsert` to update 状态/完成日期/备注 (see Bitable API pitfalls below)
3. **题解文档** — run `python3 scripts/gen_doc.py` to regenerate full document from problem files + code files

The user explicitly corrected this: "我做完之后你及时更新文档了吗？还是说每天最后的那个cron job负责更新进度多维表格和相关文档" — they expected ALL three to be synced, not just PROGRESS.md.

### ⚠️ Bitable record IDs: +record-list returns row numbers, not record IDs
`lark-cli base +record-list` returns arrays where the first element is the 序号 field value (e.g., "1", "2"), **NOT** the actual record_id. The actual record_id (format `recXXXXXXXXXX`) is needed for `+record-upsert`.

**To get real record IDs**, use the raw API:
```bash
lark-cli api GET "/open-apis/bitable/v1/apps/<base_token>/tables/<table_id>/records" \
  --params '{"page_size":100}' --as bot
```
This returns `items[].record_id` in the proper `recXXX` format. Then use:
```bash
lark-cli base +record-upsert --base-token <base> --table-id <table> \
  --record-id recXXX --as bot --json '{"状态": "✅ 已完成", "完成日期": "2026-06-08 00:00:00", "备注": "..."}'
```
Datetime format: `"YYYY-MM-DD HH:MM:SS"` (will be stored as millisecond timestamp internally).

### ⚠️ gen_doc.py regex bug — must match 题号 column, not 序号 column
The `get_completed()` function in `scripts/gen_doc.py` must use a regex that skips the 序号 (first column) and captures the 题号 (second column):
```python
# WRONG — captures 序号 (1,2,3...) instead of 题号 (1,49,128...)
re.finditer(r'\| (\d+) \| .+? \| ✅ 已完成', content)
# CORRECT — skips 序号, captures 题号
re.finditer(r'\| \d+ \| (\d+) \| .+? \| .+? \| ✅ 已完成', content)
```
This bug caused completed problems to not be marked ✅ in the generated 题解文档.

**Three-way sync checklist (in order):**
1. **PROGRESS.md** — two patches: row status + count
2. **多维表格** — `lark-cli base +record-upsert` to update 状态/完成日期/备注
3. **题解文档** — run `python3 scripts/gen_doc.py` to regenerate full doc

Do NOT skip #2 and #3. User was surprised they weren't being synced.

### ⚠️ PROGRESS.md 正则匹配列偏移 Bug
PROGRESS.md 表格有 7 列：`| 序号 | 题号 | 题名 | 难度 | 状态 | 完成日期 | 备注 |`

**错误写法**（匹配第一列「序号」而非「题号」）：
```python
re.findall(r'\| (\d+) \| .+? \| ✅ 已完成', content)
# → 返回 [1, 2, 3, 4, 5, 6]（序号），不是题号！
```

**正确写法**（跳过序号列，匹配第二列题号）：
```python
re.findall(r'\| \d+ \| (\d+) \| .+? \| .+? \| ✅ 已完成', content)
# → 返回 [1, 3, 11, 49, 283, 560]（题号）✓
```

This bug caused `gen_doc.py` to mark #49 as ⏳ even after PROGRESS.md was updated. Every script that reads PROGRESS.md must use the correct 7-column pattern.

### Old job IDs are stale
All previous job IDs (`2194b79ef67d`, `7d33e6f42294`, `814448da952c`, `ce77b827ed2a`, etc.) have been deleted. Only the 6 current IDs in the table above are active.

## Script Reference

Key constants and dicts in core scripts:
- `push_new.py`: STATE.json management, reads full problem descriptions from `problems/NNNN_name.md`
- `push_review.py`: `CHALLENGES` list (random review prompts), picks 2 problems (1 recent + 1 older), reads full problem descriptions from `problems/NNNN_name.md`
- `push_summary.py`: reads STATE.json for push count, generates ASCII progress bar
