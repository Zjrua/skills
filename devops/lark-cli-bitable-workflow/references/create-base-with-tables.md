# 创建完整的多维表格（Base + 多张表 + 批量数据）

> 当需要从零创建一个多维表格，包含多张表、自定义字段和批量数据时参考。

## 完整流程

```bash
# 1. 创建 Base
lark-cli base +base-create --name "表名" --time-zone "Asia/Shanghai" --as bot

# 2. 创建表（不含默认表的数据）
lark-cli base +table-create --base-token <BASE> --name "表1" --as bot
lark-cli base +table-create --base-token <BASE> --name "表2" --as bot

# 3. 逐个添加字段（--json 内联）
lark-cli base +field-create --base-token <BASE> --table-id <TBL> \
  --json '{"name":"字段名","type":"number"}' --as bot

# 4. 批量插入数据
lark-cli base +record-batch-create --base-token <BASE> --table-id <TBL> \
  --json '{"fields":["字段1","字段2"],"rows":[["值1",123],["值2",456]]}' --as bot

# 5. 删除默认空表
lark-cli base +table-delete --base-token <BASE> --table-id <DEFAULT_TBL> --as bot --yes
```

## 字段类型速查

| type | 说明 | 值格式 |
|------|------|--------|
| `text` | 文本 | `"字符串"` |
| `number` | 数字 | `123` 或 `12.5` |
| `select` | 单选 | `"选项名"` |
| `multi_select` | 多选 | ⚠️ 用 raw API + type:4 |
| `datetime` | 日期 | `"2026-06-08 00:00:00"` |
| `url` | URL | ⚠️ 用 raw API + type:15 |
| `checkbox` | 复选 | `true`/`false` |

## ⚠️ 按业务键查找 record_id

`+record-upsert` 需要 `--record-id`，但新建表时没有现成的 record_id。用 `+record-search` 按业务键查找：

```bash
# 按字段值搜索记录
lark-cli base +record-search --base-token <BASE> --table-id <TBL> \
  --keyword "49" --search-field "题号" --limit 5 --as bot --format json

# 响应中 data[0] 的第一个元素是 序号（非 record_id）
# 需要用 raw API 获取真正的 record_id：
lark-cli api GET "/open-apis/bitable/v1/apps/<BASE>/tables/<TBL>/records" \
  --params '{"page_size":3}' --as bot | python3 -c "
import sys, json
data = json.loads(sys.stdin.read())
for item in data.get('data',{}).get('items',[])[:3]:
    print(f'record_id: {item[\"record_id\"]}, 题号: {item[\"fields\"].get(\"题号\",\"?\")}')
"
```

**注意**：`+record-list` 和 `+record-search` 返回的 `data` 数组中，第一个元素是**序号字段的值**，不是 record_id。必须用 raw API 才能拿到真正的 `record_id`（格式为 `rec` + 字母数字）。

## ⚠️ 内联 JSON 的 shell 转义

当 JSON 包含中文或复杂值时，用文件中转更可靠：

```bash
# 写入临时文件
echo '{"fields":["Name"],"rows":[["值"]]}' > /tmp/data.json

# cd 到文件所在目录，用相对路径
cd /tmp && lark-cli base +record-batch-create --base-token X --table-id Y \
  --json @./data.json --as bot
```

## ⚠️ Python hermes_tools.terminal 的 JSON 转义

在 `execute_code` 中调用 terminal 时，单引号嵌套需要转义：

```python
payload_json = json.dumps(payload, ensure_ascii=False)
payload_escaped = payload_json.replace("'", "'\\''")
r = terminal(f"lark-cli ... --json '{payload_escaped}'")
```
