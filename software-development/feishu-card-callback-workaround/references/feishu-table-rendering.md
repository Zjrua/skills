# Feishu Markdown Table Rendering — Fix Record (2026-05-26)

## Symptom

Markdown tables in Hermes replies appeared as raw pipe-delimited text in Feishu chat, e.g.:

```
| 时间 | 类型 | 题数 |
|------|------|------|
| 09:00 | ⚡ 早题① | 2新题 |
```

instead of being rendered as a proper table.

## Root Cause

In `gateway/platforms/feishu.py`, method `_build_outbound_payload()` (line ~4007), there was a pre-check that forced any content containing markdown tables to use `msg_type="text"` instead of `msg_type="post"`:

```python
# REMOVED — this was wrong
if _MARKDOWN_TABLE_RE.search(content):
    text_payload = {"text": content}
    return "text", json.dumps(text_payload, ensure_ascii=False)
```

The comment claimed: *"Feishu post-type 'md' elements do not render markdown tables; sending table content as post causes the message to appear blank on the client."*

**This was incorrect.** User confirmed tables rendered fine as `post` type before this downgrade was added.

## Fix

Removed the 6-line downgrade block entirely. Tables now flow through the normal markdown detection path:

```python
if _MARKDOWN_HINT_RE.search(content):
    return "post", _build_markdown_post_payload(content)
```

## Diff

```diff
 def _build_outbound_payload(self, content: str) -> tuple[str, str]:
-    # Feishu post-type 'md' elements do not render markdown tables; sending
-    # table content as post causes the message to appear blank on the client.
-    # Force plain text for anything that looks like a markdown table.
-    if _MARKDOWN_TABLE_RE.search(content):
-        text_payload = {"text": content}
-        return "text", json.dumps(text_payload, ensure_ascii=False)
     if _MARKDOWN_HINT_RE.search(content):
```

## Verification

- Patch applied, gateway restart pending user confirmation.
- `_MARKDOWN_TABLE_RE` regex is still defined in the file but now unused by this method — could be cleaned up later.
