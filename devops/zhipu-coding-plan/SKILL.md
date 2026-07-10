---
name: zhipu-coding-plan
description: Query and manage GLM Coding Plan (智谱编码套餐) usage, subscriptions, and configuration via undocumented APIs and the chelper CLI tool.
version: 1.0.0
tags: [zhipu, bigmodel, coding-plan, usage, subscription, chelper]
triggers:
  - user asks about coding plan usage, balance, quota, or remaining tokens
  - user mentions GLM Coding Plan, 编码套餐, or zhipu subscription
  - user wants to check their zhipu/zai API usage without opening a browser
---

# Zhipu BigModel Coding Plan Management

Manage GLM Coding Plan subscriptions, query token usage, and configure coding tools via CLI — all without opening a browser.

## Quick Usage Check

```bash
# Set your API key (same as the one used for chat completions)
API_KEY="<your-zhipu-api-key>"

# 1. Rate limit & quota status (5-min window)
curl -s "https://open.bigmodel.cn/api/monitor/usage/quota/limit" \
  -H "Authorization: Bearer $API_KEY"

# 2. Model usage over a date range
curl -s "https://open.bigmodel.cn/api/monitor/usage/model-usage?startTime=2026-05-20%2000:00:00&endTime=2026-05-27%2023:59:59" \
  -H "Authorization: Bearer $API_KEY"

# 3. Tool-level usage (Claude Code, Cline, etc.)
curl -s "https://open.bigmodel.cn/api/monitor/usage/tool-usage?startTime=2026-05-20%2000:00:00&endTime=2026-05-27%2023:59:59" \
  -H "Authorization: Bearer $API_KEY"

# 4. Subscription info (plan name, billing, renewal dates)
curl -s "https://open.bigmodel.cn/api/biz/subscription/list" \
  -H "Authorization: Bearer $API_KEY"
```

> **⚠️ URL encoding**: Spaces in query params must be `%20`, not `+` or literal spaces. Failure to encode causes empty responses or timeouts.

## API Reference

### `GET /api/monitor/usage/quota/limit`
Returns current rate-limit window status.

**Response shape:**
```json
{
  "data": {
    "limits": [
      {
        "type": "TIME_LIMIT",       // RPM (requests per window)
        "unit": 5, "number": 1,     // 5-minute window
        "usage": 100,               // max calls in window
        "currentValue": 0,          // used so far
        "remaining": 100,
        "percentage": 0,
        "nextResetTime": 1782283691972,  // epoch ms
        "usageDetails": [...]       // per-tool breakdown
      },
      {
        "type": "TOKENS_LIMIT",     // TPM (tokens per window)
        "unit": 3, "number": 5,     // 5-minute window
        "percentage": 10,           // used %
        "nextResetTime": ...
      }
    ],
    "level": "lite"  // plan tier: lite, pro, etc.
  }
}
```

### `GET /api/monitor/usage/model-usage`
Hourly token usage per model over a date range.

**Params:** `startTime`, `endTime` (format: `YYYY-MM-DD HH:mm:ss`, URL-encoded)

**Response shape:**
```json
{
  "data": {
    "x_time": ["2026-05-20 08:00", ...],
    "tokensUsage": [518611, 0, ...],
    "modelCallCount": [10, 0, ...],
    "totalUsage": {
      "totalModelCallCount": 2230,
      "totalTokensUsage": 127501374,
      "modelSummaryList": [
        {"modelName": "GLM-5.1", "totalTokens": 116521742},
        {"modelName": "GLM-5-Turbo", "totalTokens": 10979331}
      ]
    },
    "modelDataList": [...],
    "granularity": "hourly"
  }
}
```

### `GET /api/biz/subscription/list`
All active subscriptions with billing details.

**Response shape:**
```json
{
  "data": [{
    "id": "209229",
    "productName": "GLM Coding Lite",
    "status": "VALID",
    "valid": "2027-01-24 10:00:00-2028-01-24 10:00:00",
    "actualPrice": 192.00,
    "billingCycle": "annually",
    "currentPeriod": 2
  }]
}
```

## chelper CLI (`@z_ai/coding-helper`)

Official helper tool for managing coding plan integration with IDE tools.

```bash
# Run directly (no install needed)
npx @z_ai/coding-helper

# Or install globally
npm i -g @z_ai/coding-helper
chelper
```

### Key Commands

| Command | Purpose |
|---------|---------|
| `chelper init` | Interactive setup wizard |
| `chelper auth` | Set/manage API key |
| `chelper auth glm_coding_plan_china <key>` | Set China plan key directly |
| `chelper auth reload claude` | Reload plan config into Claude Code |
| `chelper doctor` | Health check (API key, tools, network) |
| `chelper lang set zh_CN` | Switch to Chinese UI |

### Config Location
`~/.chelper/config.yaml`

```yaml
lang: zh_CN
plan: glm_coding_plan_china
api_key: <your-key>
```

## Pitfalls

1. **These APIs are undocumented.** Found by reverse-engineering the `open.bigmodel.cn` SPA webpack chunks (`claude-usage~subscribe-overview.*.js`). They may change without notice.

2. **No official balance/usage API exists in the zhipuai Python SDK.** The SDK (`zhipuai` PyPI package) only has chat/embeddings/files etc. — no billing or usage modules.

3. **URL-encode query parameter spaces.** `startTime=2026-05-20 00:00:00` must be `startTime=2026-05-20%2000:00:00` or curl returns empty/timeout.

4. **Coding Plan API base URL vs Platform API.** The Coding Plan uses `/api/coding/paas/v4` for model calls but `/api/monitor/usage/` and `/api/biz/` for account management — different base paths.

5. **SPA documentation pages.** The docs site (`docs.bigmodel.cn`) is a Mintlify SPA — curl cannot extract content. The control panel (`open.bigmodel.cn`) is also SPA (Vue/webpack). To scrape, you need a headless browser or find the API calls directly from the JS bundles.

## How the APIs Were Discovered

1. Loaded `open.bigmodel.cn/js/runtime.*.js` → found webpack chunk map with chunk names like `claude-usage`, `subscribe-overview`
2. Loaded `claude-usage~subscribe-overview.*.js` → found API URLs: `/monitor/usage/quota/limit`, `/monitor/usage/model-usage`, `/monitor/usage/tool-usage`, `/monitor/usage/model-performance-day`
3. Loaded `app.*.js` → found `/biz/subscription/list`, `/biz/account/query-customer-account-report`
4. Confirmed all endpoints work with `Authorization: Bearer <api_key>` header

## References

- See `references/api-endpoints.md` for the full list of discovered `/biz/` and `/monitor/` endpoints.
