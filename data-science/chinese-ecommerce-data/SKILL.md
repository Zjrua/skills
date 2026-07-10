---
name: chinese-ecommerce-data
description: Get product data (prices, titles, sales) from Chinese e-commerce platforms (Taobao, JD, PDD). Covers why browser automation fails and practical bypass methods.
---

# Chinese E-commerce Data Acquisition

## Core Problem

Chinese e-commerce platforms (Taobao, JD, PDD) **require login** to return search results. When browser automation shows "加载中..." with empty product lists, the root cause is **missing login cookies**, not a simple anti-scraping detection.

## Available Tools (verified in Hermes sandbox)

| Tool | Version | Use |
|------|---------|-----|
| DrissionPage | 4.1.1.2 | Cookie injection + browser automation |
| Playwright + stealth | 1.58.0 | Stealth browser automation |
| undetected-chromedriver | 3.5.5 | Anti-detection Chrome driver |
| curl_cffi | 0.15.0 | TLS fingerprint impersonation |
| lark-cli | global | Create/update Feishu documents |

## Recommended Approach (by priority)

### 1. Cookie Injection + DrissionPage (fastest, short-term)

```python
from DrissionPage import ChromiumPage, ChromiumOptions

co = ChromiumOptions()
co.set_browser_path('/usr/bin/google-chrome')
co.headless()
co.set_argument('--no-sandbox')
co.set_argument('--disable-blink-features=AutomationControlled')

page = ChromiumPage(co)
page.get('https://www.taobao.com')
# Inject user's cookies (from browser F12)
for cookie in cookies:
    page.set.cookies(cookie)
page.get('https://s.taobao.com/search?q=KEYWORD')
# Extract items with CSS selectors
```

**Get cookies from user**: Ask them to log in to taobao.com in their browser, F12 → Console → run:
```js
copy(document.cookie.split('; ').map(c => {
  const [k,v] = c.split('=');
  return JSON.stringify({name:k, value:v, domain:'.taobao.com'});
}).join(',\n'))
```

### 2. Official Affiliate APIs (best long-term, free)

| Platform | API | URL | Setup Time |
|----------|-----|-----|------------|
| Taobao/Tmall | `taobao.tbk.dg.material.optional` | pub.alimama.com | 1-2 days |
| JD | `jd.union.open.goods.query` | union.jd.com/openplatform | 1-3 days |
| PDD | `pdd.ddk.goods.search` | jinbao.pinduoduo.com | 1-2 days |

All free, all require real-name registration. Return: title, price, coupons, sales, shop info.

### 3. RapidAPI (quick prototype)

Search for "Taobao Search API" or "JD Search API" on rapidapi.com. Free tiers available (~100 calls/month).

## Platforms That Also Block

- 拼多多 (PDD) — login required
- 什么值得买 (SMZDM) — Cloudflare + no API
- 慢慢买 — no public API
- 知乎 — verification required for content

## Document Output

When chatting on Feishu, always generate results as a Feishu document using `lark-cli`:

```bash
lark-cli docs +create --title "标题" --markdown "$(cat <<'EOF'
# Markdown content here
EOF
)"
```

## Pitfalls

- Camofox browser cannot bypass Chinese e-commerce login walls — use DrissionPage or Playwright instead
- Cookies expire (days to weeks) — need periodic refresh
- Camofox does not support `browser_console` for JS evaluation on these sites
- Bing search can partially extract price info from Zhihu/Chiphell discussions as a fallback
