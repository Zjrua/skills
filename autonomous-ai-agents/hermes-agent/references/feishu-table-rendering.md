# Feishu Markdown Table Rendering — Known Bug & Fix

## Symptom

Markdown tables in Hermes Agent's Feishu messages render as raw plain text or disappear entirely. Bold, lists, code blocks, and links render normally.

## Root Cause

In `gateway/platforms/feishu.py`, `_build_outbound_payload()` (line ~4007) detects markdown table syntax and **forces `msg_type="text"`**, bypassing the `post` rendering pipeline entirely:

```python
_MARKDOWN_TABLE_RE = re.compile(r"^\|.*\|\n\|[-|: ]+\|", re.MULTILINE)

def _build_outbound_payload(self, content):
    # Line 4011-4013: tables forced to plain text
    if _MARKDOWN_TABLE_RE.search(content):
        text_payload = {"text": content}
        return "text", json.dumps(text_payload, ensure_ascii=False)
    if _MARKDOWN_HINT_RE.search(content):
        return "post", _build_markdown_post_payload(content)
    # ...
```

This was originally a workaround because Feishu's `post` type `md` element **did not render tables** (showed blank). However, **Feishu now supports tables in post format**, making the workaround counterproductive — it produces worse output (raw text) than the original issue (blank).

Additionally, `_MARKDOWN_HINT_RE` (line 152) does not include table syntax detection (`^\s*\|`), so even without the workaround, table-only messages would fall through to plain text anyway.

## GitHub Issues & PRs (all open as of 2026-05-25)

| # | Title | Type |
|---|-------|------|
| [#9549](https://github.com/NousResearch/hermes-agent/issues/9549) | [Feishu] Markdown tables not rendering in Feishu messages | Bug report (P2) |
| [#26658](https://github.com/NousResearch/hermes-agent/issues/26658) | Remove markdown table force-text workaround — Feishu now supports tables | Feature request (P2) |
| [#27922](https://github.com/NousResearch/hermes-agent/pull/27922) | fix(feishu): render markdown tables as native Feishu tables | PR (most complete) |
| [#25453](https://github.com/NousResearch/hermes-agent/pull/25453) | fix(feishu): render markdown tables as interactive card table components | PR |
| [#29918](https://github.com/NousResearch/hermes-agent/pull/29918) | fix: render Feishu markdown tables as cards | PR |
| [#29736](https://github.com/NousResearch/hermes-agent/pull/29736) | fix(feishu): render markdown tables with card json 2.0 | PR |
| [#28837](https://github.com/NousResearch/hermes-agent/pull/28837) | fix(feishu): render markdown tables via cards | PR |

## Local Fix (PR #27922 approach)

In `gateway/platforms/feishu.py`:

1. **Remove** the `_MARKDOWN_TABLE_RE` check in `_build_outbound_payload()` (lines 4011-4013)
2. **Add** `|(\s*\|)` to `_MARKDOWN_HINT_RE` (line 152-154) so table syntax is detected and routed to `post` type

```python
# Before (line 152-154):
_MARKDOWN_HINT_RE = re.compile(
    r"(^#{1,6}\s)|(^\s*[-*]\s)|(^\s*\d+\.\s)|(^\s*---+\s*$)|(```)|(`[^`\n]+`)|(\*\*[^*\n].+?\*\*)|(~~[^~\n].+?~~)|(<u>.+?</u>)|(\*[^*\n]+\*)|(\[[^\]]+\]\([^)]+\))|(^>\s)",
    re.MULTILINE,
)

# After — add |(\s*\|) at end:
_MARKDOWN_HINT_RE = re.compile(
    r"(^#{1,6}\s)|(^\s*[-*]\s)|(^\s*\d+\.\s)|(^\s*---+\s*$)|(```)|(`[^`\n]+`)|(\*\*[^*\n].+?\*\*)|(~~[^~\n].+?~~)|(<u>.+?</u>)|(\*[^*\n]+\*)|(\[[^\]]+\]\([^)]+\))|(^>\s)|(\s*\|)",
    re.MULTILINE,
)
```

And in `_build_outbound_payload()`:
```python
# Remove these lines (4011-4013):
if _MARKDOWN_TABLE_RE.search(content):
    text_payload = {"text": content}
    return "text", json.dumps(text_payload, ensure_ascii=False)
```

## Message Routing Logic

The Feishu adapter has two message types:
- **`post`** (富文本): Supports `md` tag for markdown rendering (bold, lists, code, **and now tables**)
- **`text`** (纯文本): Raw text, no formatting at all

The `_build_outbound_payload()` decision tree:
1. Table detected → forced to `text` (BUG — should go to `post`)
2. Any markdown detected (`_MARKDOWN_HINT_RE`) → `post`
3. No markdown → `text`

## Verification

After patching, restart the gateway (`/restart` or `hermes gateway restart`) and send a message containing a markdown table to confirm it renders correctly.
