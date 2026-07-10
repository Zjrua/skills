---
name: chinese-university-english-sites
description: Scrape Chinese university English websites — find English site URLs, extract news/articles, count updates by date. Covers HIT, and general patterns for other Chinese universities.
triggers:
  - 大学英文网站
  - university english site
  - 学院英文网站
  - hit.edu.cn english
  - 新闻更新统计
  - college website news count
---

# Chinese University English Site Scraping

Systematically visit Chinese university college/faculty websites, find their English versions, and collect news/article statistics (counts, dates, monthly averages).

## Workflow

### Phase 1: Discover English Site URLs

1. Fetch each Chinese homepage via `curl -sL -m 10 <url>`
2. Search HTML for English site links — multiple naming conventions exist (see URL Patterns below)
3. Filter out false positives: exclude `.css`, `.js`, `simpleNews.css`, `booking-edge.hit.edu.cn`, bare `#` links
4. Verify each English URL returns HTTP 200

### Phase 2: Find News Section

1. Fetch the English homepage
2. Look for nav items with news-related text: `News`, `Events`, `Updates`, `Information`, `动态`, `新闻`
3. Also look for `/list.htm` links — common CMS list page pattern
4. Identify the primary news list URL(s) — some sites have multiple sections (News, Events, Research News)

### Phase 3: Count Articles by Date

1. Fetch the news list page(s)
2. Extract dates using two methods (see Date Extraction below)
3. Handle pagination: `list.htm`, `list2.htm`, `list3.htm`, ...
4. Deduplicate across pages and sections
5. Count articles since target date (e.g., 2026-01-01)

### Phase 4: Calculate Monthly Averages

**Critical**: The user wants **two** time horizons:

1. **Current-year average**: Count 2026 articles ÷ months since earliest 2026 article
   - Find the **earliest** article in the target year (2026)
   - Count months from that date to the current month (inclusive)
   - Example: earliest article is 2026-03-15 → 3 months (Mar, Apr, May) → monthly avg = count / 3
   - If earliest is Jan → 5 months (Jan-May)

2. **All-time average** (建站以来): Count all articles ÷ months since site establishment
   - User correction (2026-05-29): "我说的最早的一篇是英文站建站以来最早的一篇，以免26年刚建站拿5个月除降低月均"
   - Must find the **earliest article ever** on the site, not just 2026
   - Navigate to last page of news list to find oldest article
   - Denominator = months from that earliest date to now (inclusive)
   - This prevents newly-established sites from having inflated "monthly averages"

**When the user says "最早"** without qualification, they mean **建站以来** (since establishment), NOT the earliest in the current year.

## URL Patterns

### HIT (Harbin Institute of Technology) English Sites

| Pattern | Example | Notes |
|---------|---------|-------|
| `en{subdomain}.hit.edu.cn` | `ensa.hit.edu.cn`, `enmse.hit.edu.cn` | Most common |
| `{subdomain}en.hit.edu.cn` | `mathen.hit.edu.cn`, `tyben.hit.edu.cn` | Less common |
| `en.hitwh.edu.cn` / `en.hitsz.edu.cn` | Campuses | Dedicated subdomains |
| `http://{subdomain}.hit.edu.cn/en/` | `som.hit.edu.cn/en/` | Subdirectory |
| `http://{subdomain}.hit.edu.cn/eng` | `civil.hit.edu.cn/eng` | Subdirectory variant |
| `http://{subdomain}.hit.edu.cn/english/` | `seie.hit.edu.cn/english/` | Subdirectory variant |
| `/{ENGLISH}/list.htm` | `future.hit.edu.cn/ENGLISH/list.htm` | Uppercase path |

### General Chinese University Patterns

- `en.{domain}` or `{subdomain}-en.{domain}`
- `/en/`, `/eng/`, `/english/` subdirectories
- Language toggle buttons (top-right, usually "EN" or "English")

## Date Extraction

### ⚠️ CRITICAL: URL dates ≠ news dates

**URL path dates** (e.g., `/2026/0108/page.htm`) represent when the article was **posted to the English site**, NOT when the news happened. Chinese universities batch-translate old Chinese news — an article posted Jan 2026 may report on a November 2025 event.

**The display date** (text shown next to the article link in the list) is the correct news date. Always use display dates for year classification.

**Example**: Article at `/english/2026/0108/c21697a386080/page.htm` with display text "11-14 Professor Chen Yushi Named in Clarivate's 2025 List" → URL says Jan 8 2026, but display date "11-14" = November (2025). This is a 2025 article.

### Date inference logic (display dates without year)

When display dates show only `MM-DD` or `DD Mon` without a year:

1. If display month > current month → year = **previous year** (e.g., "11-14" in May 2026 → November 2025)
2. If display month ≤ current month → year = **current year** (e.g., "05-07" in May 2026 → May 2026)
3. If display date includes explicit year (e.g., "Jan 29, 2026", "2026-01-08") → use as-is

### Common display date formats (HIT examples)

| Format | Site | Example |
|--------|------|---------|
| `DD Mon` | 航天学院 | `26 May`, `20 Apr` |
| `MM-DD` | 电信学院 | `05-07`, `11-14` (NO year!) |
| `YYYY-MM-DD` | 电气学院 | `2026-01-08` |
| `Mon DD, YYYY` | 仪器学院 | `Jan 29, 2026` |
| `DD Mon. YYYY` | 物理学院 | `12 Jan. 2026` |
| `MM.DD.YYYY` | 经管学院 | `05.16.2026` |
| `DD YYYY.MM` | 计算学部 | `06 2025.11` |
| `[ YYYY-MM-DD ]` | 土木学院 | `[ 2026-01-13 ]` |
| `DD Month YYYY` | 体育部 | `27 2026-02` |

### URL path dates (for reference only)

Pattern: `/(YYYY)/(MMDD)/.*?page\\.htm`

```python
url_dates = re.findall(r'/(202[4-6])/(\d{4})/.*?page\.htm', html)
# /2026/0526/ → posted May 26, 2026 (but news may be older)
```

Use URL dates only when no display date is available. Never use them to override display dates.

### Deduplication Strategy

```python
def count_articles(base_url, news_suffixes):
    all_urls = set()  # Deduplicate by article URL
    for suffix in news_suffixes:
        for page in range(1, max_pages + 1):
            url = make_page_url(base_url + suffix, page)
            html = fetch(url)
            articles = re.findall(r'href=["\']([^"\']*page\.htm)["\']', html)
            for a in articles:
                all_urls.normalize_and_add(a, base_url)
    
    # Count by URL date
    count_2026 = sum(1 for u in all_urls if '/2026/' in u)
    return count_2026
```

## Pagination

### HIT-style CMS (SudyCMS / 方正/Founder / 织梦/DedeCMS)

Most HIT English sites use **SudyCMS** (also called 方正Founder CMS). Key characteristics:

- **Dates loaded via JavaScript** — curl returns empty shells for article lists
- News list URL pattern: `/{section_id}/list.htm` (e.g., `/21526/list.htm`)
- Pagination: `list.htm` → `list2.htm` → `list3.htm` → ...
- Article URLs: `/{YYYY}/{MMDD}/c{section}a{article_id}/page.htm`
- **Article IDs in URL** (`aNNNNNN`) are the best dedup key — same article appears in multiple sections with different section codes
- Some sites have multiple news sections: News, Events, Research News, Notices — each is a separate `/{id}/list.htm`

### 675704213 CMS (most non-HIT universities)
- `?page=N` query parameter pagination
- URL pattern: `/listXXXXX.html?page=N`
- Common across 西安交大, 大连理工, 吉林大, 华东理工, etc.

### ASPX sites (graduate school pages)
- `content.aspx?id=N&Page=M` pagination
- Used by: 江西财经, 中南财经, 中央财经, 江西师范大学

### WordPress sites
- `/page/N/` pagination
- Used by: 山东大学 (view.sdu.edu.cn), 温州肯恩大学 (wku.edu.cn), 上海体育学院 (sus.edu.cn)

## Reference Files

- `references/university-url-list.md` — 80+ university English site URLs with pagination types and establishment dates
- `references/hit-english-sites.md` — HIT-specific English site patterns
- `scripts/check_establishment.py` — Check if sites were established before a target year

## Pitfalls

### Excel Cell Format for Zero Values
Writing `0` to an Excel cell with default format → displays as `1900-01-00` (Excel's date serial number). Fix:
```python
cell.number_format = '@'  # Force text format BEFORE writing
cell.value = str(0)
```

### Deduplicate Across Sections by Article ID
Some sites show the same articles in multiple sections. E.g., 化工学院's `News&Events` (`c21752a389908`) and `Latest News` (`c21753a389908`) share articles — only the section code differs. Deduplicate by the `aNNNNNN` article ID part, not the full URL.

### Faculty/Staff Pages ≠ News Pages
数学学院's English site has `/list.htm` pages that are faculty directories, not news. Profile links contain date-like URL paths (e.g., `/2026/0426/c22193a390907/page.htm`) but these are staff profile pages. Verify by checking if the page contains article titles vs person names + contact info.

### Pagination: Server vs JS
- Server-rendered: `list.htm`, `list2.htm`, `list3.htm` — curl works, stop when no `page.htm` links
- JavaScript: pagination buttons with `javascript:void(0)` — need browser
- Some pages 2+ exist but return empty HTML (航天学院) — verify with browser if curl results seem low

### Camofox Stale Tab / 500 Errors
When `browser_navigate` returns `500 Server Error`, the tab is stale. Fix:
```bash
# Clear ALL sessions (nuclear option)
curl -s -X DELETE "http://localhost:9377/sessions/agent1"
# Or clear specific session
curl -s -X DELETE "http://localhost:9377/sessions/{userId}"
```
Then retry — the browser tools will create a fresh tab.

**Camofox limitations**:
- `/execute` endpoint does NOT exist — cannot evaluate JavaScript via API
- `full=true` parameter on snapshot doesn't add much content
- Pages with heavy JS need 4-6 seconds wait time after navigation
- Scroll + re-snapshot is the best way to capture lazy-loaded content

### Browser Service Startup
When Camofox is down, subagents with `browser` toolset fail silently. Start it:
```bash
cd /tmp/camofox-install/camofox-browser-master && node server.js
curl -s http://localhost:9377/health  # verify
```

### JS-Loaded Content Is Invisible to curl
Some sites (e.g., `som.hit.edu.cn/en/`) load news via JavaScript. curl returns empty shell HTML. Use browser for these sites.

### Camofox DNS Resolution Failures
Some Chinese university sites (e.g., en.ctgu.edu.cn) fail with `NS_ERROR_UNKNOWN_HOST` when accessed via Camofox. This is a DNS issue from the server's network location. Workaround: use curl with user-agent header, or skip inaccessible sites.

### Playwright as Alternative to Camofox
When Camofox is broken or insufficient, use Playwright chromium directly. Key gotchas:

**Installation**:
```bash
pip install playwright --break-system-packages  # or in correct venv
playwright install chromium  # Downloads main chromium
# ⚠️ Must ALSO install headless shell separately:
playwright install chromium  # Second run downloads chromium_headless_shell
# Verify: ls /root/.cache/ms-playwright/chromium_headless_shell-*/
```

**Hermes venv mismatch**: Hermes uses python3.11 venv at `/root/.hermes/hermes-agent/venv/bin/python3`, but system pip installs to `/usr/local/lib/python3.12/`. Use `/usr/bin/python3` for Playwright scripts.

**Batch scraping pattern** (80+ sites):
```python
from playwright.sync_api import sync_playwright
import re, time

def find_dates(text):
    dates = []
    for m in re.finditer(r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', text):
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if 2000 <= y <= 2026 and 1 <= mo <= 12 and 1 <= d <= 31:
            dates.append((y, mo, d))
    # Also match: YYYY年MM月DD日, English formats
    return dates

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    for name, url in sites:
        ctx = b.new_context(user_agent='Mozilla/5.0 ...')  # NEW context per site
        pg = ctx.new_page()
        try:
            pg.goto(url, timeout=20000, wait_until='networkidle')  # NOT domcontentloaded
            time.sleep(2)
            dates = find_dates(pg.content())
            if not dates:
                dates = find_dates(pg.inner_text('body'))  # Fallback for JS-rendered
        finally:
            pg.close(); ctx.close()
    b.close(); p.stop()
```

**Key patterns**:
- Create new `context` per site (don't reuse — causes stale pages)
- Use `wait_until='networkidle'` not `'domcontentloaded'` for JS-rendered Chinese sites
- `page.inner_text('body')` as fallback when `page.content()` returns empty shells
- Many URLs return 404 — sites change URL structures frequently
- Run with `/usr/bin/python3` not `python3` (venv mismatch)
- 80+ sites takes ~10-15 min; use `timeout 580` wrapper

### Finding the Earliest (Oldest) Article on a Site

When the user asks for the earliest article since site establishment:

1. Fetch the news list page (page 1)
2. Check for pagination: `re.findall(r'list(\d+)\.htm', html)` → get max page
3. Navigate to the LAST page (`listN.htm`) — oldest articles are there
4. Extract dates from the last page
5. If no pagination exists, all articles are on page 1 — the oldest visible is the oldest

**For JS-rendered SudyCMS sites**: curl won't show dates. Use browser:
```bash
# Via Camofox API
curl -s -X POST "http://localhost:9377/tabs" \
  -H "Content-Type: application/json" \
  -d '{"userId":"find","sessionKey":"s1","url":"<news_list_url>"}'
sleep 5
curl -s "http://localhost:9377/tabs/<tabId>/snapshot?userId=find"
```
Look for dates in the accessibility tree snapshot text.

**For sites with no pagination but many articles**: Check if article IDs are sequential.
Lower IDs = older articles. E.g., `/info/1020/1463.htm` is older than `/info/1020/1511.htm`.

### Subagent Timeout Issues
When delegating site checking to subagents, limit each batch to 10-15 sites max. Subagents checking 20+ sites consistently timeout after 600s. Split large lists into smaller batches.

### Date Format Variations
Chinese university sites use multiple date formats:
- `YYYY-MM-DD` or `YYYY/MM/DD` (most common)
- `YYYY年MM月DD日` (Chinese format)
- `DD Mon YYYY` (English format, e.g., "15 Jan 2026")
- `Mon DD, YYYY` (US format, e.g., "Jan 15, 2026")
- `MM-DD` without year (requires inference from context)

Always check multiple patterns when extracting dates.

### False Positive English Links
Filter out: `.css`, `.js`, `simpleNews.css`, `booking-edge.hit.edu.cn`, bare `#`, `_js/_portletPlugs/`

### Date Extraction Double-Counting
The same article can produce multiple date matches in HTML. Always deduplicate by unique article URL.

### Monthly Average Calculation
User correction: "有的可能2026年3月才开通，那到现在就是3个月，别都用6个月除"
- Count months inclusively: Mar-May = 3 months
- Only count from earliest article's month in target year
- No articles → average is 0

### Determining Site Establishment Date
When calculating monthly averages, the denominator depends on when the English site was established:
- If site has articles from before 2026 → denominator = 5 (Jan-May 2026)
- If site was established in 2026 (e.g., March) → denominator = (5 - month + 1)

**Efficient approach**: Only check sites where the earliest 2026 article is AFTER January. Sites with January articles don't need checking (denominator = 5 regardless).

**User correction**: "我说的最早的一篇是英文站建站以来最早的一篇，以免26年刚见站拿5个月除降低月均" — The denominator should be based on the site's ESTABLISHMENT date (earliest article ever), not just the earliest article in the target year. If a site was established in March 2026, denominator = 5-3+1 = 3, not 5.

**Verification**: For late sites, fetch the homepage and look for pre-2026 dates:
```bash
curl -sL -m 8 "https://site.edu.cn/" | grep -oP '20(2[0-5]|1[0-9])[-/]\d{2}' | sort | head -3
```
If pre-2026 dates exist → site was established before 2026 → denominator = 5.

## Example: Full Pipeline for One Site

```python
import subprocess, re
from datetime import datetime

# 1. Fetch Chinese homepage, find English link
r = subprocess.run(["curl", "-sL", "-m", "10", "http://sa.hit.edu.cn/"], 
                   capture_output=True, text=True, timeout=15)
en_links = re.findall(r'href=["\']([^"\']*(?:en\.hit|/en)[^"\']*)["\']', r.stdout, re.I)
# → https://ensa.hit.edu.cn/

# 2. Fetch English homepage, find news section
r = subprocess.run(["curl", "-sL", "-m", "10", "https://ensa.hit.edu.cn/"], 
                   capture_output=True, text=True, timeout=15)
news_links = re.findall(r'href=["\']([^"\']*(?:/list\.htm)[^"\']*)["\']', r.stdout)
# → /20665/list.htm

# 3. Fetch news list, extract articles with display dates
r = subprocess.run(["curl", "-sL", "-m", "10", "https://ensa.hit.edu.cn/20665/list.htm"],
                   capture_output=True, text=True, timeout=15)

# Extract articles: link text has "DD Mon Title" format
articles = re.findall(r'link "(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(.+?)"', r.stdout)

# 4. Classify by display date (NOT URL date)
# "26 May ..." → May 2026 ✓, "11-14 ..." → Nov 2025 ✗ (month > current month)
# → 6 articles from 2026 on this page
```
