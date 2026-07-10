---
name: wechat-article-scraping
description: Extract metadata (authors, titles, text content) from WeChat public account (微信公众号) articles. Covers author-line patterns, anti-bot workarounds, efficient extraction via browser_console, and scale limits.
category: research
tags: [wechat, scraping, browser, camofox, chinese-web]
---

# WeChat Article Scraping

Extract metadata — especially author credits (文字/采写/视频) — from WeChat public account articles and album pages.

## When to use

- User asks to extract author info, titles, or content from WeChat MP articles
- User shares a 微信公众号 album URL and wants a table of authors
- Need to scrape metadata from multiple WeChat articles in bulk

## Anti-bot reality

**WeChat pages aggressively block plain HTTP clients.** Known failure modes:
- Curl returns mostly CSS/JS boilerplate, not article content — the body is loaded dynamically
- Playwright (Python) gets the "环境异常，完成验证后即可继续访问" (environment anomaly) CAPTCHA wall
- Only the **Camofox browser** (what `browser_navigate` uses internally) reliably renders WeChat pages

**Never attempt** `curl`, `playwright`, or `requests` for WeChat pages — they all fail. Go straight to `browser_navigate`.

## Author info patterns

WeChat articles in the "追求卓越的哈工大人" / similar 高校 PR albums consistently place author credits at the very bottom of the article in plain text:

```
文字、排版丨王晨阳           ← combined text+layout credit
文字丨梁英爽                  ← text-only author
采写丨商艳凯                  ← interview/writeup author
文字、视频丨由培远            ← combined text+video credit (rare)
文字&排版丨李双余             ← ampersand variant
文字丨阚思邈 谢梁晖           ← multiple authors
资料来源丨中国青年报等         ← external source, no individual author
```

**Regex to match:**
```
/^(文字|采写|文字、视频|文字、排版|文字&排版)[丨|：:]\s*(.+)/ 
/^视频[丨|：:]\s*(.+)/ (only when NOT preceded by 文字)
```

## Efficient extraction method

### Single article (fastest)

1. `browser_navigate(url)` — load the page
2. `browser_console` with JS extraction:

```js
(() => {
  const text = document.body.innerText;
  const lines = text.split('\n');
  const result = {};
  for (const line of lines) {
    const t = line.trim();
    if (/^(文字|采写|文字、视频|文字、排版)/.test(t)) 
      result.text_author = t.replace(/^(文字|采写|文字、视频|文字、排版)[丨|：:]\s*/, '').trim();
    if (/^视频[丨|：:]/.test(t) && !t.includes('文字'))
      result.video_author = t.replace(/^视频[丨|：:]\s*/, '').trim();
  }
  return JSON.stringify(result);
})()
```

This is much more token-efficient than reading the full page snapshot.

### Album listing (all articles)

1. `browser_navigate("https://mp.weixin.qq.com/mp/appmsgalbum?action=getalbum&__biz=...&album_id=...&count=30")`
2. Use JS to extract all article URLs:

```js
Array.from(document.querySelectorAll('.album__list-item.js_album_item')).map(item => ({
  title: item.getAttribute('data-title'),
  link: item.getAttribute('data-link'),
  pos: item.getAttribute('data-pos_num')
}))
```

## Scale limits — IMPORTANT

Scraping 30+ articles one-by-one via browser navigation takes **~1 minute per article** (browser navigate + extract). With 30 articles, expect ~30 turns / ~15-20 minutes minimum.

**What does NOT work for scaling:**
- `delegate_task` subagents with `browser` toolsets — they time out (600s for 8 articles)
- Curl / Playwright — blocked by WeChat anti-bot
- Any parallelization — Camofox is single-session
- The Camofox HTTP API (`localhost:9377`) doesn't expose `/fetch` or `/render` endpoints

**Pragmatic approach:** If the user asks for "all 30 articles", set expectations early. Offer to do a representative sample first (first 5-10), then ask whether to continue. The author-line pattern becomes clear after 5-6 articles — for albums from the same publisher, the format is extremely consistent.

## Video author rarity

In 高校 promotional article albums (like 哈工大's "追求卓越的哈工大人"), **video authors are almost never credited separately**. Out of a 30-article album, typically 0-2 articles will have a "视频丨XXX" line. Most videos embedded in articles are from news agencies (CCTV, 新华社) and are not separately credited in the article footer.

## Pitfalls

- **Article # not matching URL**: The `data-pos_num` in the album page HTML might differ from the displayed number. Trust the displayed title prefix (e.g. "29. ") over data attributes.
- **Footer format variation**: Some older articles use `编辑&排版丨` or `海報丨` instead of the standard `文字丨` / `排版丨` format. Always scan for `文字`, `采写`, `撰稿` first.
- **External source articles**: Some articles are republished from other outlets with `资料来源丨` lines — these have no individual text author.
