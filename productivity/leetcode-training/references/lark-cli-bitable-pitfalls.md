# lark-cli Bitable API Pitfalls

## Command Names
- Bitable operations: `lark-cli base` (NOT `lark-cli bitable`)
- Docs fetch: `lark-cli docs +fetch` (NOT `+get`)

## Flag Names
- `--base-token` (NOT `--base`)
- `--table-id` (NOT `--table`)
- `--limit` for pagination (NOT `--page-size`)
- `--format json` or `--format markdown` only (NOT `pretty`)

## Record IDs
- `+record-list` returns data arrays where the first element is the 序号 field value, NOT the record_id
- Actual record IDs have format `recXXXXXXXXXX` (rec + 1-11 alphanumeric)
- To get real record IDs, use the raw API:
  ```bash
  lark-cli api GET "/open-apis/bitable/v1/apps/<base_token>/tables/<table_id>/records" --params '{"page_size":3}' --as bot
  ```
- Then parse `item["record_id"]` from the response

## Finding a Specific Record
```bash
lark-cli base +record-search --base-token S2iLbvRetaPEiXsDOsQcWhBHnyd \
  --table-id tblgIezE2dgQ7ntK --keyword "49" --search-field "题号" \
  --limit 5 --as bot --format json
```
This returns the record data but still uses the array format. Use raw API to get record_id.

## Updating a Record
```bash
lark-cli base +record-upsert --base-token <base> --table-id <table> \
  --record-id recXXXXXXXXXX --as bot \
  --json '{"状态": "✅ 已完成", "完成日期": "2026-06-08 00:00:00", "备注": "排序+哈希表分组"}'
```
- datetime values: `"YYYY-MM-DD HH:MM:SS"` format
- select values: exact string match from options (e.g. `"✅ 已完成"`)
- multi_select values: `["Tag A", "Tag B"]`

## gen_doc.py — Full Document Regeneration
Script at `/root/projects/leetcode-hot100/scripts/gen_doc.py` regenerates the entire 题解文档 and uploads to Feishu.

Usage: `cd /root/projects/leetcode-hot100 && python3 scripts/gen_doc.py`

- Reads PROGRESS.md to determine which problems are ✅
- Reads problems/*.md for problem descriptions
- Reads code/*.py for solutions (completed problems only)
- Cleans HTML tags from LeetCode API responses
- Outputs to /tmp/lc100_doc.md then uploads via `lark-cli docs +update --mode overwrite`
- Uses `@./lc100_doc.md` (relative path, NOT absolute) — must `cwd=/tmp`

### PROGRESS.md Column Parsing (critical)
The table has 7 columns. Regex must skip the 序号 column:
```python
# WRONG — matches 序号 (1st column)
re.findall(r'\| (\d+) \| .+? \| ✅ 已完成', content)

# RIGHT — matches 题号 (2nd column)  
re.findall(r'\| \d+ \| (\d+) \| .+? \| .+? \| ✅ 已完成', content)
```
