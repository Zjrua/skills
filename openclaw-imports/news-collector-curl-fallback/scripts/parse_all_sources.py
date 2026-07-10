#!/usr/bin/env python3
"""
Multi-source news parser for the daily-news-collector curl fallback path.

USAGE:
  1. Fetch all sources via curl (see SKILL.md for curl commands):
     curl -s --connect-timeout 10 --max-time 15 "https://www.cls.cn/" -o /tmp/cls_home.html
     curl -s ... "https://api-one.wallstcn.com/apiv1/content/lives?channel=global-channel&limit=20" -o /tmp/wallstcn.json
     curl -s ... "https://api-one.wallstcn.com/apiv1/content/articles?channel=ai-channel&limit=10" -o /tmp/wallstcn_ai.json
     curl -s ... "https://36kr.com/newsflashes" -o /tmp/36kr.html
     curl -s ... "https://finance.sina.com.cn/7x24/" -o /tmp/sina7x24.html
     curl -s ... "https://www.ithome.com/" -o /tmp/ithome.html
     curl -s ... "https://www.news.cn/" -o /tmp/newsxinhua.html
     curl -s ... "https://www.people.com.cn/" -o /tmp/people.html
     curl -s ... "https://www.thepaper.cn/" -o /tmp/thepaper.html
     curl -s ... "https://www.yicai.com/" -o /tmp/yicai.html
  2. Run: python3 scripts/parse_all_sources.py
  3. Read structured output from stdout — each source section clearly labeled.

EXPECTED YIELDS (2026-07-03 baseline):
  CLS首页:       ~30 items (depth_list + hotArticleData via __NEXT_DATA__)
  Wallst lives:  20 items (JSON API)
  Wallst AI:     2-4 unique items (JSON API, dedup by .uri)
  36kr:          20 items (itemList bracket matching)
  Sina 7x24:     ~25 items (regex on 7x24/{id} links)
  IT之家:        300+ items (robust <a> tag extraction, no date filter)
  Xinhua:        ~20 items (<a> tag regex with keyword filtering)
  People:        ~20 items (<a> tag regex with keyword filtering)
  ThePaper:      4-5 items (__NEXT_DATA__ recommendChannels)
  第一财经:       0-3 items (__NEXT_DATA__ often missing; <a> fallback yields ads)

NOTE: Some source files may not exist (curl failed). The script handles missing
files gracefully — it prints an error for that source and continues to the next.
"""
import json, re, time, html as html_mod, os

def clean(text):
    """Strip HTML tags and unescape entities."""
    if not text:
        return ''
    text = re.sub(r'<[^>]+>', '', str(text))
    return html_mod.unescape(text).strip()

def fmt_time(ts):
    """Format unix timestamp as MM-DD HH:MM."""
    if not ts:
        return '?'
    try:
        return time.strftime('%m-%d %H:%M', time.localtime(ts))
    except Exception:
        return '?'

def safe_read(path):
    """Read file content, return None if missing."""
    try:
        with open(path, 'r', errors='replace') as f:
            return f.read()
    except FileNotFoundError:
        print(f"  ⚠️ File not found: {path} — source skipped")
        return None
    except Exception as e:
        print(f"  ⚠️ Error reading {path}: {e}")
        return None

def parse_cls_home():
    """Parse CLS首页 __NEXT_DATA__ for depth_list + hotArticleData."""
    print("=" * 60)
    print("📊 SOURCE 1: CLS首页 (__NEXT_DATA__)")
    print("=" * 60)
    raw = safe_read('/tmp/cls_home.html')
    if not raw:
        return
    start = raw.find('__NEXT_DATA__" type="application/json">')
    if start < 0:
        # Regex fallback: extract /detail/{id} links
        print("  __NEXT_DATA__ not found, using regex fallback")
        news_links = re.findall(r'href="(/detail/\d+)"[^>]*>(.*?)</a>', raw, re.DOTALL)
        seen = set()
        for link, raw_text in news_links:
            nid = link.split('/')[-1]
            if nid in seen:
                continue
            seen.add(nid)
            title = clean(raw_text)
            if title and len(title) > 5:
                print(f"  https://www.cls.cn/detail/{nid}")
                print(f"    {title[:120]}")
        return

    json_start = raw.find('>', start) + 1
    json_end = raw.find('</script>', json_start)
    try:
        data = json.loads(raw[json_start:json_end])
    except json.JSONDecodeError as e:
        print(f"  JSON parse error: {e}")
        return

    pp = data.get('props', {}).get('pageProps', {})
    assemble = pp.get('assembleData', {})

    print("\n--- depth_list (深度) ---")
    for item in assemble.get('depth_list', [])[:20]:
        tid = item.get('id', '')
        title = clean(item.get('title', ''))
        brief = clean(item.get('brief', ''))[:150]
        ctime = item.get('ctime', 0)
        print(f"  [{fmt_time(ctime)}] https://www.cls.cn/detail/{tid}")
        print(f"    {title}")
        if brief:
            print(f"    摘要: {brief}")

    print("\n--- hotArticleData (热门) ---")
    for item in pp.get('hotArticleData', [])[:15]:
        tid = item.get('id', '')
        title = clean(item.get('title', ''))
        brief = clean(item.get('brief', ''))[:150]
        ctime = item.get('ctime', 0)
        print(f"  [{fmt_time(ctime)}] https://www.cls.cn/detail/{tid}")
        print(f"    {title}")
        if brief:
            print(f"    摘要: {brief}")


def parse_wallst_lives():
    """Parse华尔街见闻 lives JSON API."""
    print("\n" + "=" * 60)
    print("📊 SOURCE 2: 华尔街见闻 lives (JSON API)")
    print("=" * 60)
    raw = safe_read('/tmp/wallstcn.json')
    if not raw:
        return
    try:
        data = json.loads(raw)
        items = data.get('data', {}).get('items', [])
        for item in items[:20]:
            title = item.get('title', '') or ''
            content = clean(item.get('content_text', ''))[:200]
            dt = item.get('display_time', 0)
            print(f"  [{fmt_time(dt)}] {title}")
            if content:
                print(f"    内容: {content}")
    except Exception as e:
        print(f"  ERROR: {e}")


def parse_wallst_ai():
    """Parse华尔街见闻 AI articles JSON API."""
    print("\n" + "=" * 60)
    print("📊 SOURCE 3: 华尔街见闻 AI articles (JSON API)")
    print("=" * 60)
    raw = safe_read('/tmp/wallstcn_ai.json')
    if not raw:
        return
    try:
        data = json.loads(raw)
        items = data.get('data', {}).get('items', [])
        seen_uri = set()
        for item in items[:10]:
            uri = item.get('uri', '')
            if uri in seen_uri:
                continue
            seen_uri.add(uri)
            title = item.get('title', '') or ''
            content = clean(item.get('content_text', ''))[:200]
            print(f"  {title}")
            if uri:
                print(f"    链接: {uri}")
            if content:
                print(f"    内容: {content}")
    except Exception as e:
        print(f"  ERROR: {e}")


def parse_36kr():
    """Parse 36氪快讯 via itemList bracket matching."""
    print("\n" + "=" * 60)
    print("📊 SOURCE 4: 36氪快讯")
    print("=" * 60)
    raw = safe_read('/tmp/36kr.html')
    if not raw:
        return
    idx = raw.find('"itemList":[{')
    if idx < 0:
        print("  itemList not found")
        return
    bracket_start = raw.find('[', idx)
    depth = 0
    i = bracket_start
    item_list_str = None
    while i < len(raw):
        if raw[i] == '[':
            depth += 1
        elif raw[i] == ']':
            depth -= 1
            if depth == 0:
                item_list_str = raw[bracket_start:i + 1]
                break
        i += 1
    if not item_list_str:
        print("  Could not extract itemList array")
        return
    try:
        items = json.loads(item_list_str)
        for item in items[:20]:
            mat = item.get('templateMaterial', {})
            title = clean(mat.get('widgetTitle', ''))
            content = clean(mat.get('widgetContent', ''))[:200]
            pub_time = mat.get('publishTime', 0)
            ts = fmt_time(pub_time / 1000) if pub_time else '?'
            print(f"  [{ts}] {title}")
            if content:
                print(f"    内容: {content}")
    except Exception as e:
        print(f"  ERROR: {e}")


def parse_sina_7x24():
    """Parse新浪7×24快讯 via regex."""
    print("\n" + "=" * 60)
    print("📊 SOURCE 5: 新浪7×24快讯")
    print("=" * 60)
    raw = safe_read('/tmp/sina7x24.html')
    if not raw:
        return
    # Primary: 7x24/{id} links with 15+ char text
    matches = re.findall(r'href="[^"]*7x24/(\d+)"[^>]*>([^<]{15,})</a>', raw)
    seen = set()
    count = 0
    for sid, title in matches:
        title = clean(title)
        if title and title not in seen and len(title) > 15:
            seen.add(title)
            count += 1
            print(f"  [{sid}] {title[:120]}")
            if count >= 25:
                break
    # Fallback: 【标题】pattern
    if count == 0:
        matches2 = re.findall(r'>(【[^】]+】[^<]{10,})<', raw)
        for m in matches2[:25]:
            print(f"  {clean(m)[:120]}")


def parse_ithome():
    """Parse IT之家 via robust <a> tag extraction (no date filter)."""
    print("\n" + "=" * 60)
    print("📊 SOURCE 6: IT之家")
    print("=" * 60)
    raw = safe_read('/tmp/ithome.html')
    if not raw:
        return
    a_matches = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>([^<]+)</a>', raw)
    seen = set()
    results = []
    skip_kw = ['系统镜像', '描述文件', '下载大全', 'Win11', 'Win10', 'iOS描述']
    for url, title in a_matches:
        title = clean(title)
        is_ithome = ('ithome.com' in url) or (url.startswith('/') and not url.startswith('//'))
        if is_ithome and len(title) > 8 and url not in seen:
            if any(k in title for k in skip_kw):
                continue
            seen.add(url)
            results.append((url, title))
    for url, title in results[:30]:
        full_url = url if url.startswith('http') else f"https://www.ithome.com{url}"
        print(f"  {title[:100]}")
        print(f"    -> {full_url[:100]}")
    print(f"  Total: {len(results)} items")


def parse_xinhua():
    """Parse新华社 via <a> tag regex."""
    print("\n" + "=" * 60)
    print("📊 SOURCE 7: 新华社 (news.cn)")
    print("=" * 60)
    raw = safe_read('/tmp/newsxinhua.html')
    if not raw:
        return
    links = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>([^<]{8,60})</a>', raw)
    seen = set()
    skip = ['首页', '登录', '注册', '下载', '客服', '关于', '更多', '频道',
            '导航', '新华炫闻', '客户端', 'Français', 'Русский', 'Português']
    count = 0
    for url, title in links:
        title = clean(title)
        if len(title) >= 8 and title not in seen and not any(x in title for x in skip):
            seen.add(title)
            count += 1
            print(f"  {title}")
            if count >= 20:
                break


def parse_people():
    """Parse人民网 via <a> tag regex."""
    print("\n" + "=" * 60)
    print("📊 SOURCE 8: 人民网 (people.com.cn)")
    print("=" * 60)
    raw = safe_read('/tmp/people.html')
    if not raw:
        return
    links = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>([^<]{8,60})</a>', raw)
    seen = set()
    skip = ['首页', '登录', '注册', '下载', '客服', '关于', '更多', '频道',
            '导航', 'Follow Xi']
    count = 0
    for url, title in links:
        title = clean(title)
        if len(title) >= 8 and title not in seen and not any(x in title for x in skip):
            seen.add(title)
            count += 1
            print(f"  {title}")
            if count >= 20:
                break


def parse_thepaper():
    """Parse澎湃新闻 via __NEXT_DATA__ recommendChannels."""
    print("\n" + "=" * 60)
    print("📊 SOURCE 9: 澎湃新闻 (thepaper.cn)")
    print("=" * 60)
    raw = safe_read('/tmp/thepaper.html')
    if not raw:
        return
    m = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>', raw, re.DOTALL)
    if m:
        try:
            data = json.loads(m.group(1))
            pp = data.get('props', {}).get('pageProps', {})
            page_data = pp.get('data', pp)
            channels = page_data.get('recommendChannels', [])
            if not channels:
                for key in pp:
                    val = pp[key]
                    if isinstance(val, dict):
                        channels = val.get('recommendChannels', [])
                        if channels:
                            break
            for ch in channels:
                for item in ch.get('contentList', [])[:5]:
                    name = item.get('name', '')
                    contId = item.get('contId', '')
                    print(f"  {name}")
                    if contId:
                        print(f"    -> https://www.thepaper.cn/newsDetail_cont_{contId}")
        except Exception as e:
            print(f"  JSON parse error: {e}")
    else:
        print("  __NEXT_DATA__ not found")
    # Generic fallback
    a_titles = re.findall(r'<a[^>]*>([^<]{15,80})</a>', raw)
    seen = set()
    count = 0
    for t in a_titles:
        t = clean(t)
        if len(t) > 15 and t not in seen:
            seen.add(t)
            count += 1
            print(f"  (generic) {t[:100]}")
            if count >= 10:
                break


def parse_yicai():
    """Parse第一财经 via __NEXT_DATA__ or <a> fallback."""
    print("\n" + "=" * 60)
    print("📊 SOURCE 10: 第一财经 (yicai.com)")
    print("=" * 60)
    raw = safe_read('/tmp/yicai.html')
    if not raw:
        return
    m = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>', raw, re.DOTALL)
    if m:
        try:
            data = json.loads(m.group(1))
            pp = data.get('props', {}).get('pageProps', {})
            found_any = False
            for key, val in pp.items():
                if isinstance(val, list) and len(val) > 0 and isinstance(val[0], dict):
                    found_any = True
                    print(f"\n  --- {key} ({len(val)} items) ---")
                    for item in val[:10]:
                        title = item.get('title', '') or item.get('name', '') or ''
                        if title:
                            print(f"    {clean(title)[:100]}")
            if not found_any:
                print("  __NEXT_DATA__ found but no list data in pageProps")
        except Exception as e:
            print(f"  JSON parse error: {e}")
    else:
        print("  __NEXT_DATA__ not found, using <a> tags")
    # Generic fallback
    a_titles = re.findall(r'<a[^>]*href="([^"]*)"[^>]*>([^<]{15,100})</a>', raw)
    seen = set()
    count = 0
    skip = ['首页', '登录', '更多', '下载', '客户端', '关于', '联系']
    for url, title in a_titles:
        title = clean(title)
        if len(title) > 15 and title not in seen and not any(x in title for x in skip):
            seen.add(title)
            count += 1
            print(f"  {title[:100]}")
            if count >= 15:
                break


def main():
    """Parse all available sources and print structured output."""
    parse_cls_home()
    parse_wallst_lives()
    parse_wallst_ai()
    parse_36kr()
    parse_sina_7x24()
    parse_ithome()
    parse_xinhua()
    parse_people()
    parse_thepaper()
    parse_yicai()

    print("\n" + "=" * 60)
    print("✅ ALL SOURCES PARSED")
    print("=" * 60)


if __name__ == '__main__':
    main()
