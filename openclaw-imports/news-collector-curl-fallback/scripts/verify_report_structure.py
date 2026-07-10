#!/usr/bin/env python3
"""
Verify a daily news report markdown file for structural completeness.

USAGE:
    python3 scripts/verify_report_structure.py [path/to/daily_news.md]

If no path given, defaults to /root/.hermes/hermes-agent/daily_news.md.

Checks:
    1. File exists and is non-empty
    2. Starts with the expected title heading (# 📰 YYYY年M月D日 新闻日报)
    3. Contains an opening quote block (markdown > blockquote with attribution)
    4. Contains all 5 required section headings (🤖/🌍/💰/📈/🏭)
    5. Contains ≥5 编者按 (editor's note) blocks
    6. Contains 今日观察 summary
    7. Contains 来源说明 attribution
    8. No unrendered template placeholders (${...}, YYYY)

Exit code 0 = all checks pass; 1 = one or more checks failed.
"""
import sys, os, re

def check_file(path):
    if not os.path.exists(path):
        print(f"FAIL: file not found at {path}")
        sys.exit(1)
    with open(path, 'r', errors='replace') as f:
        content = f.read()
    if not content.strip():
        print("FAIL: file is empty")
        sys.exit(1)
    return content

def has_quote_block(content):
    """
    A valid opening quote block is a markdown blockquote (lines starting with '>')
    that contains BOTH:
      - a quoted sentence (≥10 non-whitespace chars)
      - an attribution line (—— or a publication name like 《...》 / 人民日报 / 求是 / 锐评)
    Checks the first 15 lines (the header zone) so body '> 💡 编者按' blocks don't trip it.
    """
    header = '\n'.join(content.splitlines()[:15])
    quote_lines = [ln.strip() for ln in header.splitlines() if ln.strip().startswith('>')]
    if len(quote_lines) < 1:
        return False
    joined = '\n'.join(quote_lines)
    # Attribution signal: em-dash credit, 《》 publication, or known outlet keywords
    has_attribution = any(sig in joined for sig in
                          ['——', '《', '人民日报', '新华社', '央视', '求是', '锐评',
                           '评论员', '社论', '引自', '来源'])
    # Quoted content: at least one quote line with substantial non-marker text
    has_content = any(len(re.sub(r'[>《》\s—]', '', ln)) >= 10 for ln in quote_lines)
    return has_attribution and has_content

def run_checks(content):
    checks = [
        ('title heading',
         content.startswith('# 📰') and '新闻日报' in content[:50]),
        ('quote block',
         has_quote_block(content)),
        ('今日观察',
         '今日观察' in content),
        ('🤖 AI与科技 section',
         '## 🤖 AI与科技' in content),
        ('🌍 国际局势 section',
         '## 🌍 国际局势' in content),
        ('💰 宏观与政策 section',
         '## 💰 宏观与政策' in content),
        ('📈 资本市场 section',
         '## 📈 资本市场' in content),
        ('🏭 行业动态 section',
         '## 🏭 行业动态' in content),
        ('≥5 编者按 blocks',
         content.count('编者按') >= 5),
        ('来源说明 attribution',
         '来源说明' in content),
        ('no template placeholders',
         '${' not in content and 'YYYY' not in content),
    ]
    all_ok = True
    for name, ok in checks:
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_ok = False
        print(f"  {status}: {name}")
    return all_ok

def main():
    path = sys.argv[1] if len(sys.argv) > 1 else '/root/.hermes/hermes-agent/daily_news.md'
    print(f"Verifying: {path}")
    content = check_file(path)
    ok = run_checks(content)
    print(f"\nFile size: {len(content)} chars")
    if ok:
        print("✅ ALL CHECKS PASSED")
        sys.exit(0)
    else:
        print("❌ SOME CHECKS FAILED")
        sys.exit(1)

if __name__ == '__main__':
    main()
