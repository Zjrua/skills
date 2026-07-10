---
name: feishu-card-callback-workaround
description: Known Feishu messaging platform quirks and fixes in Hermes gateway — card callbacks, table rendering, post-type limitations
---

# Hermes Feishu Platform — Known Quirks & Fixes

This skill documents verified issues in Hermes Agent's Feishu gateway adapter (`gateway/platforms/feishu.py`) and their fixes.

---

## 1. Markdown Table Rendering in Post Messages (2026-05-26)

**See `references/feishu-table-rendering.md` for full details.**

### What happened
`_build_outbound_payload()` (line ~4007) had logic that detected markdown tables and **downgraded them to `text` msg_type**, assuming Feishu post-type `md` elements couldn't render tables. This made tables appear as raw `|---|---|` text.

### Fix
Removed the downgrade block. Post-type messages **do** render markdown tables correctly — the original assumption was wrong. Tables now flow through the normal `_MARKDOWN_HINT_RE` → `post` path.

### Key file
`gateway/platforms/feishu.py`, method `_build_outbound_payload()` (line ~4007).

---

## 2. Interactive Card Callbacks in WebSocket Mode (2026-04-12)

## Problem

In Feishu **WebSocket mode**, clicking an interactive card button (e.g. approval buttons) causes a loading spinner, then reverts to the original card with error code **11310** — the backend action may or may not succeed.

## Root Cause (Verified 2026-04-12)

The Python `lark-oapi` SDK's WebSocket client (`lark_oapi/ws/client.py`) **silently drops ALL CARD-type messages** at the frame handler level:

```python
# lark_oapi/ws/client.py — _handle_data_frame()
if message_type == MessageType.EVENT:
    result = self._event_handler.do_without_validation(pl)
elif message_type == MessageType.CARD:
    return  # ← CARD messages are NEVER dispatched!
else:
    return
```

This means:
1. `_on_card_action_trigger` is **never called** in WebSocket mode
2. The `P2CardActionTriggerResponse` return value is irrelevant (code never runs)
3. Error 11310 = Feishu client timeout waiting for a response that never comes
4. Any `button resolved` logs you see are from **webhook mode** or other paths

**This is a hard SDK bug**, not a timing/serialization issue.

## OpenClaw's Approach (Reference)

The `openclaw-feishu` (667⭐) and `feishu-openclaw` (322⭐) projects **completely avoid interactive cards**:
- Only register `im.message.receive_v1` — no `card_action_trigger` at all
- Approval handled in local CLI SDK, not Feishu UI
- "Thinking" uses plain text `"正在思考…"` + `updateMessage` API
- Confirms this is a known community limitation

## Fix: Monkey-patch `_handle_data_frame`

In `gateway/platforms/feishu.py`, function `_run_official_feishu_ws_client()`, patch the WS client's `_handle_data_frame` to dispatch CARD messages through `do_without_validation()`:

```python
# After ws_client is created, before ws_client.start():
_stock_handle_data_frame = ws_client._handle_data_frame

async def _handle_data_frame_with_card_support(frame):
    from lark_oapi.ws.enum import MessageType
    from lark_oapi.ws.model import Response
    import time, base64
    from lark_oapi.core.json import JSON
    from lark_oapi.core.const import UTF_8

    hs = frame.headers
    type_ = ws_client_module._get_by_key(hs, ws_client_module.HEADER_TYPE)
    pl = frame.payload
    sum_ = ws_client_module._get_by_key(hs, ws_client_module.HEADER_SUM)
    msg_id = ws_client_module._get_by_key(hs, ws_client_module.HEADER_MESSAGE_ID)

    if int(sum_) > 1:
        pl = ws_client._combine(msg_id, int(sum_),
            int(ws_client_module._get_by_key(hs, ws_client_module.HEADER_SEQ)), pl)
        if pl is None:
            return

    message_type = MessageType(type_)
    resp = Response(code=ws_client_module.http.HTTPStatus.OK)
    try:
        start = int(round(time.time() * 1000))
        if message_type == MessageType.EVENT:
            result = ws_client._event_handler.do_without_validation(pl)
        elif message_type == MessageType.CARD:
            result = ws_client._event_handler.do_without_validation(pl)
        else:
            return
        end = int(round(time.time() * 1000))
        header = hs.add()
        header.key = ws_client_module.HEADER_BIZ_RT
        header.value = str(end - start)
        if result is not None:
            resp.data = base64.b64encode(JSON.marshal(result).encode(UTF_8))
    except Exception as e:
        logger.error("[Feishu] handle WS message failed, type=%s, err: %s",
                      message_type.value, e)
        resp = Response(code=ws_client_module.http.HTTPStatus.INTERNAL_SERVER_ERROR)

    frame.payload = JSON.marshal(resp).encode(UTF_8)
    await ws_client._write_message(frame.SerializeToString())

ws_client._handle_data_frame = _handle_data_frame_with_card_support
```

## Fix: Double-guarantee with `message.update` API

Even after the monkey-patch, also call `_update_approval_card()` proactively in `_handle_approval_action_sync()` — this provides a fallback visual update via the REST API:

```python
# In _handle_approval_action_sync(), after resolve_gateway_approval():
await self._update_approval_card(
    state.get("message_id", ""), label, user_name, choice
)
# Still return the card in the callback response (works in webhook mode too)
```

## Files Involved

- `gateway/platforms/feishu.py`:
  - `_run_official_feishu_ws_client()` (line ~947) — monkey-patch location
  - `_on_card_action_trigger()` (line ~1837) — sync callback handler
  - `_handle_approval_action_sync()` (line ~1957) — approval processing + update
  - `_update_approval_card()` (line ~1483) — REST API card update
- `gateway/run.py` — `_approval_notify_sync()` (line ~7437) sends the approval card

## SDK Source Reference

- `lark_oapi/ws/client.py` line 264: `elif message_type == MessageType.CARD: return`
- `lark_oapi/ws/const.py`: `HEADER_TYPE`, `HEADER_SUM`, `HEADER_MESSAGE_ID`, etc.
- `lark_oapi/ws/model.py`: `Response` class
- `lark_oapi/ws/enum.py`: `MessageType.CARD`

## Important Notes

1. **Module-level functions**: `_get_by_key` is a module-level function in `lark_oapi.ws.client`, accessed via `ws_client_module._get_by_key`
2. **Constants**: `HEADER_*` are in `lark_oapi.ws.const`, imported into the client module via `from lark_oapi.ws.const import *`
3. **WebSocket mode only affects Feishu (China)** — Lark (international) must use webhook mode
4. **Error 11310** = card action trigger failed / timeout — the telltale sign of this bug
5. **First click always 11310, subsequent clicks may not** — Feishu client does dedup/dedgradation after first timeout

## Rollback
If issues arise: `cd /root/.hermes/hermes-agent && git checkout -- gateway/platforms/feishu.py`

## Verification
Fix was applied and gateway restarted on 2026-04-12. **Pending user verification** — send a command that triggers exec_approval to confirm card button updates correctly.
