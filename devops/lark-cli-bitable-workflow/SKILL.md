---
name: lark-cli-bitable-workflow
description: "lark-cli 操作飞书多维表格（Base/Bitable）的实战经验和踩坑记录。当需要创建表、批量写记录、设置关联字段、重建表结构时参考。"
---

# lark-cli Bitable 实战经验

> 补充 lark-base skill 的官方文档，记录实际操作中发现的坑和解决方案。

**参考资料**：
- `references/create-base-with-tables.md` — 从零创建完整多维表格的流程（Base + 多表 + 批量数据 + record_id 查找）。
- `references/model-benchmark-bitable.md` — 模型评测分数多维表格设计（透明性原则、缺失数据加权方法论）。

## 1. 文件路径必须是相对路径

`+record-batch-create --json @file` 和 `+record-upsert --json @file` 的文件路径**必须是相对路径**，绝对路径会报错。

```bash
# ❌ 报错
lark-cli base +record-batch-create --json @/tmp/data.json ...

# ✅ 正确
cd /tmp
lark-cli base +record-batch-create --json @./data.json ...
```

## 2. Shortcut 命令的 pretty 输出不含 record_id

`+record-list`、`+record-batch-create` 等 shortcut 命令默认返回 pretty 格式，**不包含 `record_id`**。

**获取 record_id 的方法**：用 `lark-cli api` 直接调原始 API + jq 提取：

```bash
# 获取所有记录的 record_id 和字段值
lark-cli api GET \
  "/open-apis/bitable/v1/apps/${BASE_TOKEN}/tables/${TABLE_ID}/records" \
  --params '{"page_size":200}' \
  --as user \
  -q '[.data.items[] | {record_id, name: .fields["Name"]}]'
```

**注意**：原始 bitable API (`/open-apis/bitable/v1/apps/...`) 返回的字段值中，**数字类型也会以字符串形式返回**，需要 `tonumber` 转换：

```bash
-q '[.data.items[] | {record_id, num: (.fields["镜头号"] | tonumber)}]'
```

## 3. Batch Update 对 Link 字段有限制

`+record-batch-update` 将同一 patch 应用到所有指定 record_id，但对 **link（关联）字段会报错**：

```
[800004135] the method：OpenAPIBatchUpdateRecords limited
```

**解决方案**：改用 `+record-upsert` 逐条更新：

```bash
for record_id in ...; do
  lark-cli base +record-upsert \
    --base-token XXX \
    --table-id tblXXX \
    --record-id "$record_id" \
    --json '{"关联场景":[{"id":"recXXX"}]}'
  sleep 0.15  # 避免限流
done
```

## 4. `--record-id` 是独立 flag

`+record-upsert` 的 `record_id` 通过 `--record-id` flag 传递，**不要放在 `--json` 里面**：

```bash
# ❌ 错误（会报 validation failed）
--json '{"record_id":"recXXX","fields":{...}}'

# ✅ 正确
--record-id recXXX --json '{"关联场景":[{"id":"recXXX"}]}'
```

## 5. Link 字段值格式

关联字段的写入值是对象数组：

```json
{"关联场景": [{"id": "recXXX"}]}
```

在 `+table-create --fields` 中创建 link 字段：

```json
{"type": "link", "name": "关联场景", "link_table": "场景", "bidirectional": false}
```

## 6. Primary Field（主字段）不可删除

创建表时，**第一个字段自动成为 primary field**，之后不能删除，会报错：

```
[800080207] unsafe_operation_blocked — The primary field cannot be deleted
```

也无法通过 `+field-update` 将其他字段设为 primary（`primary` key 不被 API 识别）。

**重建表的流程**（当需要更换主字段时）：

1. 先创建新表（把目标主字段放在 `--fields` 第一个位置）
2. 批量写入数据到新表
3. 删除旧表（注意：base 至少保留一张表）
4. 重命名新表

```bash
# 1. 创建新表（"Name" 会是 primary field）
lark-cli base +table-create --base-token XXX --name "新表" \
  --fields '[{"type":"text","name":"Name"},{"type":"number","name":"ID"}]'

# 2. 写数据...

# 3. 删旧表（base 必须至少有 2 张表才能删）
lark-cli base +table-delete --base-token XXX --table-id tblOLD --yes

# 4. 重命名新表
lark-cli base +table-update --base-token XXX --table-id tblNEW --name "最终表名"
```

## 7. 最后一张表不能删除

Base 至少保留一张表。如果只有一张表需要删除，必须**先创建替代表，再删旧的**。

## 8. `+record-batch-create` 的格式是 `fields` + `rows`，不是 `records`

```bash
# ❌ 错误格式
--json '{"records": [{"fields": {"Name": "A"}}, {"fields": {"Name": "B"}}]}'

# ✅ 正确格式
--json '{"fields": ["Name", "Status"], "rows": [["A", "Open"], ["B", "Done"]]}'
```

字段值的顺序必须和 `fields` 数组一一对应。select/multi_select 字段直接传字符串值即可。

## 9. `+record-batch-update` 格式：统一 patch

```bash
# 对所有指定记录应用同一个 patch
--json '{"record_id_list": ["recXXX", "recYYY"], "patch": {"Status": "Done"}}'
```

**限制**：只能对所有记录应用**同一个** patch。如果每条记录需要不同的值，必须逐条用 `+record-upsert`。

## 10. 创建 multi_select 字段必须用原始 API

`+field-create --json '{"type":"multi_select","name":"标签"}` 会创建一个 `single_select` 字段（`multiple: false`）！

**正确做法**：用原始 API + `type: 4`：

```bash
lark-cli api POST "/open-apis/bitable/v1/apps/$BASE/tables/$TABLE/fields" --as bot \
  --data '{"field_name":"标签","type":4,"property":{"options":[{"name":"选项A"},{"name":"选项B"}]}}'
```

验证：`+field-list` 查看新字段，确认 `"multiple": true`。

## 11. 创建 URL 字段必须用原始 API

`+field-create --json '{"type":"url","name":"链接"}` 会创建 `text` 字段！

**正确做法**：用原始 API + `type: 15`：

```bash
lark-cli api POST "/open-apis/bitable/v1/apps/$BASE/tables/$TABLE/fields" --as bot \
  --data '{"field_name":"LeetCode","type":15}'
```

写入时直接传纯字符串（不是 `{"link":"...", "text":"..."}`），URL 字段会自动识别为可点击链接：

```bash
lark-cli base +record-upsert ... --json '{"LeetCode": "https://leetcode.cn/problems/two-sum/"}'
```

## 12. 删除字段会同时删除该字段的所有数据

`+field-delete` 是不可逆的。如果需要"迁移"字段类型（如 text→URL），必须：
1. 创建新字段
2. 逐条 `+record-upsert` 把旧字段数据复制到新字段
3. 确认数据无误后才删除旧字段

## 13. 仪表盘（Dashboard）API 不可创建

飞书 Bitable 的仪表盘没有开放创建 API。只能通过 UI 手动添加：多维表格 → 左下角「+」→ 仪表盘。

## 14. 批量操作限流

连续 `+record-upsert` 调用时建议每次间隔 `0.15~0.3` 秒，避免触发限流错误。

## 9. `+record-search` 有最低要求

`+record-search --json` 必须同时提供 `keyword`（非空）和 `search_fields`（数组），否则报验证错误。

## 10. `--page-all` 输出包含进度文本，不能直接 JSON 解析

`--page-all` 会在 JSON 前插入 `[page 1] fetching...` 等进度信息，导致 `json.load()` 失败。

**解决方案**：用手动分页代替 `--page-all`，用 `-q '.'` 输出纯 JSON 到文件：

```python
# 手动分页获取所有记录
all_items = []
page_token = None
while True:
    params = {"page_size": 200}
    if page_token:
        params["page_token"] = page_token
    
    result = subprocess.run(
        ['lark-cli', 'api', 'GET',
         f'/open-apis/bitable/v1/apps/{BASE_TOKEN}/tables/{TABLE_ID}/records',
         '--as', 'bot',
         '--params', json.dumps(params),
         '-q', '.'],
        capture_output=True, text=True, timeout=30
    )
    data = json.loads(result.stdout)
    items = data.get('data', {}).get('items', [])
    all_items.extend(items)
    
    if not data.get('data', {}).get('has_more', False):
        break
    page_token = data['data'].get('page_token')
```

## 11. Link 字段的 `record_ids` 可以为 `null`

关联字段的 `record_ids` 字段**不一定返回列表**，未关联时可能为 `null`。遍历前必须 `or []`：

```python
# ❌ 报错 TypeError: 'NoneType' object is not iterable
for rid in link_field.get('record_ids', []):

# ✅ 正确
for rid in link_field.get('record_ids') or []:
```

## 12. 附件（图片）下载：用 batch_get_tmp_download_url

Bitable 中的附件（type=17）不能直接用 `lark-cli drive download` 或 `/drive/v1/medias/{token}`。

**正确流程**：

1. 从记录的附件字段获取 `file_token` 和 `name`
2. 调用 `batch_get_tmp_download_url` API 获取临时下载链接
3. 用 `curl` 下载

```python
# 获取临时下载 URL
result = subprocess.run(
    ['lark-cli', 'api', 'GET',
     '/open-apis/drive/v1/medias/batch_get_tmp_download_url',
     '--as', 'bot',
     '--params', json.dumps({"file_tokens": file_token})],
    capture_output=True, text=True, timeout=30
)
data = json.loads(result.stdout)
url = data['data']['tmp_download_urls'][0]['tmp_download_url']

# 下载文件
subprocess.run(['curl', '-sS', '-o', local_path, url], timeout=30)
```

注意：临时 URL 有时效性，获取后应立即下载。每次调用间隔 0.2 秒避免限流。

## 13. 从 Bitable 导出数据到本地数据库的流程

1. 获取表列表 → 获取每张表的字段定义 → 获取所有记录（手动分页）
2. 下载附件（图片）到本地 `uploads/` 目录，保存 `file_token → local_filename` 映射
3. 解析字段：富文本字段提取 `.text`，用户字段提取 `.name`，时间戳转字符串
4. 数据清洗：去重、确保唯一约束（如 asset_code）、处理 null 值
5. 脱敏（如需要）：生成 `真实名 → 假名` 映射，固定随机种子保证可复现
6. 写入 SQLite

**关键教训**：导入数据前，必须先读取项目**实际的数据库定义代码**（如 `database.js`），而不是参考 CLAUDE.md 或其他文档描述。文档可能过时，字段名、约束、类型都可能有差异。直接读源码 `CREATE TABLE` 语句是最可靠的。

## 14. `PATCH` 方法对 Bitable 记录返回 404，必须用 `PUT`

`lark-cli api PATCH .../records/{record_id}` 对 Bitable 记录更新会返回 404，而 `PUT` 正常工作：

```bash
# ❌ 返回 404
lark-cli api PATCH "/open-apis/bitable/v1/apps/{BASE}/tables/{TABLE}/records/{RID}" \
  --data '{"fields":{"评测集权重":3}}'

# ✅ 正常工作
lark-cli api PUT "/open-apis/bitable/v1/apps/{BASE}/tables/{TABLE}/records/{RID}" \
  --data '{"fields":{"评测集权重":3}}'
```

注意：PUT 需要传完整 `{"fields": {...}}` 包装，字段值必须是正确类型（数字不能是字符串）。

## 15. Bitable 读取的数值字段返回为字符串

GET 记录时，即使字段类型是 `number`，返回值也是字符串 `"87.5"` 而非 `87.5`。Python 端必须显式转换：

```python
def to_float(v):
    if v is None: return None
    if isinstance(v, (int, float)): return float(v)
    try: return float(v)
    except: return None

# 读取后必须转换
val = to_float(record["fields"].get("MMLU-Pro"))  # "87.5" → 87.5
```

## 16. Table ID 在表重建后会变化

Bitable 的 table_id 在删除重建后会变成新的 ID。**每次操作前应先获取最新 table_id**：

```bash
lark-cli api GET "/open-apis/bitable/v1/apps/{BASE}/tables" | \
  jq '.data.items[] | {table_id, name}'
```

不要缓存或硬编码 table_id，除非确认表结构未变。

## 17. `--page-all` 的替代方案：`-q '.'` 单页请求

当 `--page-all` 不方便时（输出含进度文本），可以用 `-q '.'` 获取单页纯 JSON，然后手动翻页：

```bash
# 获取第一页
lark-cli api GET "/open-apis/bitable/v1/apps/${BASE_TOKEN}/tables/${TABLE_ID}/records" \
  --as bot --params '{"page_size":200}' -q '.' > /tmp/page1.json

# 从响应中提取 page_token 用于下一页
python3 -c "import json; d=json.load(open('/tmp/page1.json')); print(d['data'].get('page_token',''))"

# 获取第二页
lark-cli api GET "/open-apis/bitable/v1/apps/${BASE_TOKEN}/tables/${TABLE_ID}/records" \
  --as bot --params '{"page_size":200,"page_token":"THE_TOKEN"}' -q '.' > /tmp/page2.json
```

注意：`page_size` 最大 200。如果 `has_more=true`，继续翻页直到 `has_more=false`。

## 15. 用户字段（CreatedUser/User type=1003/11）的数据结构

- **CreatedUser（type=1001）**：返回 `{"name": "xxx", "avatar_url": "..."}` 对象，不是数组
- **User（type=11）**：返回对象数组 `[{"name": "xxx", "avatar_url": "..."}]`

提取第一个用户名：
```python
def get_first_user_name(field_val):
    if not field_val:
        return ""
    if isinstance(field_val, list) and len(field_val) > 0:
        return field_val[0].get('name', '')
    if isinstance(field_val, dict):
        return field_val.get('name', '')
    return ""
```

## 16. 公式字段（type=20）的 text 提取

公式字段返回 `[{"text": "结果文字", "type": "text"}]`，需要提取 `.text`：

```python
def get_text(field_val):
    if not field_val:
        return ""
    if isinstance(field_val, str):
        return field_val
    if isinstance(field_val, list):
        return ''.join(item.get('text', '') if isinstance(item, dict) else str(item) for item in field_val)
    return str(field_val)
```

## 17. 场景解耦工作流（关联表模式）

将扁平的"场景+镜头"数据解耦为两张关联表的推荐流程：

1. 创建「场景」表（含编号、名称、拍摄场地等）
2. 批量插入场景记录
3. 用 raw API + jq 获取场景的 `record_id`
4. 创建「镜头」表，包含 link 字段指向场景表
5. 批量插入镜头记录（不含 link 字段）
6. 用 raw API + jq 获取镜头的 `record_id`
7. 逐条 `+record-upsert` 设置 link 关联（batch-update 对 link 有限制）
8. 清理：删除旧表、重命名新表

## 18. 创建记录时字段不存在：FieldNameNotFound 或静默失败

`POST .../records` 写入不存在的字段名时，lark-cli 可能返回 `FieldNameNotFound` 错误（code 1254045），或者返回空 stdout（Python `json.loads` 会抛 JSONDecodeError）。

**根因**：Bitable 只接受已定义字段名的写入。新列必须先用 `POST .../fields` 创建。

**调试技巧**：当 Python 脚本中 `json.loads(r.stdout)` 失败时，先检查 `r.stdout` 是否为空字符串：
```python
if not r.stdout.strip():
    return {"code": -1}  # likely field name error
try:
    return json.loads(r.stdout)
except json.JSONDecodeError:
    return {"code": -1}
```

**批量操作前先检查字段列表**：
```bash
lark-cli api GET "/open-apis/bitable/v1/apps/$BASE/tables/$TABLE/fields" | \
  python3 -c "import sys,json; [print(f['field_name']) for f in json.load(sys.stdin)['data']['items']]"
```
