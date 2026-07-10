# Zhipu BigModel Console API Endpoints

Reverse-engineered from `open.bigmodel.cn/js/app.*.js` webpack bundle.
All endpoints use `Authorization: Bearer <api_key>` header. Base URL: `https://open.bigmodel.cn/api`.

## Account & Billing

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/biz/account/query-customer-account-report` | GET | Account balance (recharge, spend, available balance) |
| `/biz/account/getAccountBalanceEnough` | GET | Boolean: is balance sufficient |
| `/biz/recharge/getRechargeAmount` | GET | Recharge amounts |
| `/biz/recharge/user-recharge-list` | GET | Recharge history |
| `/biz/product/info` | GET | Product details |
| `/biz/product/createPreOrder` | POST | Create pre-order |
| `/biz/product/isLimitBuy` | GET | Check if product is limited purchase |
| `/biz/product/overview` | GET | Product overview |
| `/biz/pay/create-sign` | POST | Create payment sign |
| `/biz/pay/unsubscribe` | POST | Unsubscribe |
| `/biz/pay/status?key=` | GET | Payment status |
| `/biz/pay/batch-preview` | GET | Batch payment preview |

## Subscriptions

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/biz/subscription/list` | GET | All active subscriptions with billing info |
| `/biz/subscription/v1-coding-plan-auto-renew-closed-by-system` | GET | Check if auto-renew was closed by system |

## Usage Monitoring (Coding Plan)

| Endpoint | Method | Params | Purpose |
|----------|--------|--------|---------|
| `/monitor/usage/quota/limit` | GET | — | Current rate limit window (RPM/TPM) |
| `/monitor/usage/model-usage` | GET | `startTime`, `endTime` | Hourly token usage per model |
| `/monitor/usage/tool-usage` | GET | `startTime`, `endTime` | Usage per coding tool (Claude Code, etc.) |
| `/monitor/usage/model-performance-day` | GET | `startTime`, `endTime` | Daily model performance stats |

**Date param format:** `YYYY-MM-DD HH:mm:ss` (URL-encode spaces as `%20`)

## Customer

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/biz/customer/getCustomerInfo` | GET | Current user info |
| `/biz/customer/getTokenMagnitude?productId=` | GET | Token magnitude for product (returns 500 for coding plan products) |
| `/biz/customer/accountSet` | GET/POST | Account settings |
| `/biz/customer/risk/info` | GET | Account risk info |

## Token Packs

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/biz/tokenAccounts/isLimitBuy` | GET | Token pack limit check |
| `/biz/tokenAccounts/query-order/` | GET | Token pack order query |
| `/biz/tokenResPack/productIdInfo` | GET | Resource pack info by product ID |

## Response Format

All endpoints return:
```json
{
  "code": 200,
  "msg": "操作成功",
  "data": { ... },
  "success": true
}
```

Error: `{"code": 500, "msg": "404 NOT_FOUND", "data": null, "success": false}`

## Product IDs (as of 2026-05)

| Product ID | Name |
|-----------|------|
| `product-060148` | GLM Coding Lite (annual) |
| `product-02434c` | GLM Coding Lite (monthly) |
