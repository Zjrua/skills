# lark-cli Bitable API Patterns

Practical commands for operating on the LC100 进度追踪 Bitable.

## Base Info
- **base_token**: `S2iLbvRetaPEiXsDOsQcWhBHnyd`
- **table_id**: `tblgIezE2dgQ7ntK`
- **URL**: https://my.feishu.cn/base/S2iLbvRetaPEiXsDOsQcWhBHnyd

## Listing Records

`+record-list` returns arrays where the first element is the 序号 field value, NOT the record_id.

```bash
# List all records (returns field values, not record IDs!)
lark-cli base +record-list --base-token S2iLbvRetaPEiXsDOsQcWhBHnyd \
  --table-id tblgIezE2dgQ7ntK --limit 100 --as bot --format json

# Search for a specific problem by 题号
lark-cli base +record-search --base-token S2iLbvRetaPEiXsDOsQcWhBHnyd \
  --table-id tblgIezE2dgQ7ntK --keyword "49" --search-field "题号" \
  --limit 5 --as bot --format json
```

## Getting Real Record IDs

`+record-list` does NOT return record IDs. Use the raw API:

```bash
lark-cli api GET "/open-apis/bitable/v1/apps/S2iLbvRetaPEiXsDOsQcWhBHnyd/tables/tblgIezE2dgQ7ntK/records" \
  --params '{"page_size":100}' --as bot
```

Response contains `items[].record_id` in format `recXXXXXXXXXX`.

To find a specific record's ID:
```bash
lark-cli api GET "/open-apis/bitable/v1/apps/S2iLbvRetaPEiXsDOsQcWhBHnyd/tables/tblgIezE2dgQ7ntK/records" \
  --params '{"page_size":3}' --as bot 2>&1 | python3 -c "
import sys, json
data = json.loads(sys.stdin.read())
for item in data.get('data',{}).get('items',[]):
    print(f'record_id: {item[\"record_id\"]}, 题号: {item[\"fields\"].get(\"题号\",\"?\")}, 状态: {item[\"fields\"].get(\"状态\",\"?\")}')
"
```

## Updating a Record (Upsert)

Once you have the `recXXX` record_id:

```bash
lark-cli base +record-upsert \
  --base-token S2iLbvRetaPEiXsDOsQcWhBHnyd \
  --table-id tblgIezE2dgQ7ntK \
  --record-id recvkUjFXQVnXd \
  --as bot \
  --json '{"状态": "✅ 已完成", "完成日期": "2026-06-08 00:00:00", "备注": "排序+哈希表分组"}'
```

## Field Types
| Field | Name | Type | Notes |
|-------|------|------|-------|
| fldQLcE39l | 序号 | text | Row number |
| fldeeMPrkA | 题号 | text | Problem ID |
| fldrI5EZWb | 题名 | text | Problem name |
| fldUgUgw7v | 难度 | select | Easy/Medium/Hard |
| fldGUzNOh9 | 标签 | multi_select | Categories (哈希表, 双指针, etc.) |
| fldKlhdUT6 | 状态 | select | ✅ 已完成 / ⏳ 待推送 / 🔄 复习中 |
| fldtFCwv1v | 完成日期 | datetime | Format: yyyy/MM/dd |
| fldn7LHIA7 | 备注 | text | Notes |
| fldDdchspy | LeetCode | text (url) | URL field |

## Flag Names (lark-cli)
- `--base-token` (NOT `--base`)
- `--table-id` (NOT `--table`)
- `--record-id` for upsert (format: `recXXX`, NOT numeric)
- `--format json` or `--format markdown` (NOT `pretty` for some commands)
- `--limit` (NOT `--page-size`)

## Common Pitfalls
1. **record_id format**: Must be `rec` + 1-11 alphanumeric chars. Row numbers from `+record-list` won't work.
2. **+record-list vs +record-search**: `+record-list` returns all records but no record_ids. `+record-search` can filter by field but also doesn't return record_ids. Only the raw API returns proper record_ids.
3. **datetime field**: Use `"YYYY-MM-DD HH:MM:SS"` format. Stored as millisecond timestamp internally.
4. **select fields**: Value must be exact string match including emoji (e.g., `"✅ 已完成"` not `"已完成"`).
